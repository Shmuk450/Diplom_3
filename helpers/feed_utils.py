# helpers/feed_utils.py
from __future__ import annotations

import re
import time
import random
from selenium.webdriver.common.by import By
from locators.order_feed_locators import OrderFeedLocators as L
from pages.order_feed_page import OrderFeedPage

# --- устойчивость ожиданий ---
REFRESH_TRIES = 20       # увеличено для стабильности в Chrome
WAIT_SHORT = 2.0
WAIT_LONG = 15


# --- хелперы для сравнения номеров (без '#', пробелов и ведущих нулей) ---
def digits(s: str) -> str:
    return re.sub(r"\D", "", s or "")


def same_num(a: str, b: str) -> bool:
    da, db = digits(a), digits(b)
    return da == db or da.endswith(db) or db.endswith(da)


def to_int(txt: str) -> int:
    """Безопасно достаём число (вырезаем всё, кроме цифр)."""
    return int(re.sub(r"\D", "", txt or "") or 0)


def scroll_to_in_progress(driver) -> None:
    """Прокрутка к заголовку 'В работе' без явных ожиданий."""
    try:
        h2 = driver.find_element(By.XPATH, "//h2[normalize-space()='В работе']")
        driver.execute_script("arguments[0].scrollIntoView({block:'center'});", h2)
    except Exception:
        pass


def texts(driver, locator) -> list[str]:
    els = driver.find_elements(*locator)
    return [e.text.strip() for e in els if (e.text or "").strip()]


def inprogress_state(driver) -> tuple[list[str], str]:
    """Возвращает (номера в li под 'В работе', полный текст самого <ul>) без WebDriverWait."""
    nums = texts(driver, L.IN_PROGRESS_NUMBERS)
    txt = ""
    try:
        txt = driver.find_element(*L.IN_PROGRESS_SECTION).text.strip()
    except Exception:
        pass
    return nums, txt


# --- функции ожидания изменений фида ---

def wait_today_counter_growth(driver, base_url: str, before_today: int) -> int:
    """
    Ожидает роста счётчика 'за сегодня'.
    Проверяет также рост 'всего' или изменение списков заказов как признак обновления фида.
    """
    from locators.order_feed_locators import OrderFeedLocators as L

    max_seen = before_today
    time.sleep(2.0)  # небольшая пауза после оформления заказа

    # базовые значения
    feed = OrderFeedPage(driver).open_feed(base_url).wait_loaded()
    feed.scroll_to_counters()
    before_all = feed.total_all_time()

    before_inprog = texts(driver, L.IN_PROGRESS_NUMBERS)
    before_ready = texts(driver, L.ORDERS_READY)

    for _ in range(REFRESH_TRIES):
        # анти-кэш для Chrome
        url = f"{base_url}feed?rnd={int(time.time()*1000)%100000 + random.randint(0,999)}"
        driver.get(url)
        feed = OrderFeedPage(driver).wait_loaded()
        feed.scroll_to_counters()

        cur_today = feed.total_today()
        if cur_today > max_seen:
            return cur_today

        cur_all = feed.total_all_time()
        cur_inprog = texts(driver, L.IN_PROGRESS_NUMBERS)
        cur_ready = texts(driver, L.ORDERS_READY)

        # любой признак обновления
        if (
            cur_all > before_all
            or set(cur_inprog) != set(before_inprog)
            or set(cur_ready) != set(before_ready)
        ):
            time.sleep(1.0)
            feed = OrderFeedPage(driver).open_feed(base_url).wait_loaded()
            feed.scroll_to_counters()
            cur_today = feed.total_today()
            if cur_today > max_seen:
                return cur_today

        time.sleep(WAIT_SHORT)

    return max_seen


def wait_total_counter_growth(driver, base_url: str, before_all: int) -> int:
    """Ожидает роста счётчика 'всего'."""
    for _ in range(REFRESH_TRIES):
        feed = OrderFeedPage(driver).open_feed(base_url).wait_loaded()
        feed.scroll_to_counters()
        cur = feed.total_all_time()
        if cur > before_all:
            return cur
        time.sleep(WAIT_SHORT)
    # если не вырос — вернём последнее
    feed = OrderFeedPage(driver).open_feed(base_url).wait_loaded()
    return feed.total_all_time()


def wait_order_appearance(driver, base_url: str, order_number: str,
                          before_inprog: list[str], before_ready: list[str]) -> bool:
    """
    Ожидает появления номера заказа в 'В работе' или изменение/появление в 'Готовы'.
    Возвращает True, если заказ появился.
    """
    for _ in range(REFRESH_TRIES):
        feed = OrderFeedPage(driver).open_feed(base_url).wait_loaded()
        feed.scroll_to_counters()

        inprog, _ = inprogress_state(driver)
        ready = texts(driver, L.ORDERS_READY)

        if inprog:
            if any(same_num(x, order_number) for x in inprog) or (set(inprog) != set(before_inprog)):
                return True
        else:
            if any(same_num(x, order_number) for x in ready) or (set(ready) != set(before_ready)):
                return True

        time.sleep(WAIT_SHORT)
    return False