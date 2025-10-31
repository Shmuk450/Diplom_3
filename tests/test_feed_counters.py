# tests/test_feed_counters.py
from __future__ import annotations

import re
import time
import pytest
import allure

from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

from pages.main_page import MainPage
from pages.order_feed_page import OrderFeedPage
from locators.order_feed_locators import OrderFeedLocators as L


# --- устойчивость ожиданий ---
REFRESH_TRIES = 8
WAIT_SHORT = 2.0
WAIT_LONG = 12


def _to_int(txt: str) -> int:
    """Безопасно достаём число (вырезаем всё, кроме цифр)."""
    return int(re.sub(r"\D", "", txt or "") or 0)


def _scroll_to_in_progress(driver) -> None:
    """Прокрутка к заголовку 'В работе' (чтобы ленивый рендер отработал)."""
    try:
        h2 = WebDriverWait(driver, 8).until(
            EC.visibility_of_element_located((By.XPATH, "//h2[normalize-space()='В работе']"))
        )
        driver.execute_script("arguments[0].scrollIntoView({block:'center'});", h2)
    except Exception:
        pass


def _texts(driver, locator) -> list[str]:
    els = driver.find_elements(*locator)
    return [e.text.strip() for e in els if (e.text or "").strip()]


def _inprogress_state(driver) -> tuple[list[str], str]:
    """Возвращает (номера в li под 'В работе', полный текст самого <ul>)."""
    nums = _texts(driver, L.IN_PROGRESS_NUMBERS)
    txt = ""
    try:
        txt = WebDriverWait(driver, 5).until(
            EC.presence_of_element_located(L.IN_PROGRESS_SECTION)
        ).text.strip()
    except Exception:
        pass
    return nums, txt


@allure.suite("Лента заказов — счётчики и появление номера (UI)")
@pytest.mark.usefixtures("auth_login")
class TestFeedCounters:
    """Все тесты оформляют заказ через UI, а затем проверяют ленту."""

    @allure.title("Рост 'Выполнено за сегодня' после оформления заказа (UI)")
    def test_today_orders_counter(self, driver, base_url, auth_login):
        # 1) базовое значение
        feed = OrderFeedPage(driver).open_feed(base_url).wait_loaded()
        before_today = feed.total_today()

        # 2) оформляем заказ под логином
        main = MainPage(driver).open(base_url)
        main.add_ingredient_to_order()
        assert main.place_order_if_enabled(), "Кнопка 'Оформить заказ' недоступна/не нажалась"
        assert main.try_get_order_number_from_modal(), "Не получили номер из модалки — заказ мог не создаться"
        try:
            main.close_ingredient_modal()
        except Exception:
            pass

        # переход на /feed и ожидание загрузки
        feed = OrderFeedPage(driver).open_feed(base_url).wait_loaded()

        # 3) ждём роста счётчика
        inc = False
        for _ in range(REFRESH_TRIES):
            _scroll_to_in_progress(driver)
            try:
                WebDriverWait(driver, WAIT_LONG).until(
                    lambda d: _to_int(d.find_element(*L.TOTAL_TODAY).text) > before_today
                )
                inc = True
                break
            except Exception:
                try:
                    time.sleep(1.0)
                    if _to_int(driver.find_element(*L.TOTAL_TODAY).text) > before_today:
                        inc = True
                        break
                except Exception:
                    pass
            driver.refresh()
            feed.wait_loaded()
            time.sleep(WAIT_SHORT)

        after_today = feed.total_today()
        assert inc and after_today > before_today, f"Счётчик 'за сегодня' не изменился (было {before_today}, стало {after_today})"

    @allure.title("Рост 'Выполнено за всё время' после оформления заказа (UI)")
    def test_total_orders_counter(self, driver, base_url, auth_login):
        # 1) базовое значение
        feed = OrderFeedPage(driver).open_feed(base_url).wait_loaded()
        before_all = feed.total_all_time()

        # 2) оформляем заказ
        main = MainPage(driver).open(base_url)
        main.add_ingredient_to_order()
        assert main.place_order_if_enabled(), "Кнопка 'Оформить заказ' недоступна/не нажалась"
        assert main.try_get_order_number_from_modal(), "Не получили номер из модалки — заказ мог не создаться"
        try:
            main.close_ingredient_modal()
        except Exception:
            pass

        # переход на /feed и ожидание загрузки
        feed = OrderFeedPage(driver).open_feed(base_url).wait_loaded()

        # 3) ждём роста счётчика
        inc = False
        for _ in range(REFRESH_TRIES):
            _scroll_to_in_progress(driver)
            try:
                WebDriverWait(driver, WAIT_LONG).until(
                    lambda d: _to_int(d.find_element(*L.TOTAL_ALL_TIME).text) > before_all
                )
                inc = True
                break
            except Exception:
                driver.refresh()
                feed.wait_loaded()
                time.sleep(WAIT_SHORT)

        after_all = feed.total_all_time()
        assert inc and after_all > before_all, f"Счётчик 'всего' не увеличился (было {before_all}, стало {after_all})"

    @allure.title("После оформления номер появляется в ленте (в 'В работе' или сразу в 'Готовы')")
    def test_new_order_appears_in_work_list(self, driver, base_url, auth_login):
        # 0) снимем «до»
        feed = OrderFeedPage(driver).open_feed(base_url).wait_loaded()
        before_inprog, before_inprog_text = _inprogress_state(driver)
        before_ready = _texts(driver, L.ORDERS_READY)
        allure.attach("\n".join(before_inprog) or "<пусто>", "До: 'В работе' (li)", allure.attachment_type.TEXT)
        allure.attach(before_inprog_text or "<пусто>", "До: 'В работе' <ul>.text", allure.attachment_type.TEXT)
        allure.attach("\n".join(before_ready) or "<пусто>", "До: 'Готовы'", allure.attachment_type.TEXT)

        # 1) оформляем заказ
        main = MainPage(driver).open(base_url)
        main.add_ingredient_to_order()
        assert main.place_order_if_enabled(), "Кнопка 'Оформить заказ' недоступна/не нажалась"
        order_number = main.try_get_order_number_from_modal()
        assert order_number, "Не получили номер из модалки — заказ мог не создаться"
        try:
            main.close_ingredient_modal()
        except Exception:
            pass

        # 2) ждём появления изменений
        appeared = False
        for attempt in range(1, REFRESH_TRIES + 1):
            feed = OrderFeedPage(driver).open_feed(base_url).wait_loaded()
            _scroll_to_in_progress(driver)

            inprog, inprog_text = _inprogress_state(driver)
            ready = _texts(driver, L.ORDERS_READY)

            allure.attach("\n".join(inprog) or "<пусто>", f"[{attempt}] 'В работе' (li)", allure.attachment_type.TEXT)
            allure.attach(inprog_text or "<пусто>", f"[{attempt}] 'В работе' <ul>.text", allure.attachment_type.TEXT)
            allure.attach("\n".join(ready) or "<пусто>", f"[{attempt}] 'Готовы'", allure.attachment_type.TEXT)

            if inprog:
                if (order_number in inprog) or (set(inprog) != set(before_inprog)):
                    appeared = True
                    break
            else:
                if (order_number in ready) or (set(ready) != set(before_ready)):
                    appeared = True
                    break

            time.sleep(WAIT_SHORT)

        assert appeared, "Новые заказы не появились ни в 'В работе', ни в 'Готовы' (смотри вложения Allure)"