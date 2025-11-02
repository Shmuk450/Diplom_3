# helpers/feed_utils.py
from __future__ import annotations

import re
import time
import random
from typing import List
from selenium.common.exceptions import TimeoutException

from locators.order_feed_locators import OrderFeedLocators as L
from pages.order_feed_page import OrderFeedPage

# --- устойчивость ожиданий ---
REFRESH_TRIES = 20       # увеличено для стабильности
WAIT_SHORT = 2.0
WAIT_LONG = 15.0


# --- хелперы для сравнения номеров (без '#', пробелов и ведущих нулей) ---
def digits(s: str) -> str:
    return re.sub(r"\D", "", s or "")


def same_num(a: str, b: str) -> bool:
    da, db = digits(a), digits(b)
    return da == db or da.endswith(db) or db.endswith(da)


def to_int(txt: str) -> int:
    """Безопасно достаём число (вырезаем всё, кроме цифр)."""
    return int(re.sub(r"\D", "", txt or "") or 0)


# ------ вспомогательное без прямого driver ------
def scroll_to_in_progress(feed: OrderFeedPage) -> None:
    """Прокрутка к «В работе» через PageObject и локаторы из L."""
    target = L.TOTAL_ALL_TIME if feed.is_visible(L.TOTAL_ALL_TIME) else L.HEADER_IN_PROGRESS
    feed.scroll_into_view(target)


def texts(feed: OrderFeedPage, locator) -> List[str]:
    """Тексты всех элементов по локатору без пустых строк."""
    return [(el.text or "").strip() for el in feed.finds(locator) if (el.text or "").strip()]


def inprogress_state(feed: OrderFeedPage) -> tuple[list[str], str]:
    """(номера заказов в 'В работе', текст секции <ul>)."""
    nums = texts(feed, L.IN_PROGRESS_NUMBERS)
    section = feed.finds(L.IN_PROGRESS_SECTION)
    txt = (section[0].text or "").strip() if section else ""
    return nums, txt


# --- функции ожидания изменений фида (через PageObject) ---
def _open_feed_with_buster(feed: OrderFeedPage, base_url: str) -> OrderFeedPage:
    """Открыть /feed с анти-кэшем (Chrome любит кэшировать)."""
    rnd = int(time.time() * 1000) % 100000 + random.randint(0, 999)
    feed.open(f"{base_url.rstrip('/')}/feed?rnd={rnd}")
    return feed.wait_loaded()


def wait_today_counter_growth(feed: OrderFeedPage, base_url: str, before_today: int) -> int:
    """
    Ожидает роста счётчика 'за сегодня'.
    Проверяет также рост 'всего' или изменение списков заказов как признак обновления фида.
    """
    max_seen = before_today

    # базовые значения
    _open_feed_with_buster(feed, base_url).scroll_to_counters()
    before_all = feed.total_all_time()
    before_inprog = texts(feed, L.IN_PROGRESS_NUMBERS)
    before_ready = texts(feed, L.ORDERS_READY)

    for _ in range(REFRESH_TRIES):
        _open_feed_with_buster(feed, base_url).scroll_to_counters()

        cur_today = feed.total_today()
        if cur_today > max_seen:
            return cur_today

        cur_all = feed.total_all_time()
        cur_inprog = texts(feed, L.IN_PROGRESS_NUMBERS)
        cur_ready = texts(feed, L.ORDERS_READY)

        updated = (
            cur_all > before_all
            or set(cur_inprog) != set(before_inprog)
            or set(cur_ready) != set(before_ready)
        )

        if updated:
            try:
                feed.wait_until(lambda: feed.total_today() > max_seen, timeout=WAIT_SHORT)
                return feed.total_today()
            except TimeoutException:
                continue

        # ждём малое обновление (вместо sleep)
        try:
            feed.wait_until(
                lambda: (
                    feed.total_today() > max_seen
                    or feed.total_all_time() > before_all
                    or set(texts(feed, L.IN_PROGRESS_NUMBERS)) != set(before_inprog)
                    or set(texts(feed, L.ORDERS_READY)) != set(before_ready)
                ),
                timeout=WAIT_SHORT,
            )
            new_today = feed.total_today()
            if new_today > max_seen:
                return new_today
        except TimeoutException:
            continue

    return max_seen


def wait_total_counter_growth(feed: OrderFeedPage, base_url: str, before_all: int) -> int:
    """Ожидает роста счётчика 'всего'."""
    for _ in range(REFRESH_TRIES):
        _open_feed_with_buster(feed, base_url).scroll_to_counters()
        cur = feed.total_all_time()
        if cur > before_all:
            return cur

        try:
            feed.wait_until(lambda: feed.total_all_time() > before_all, timeout=WAIT_SHORT)
            return feed.total_all_time()
        except TimeoutException:
            continue

    _open_feed_with_buster(feed, base_url)
    return feed.total_all_time()


def wait_order_appearance(
    feed: OrderFeedPage,
    base_url: str,
    order_number: str,
    before_inprog: list[str],
    before_ready: list[str],
) -> bool:
    """
    Ожидает появления номера заказа в 'В работе' или изменение/появление в 'Готовы'.
    Возвращает True, если заказ появился.
    """
    for _ in range(REFRESH_TRIES):
        _open_feed_with_buster(feed, base_url).scroll_to_counters()

        def appeared() -> bool:
            inprog, _ = inprogress_state(feed)
            ready = texts(feed, L.ORDERS_READY)
            if inprog:
                return any(same_num(x, order_number) for x in inprog) or (set(inprog) != set(before_inprog))
            return any(same_num(x, order_number) for x in ready) or (set(ready) != set(before_ready))

        try:
            feed.wait_until(appeared, timeout=WAIT_SHORT)
            return True
        except TimeoutException:
            continue

    return False