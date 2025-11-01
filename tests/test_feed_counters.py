from __future__ import annotations

import pytest
import allure

from pages.main_page import MainPage
from pages.order_feed_page import OrderFeedPage
from locators.order_feed_locators import OrderFeedLocators as L  
from test_data.config import BASE_URL

# импортируем хелперы и константы (циклы реализованы в хелперах)
from helpers.feed_utils import (
    REFRESH_TRIES, WAIT_SHORT, WAIT_LONG,  
    digits as _digits,
    same_num as _same_num,
    texts as _texts,
    inprogress_state as _inprogress_state,
    wait_today_counter_growth,
    wait_total_counter_growth,
    wait_order_appearance,
)

@allure.suite("Лента заказов — счётчики и появление номера (UI)")
@pytest.mark.usefixtures("auth_login")
class TestFeedCounters:
    """Все тесты оформляют заказ через UI, а затем проверяют ленту."""

    @allure.title("Рост 'Выполнено за сегодня' после оформления заказа (UI)")
    def test_today_orders_counter(self, driver):
        # 1) базовое значение
        feed = OrderFeedPage(driver).open_feed(BASE_URL).wait_loaded()
        feed.scroll_to_counters()
        before_today = feed.total_today()

        # 2) оформляем заказ
        main = MainPage(driver).open(BASE_URL)
        main.add_ingredient_to_order()
        assert main.place_order_if_enabled(), "Кнопка 'Оформить заказ' недоступна/не нажалась"
        assert main.try_get_order_number_from_modal(), "Не получили номер из модалки — заказ мог не создаться"
        main.close_ingredient_modal()

        # 3) ждём рост счётчика — без циклов в тесте
        after_today = wait_today_counter_growth(driver, BASE_URL, before_today)
        assert after_today > before_today, (
            f"Счётчик 'за сегодня' не вырос (было {before_today}, максимум наблюдали {after_today})"
        )

    @allure.title("Рост 'Выполнено за всё время' после оформления заказа (UI)")
    def test_total_orders_counter(self, driver):
        feed = OrderFeedPage(driver).open_feed(BASE_URL).wait_loaded()
        before_all = feed.total_all_time()

        main = MainPage(driver).open(BASE_URL)
        main.add_ingredient_to_order()
        assert main.place_order_if_enabled(), "Кнопка 'Оформить заказ' недоступна/не нажалась"
        assert main.try_get_order_number_from_modal(), "Не получили номер из модалки — заказ мог не создаться"
        main.close_ingredient_modal()

        after_all = wait_total_counter_growth(driver, BASE_URL, before_all)
        assert after_all > before_all, (
            f"Счётчик 'всего' не увеличился (было {before_all}, стало {after_all})"
        )

    @allure.title("После оформления номер появляется в ленте (в 'В работе' или сразу в 'Готовы')")
    def test_new_order_appears_in_work_list(self, driver):
        # снимем «до»
        feed = OrderFeedPage(driver).open_feed(BASE_URL).wait_loaded()
        before_inprog, before_inprog_text = _inprogress_state(driver)
        before_ready = _texts(driver, L.ORDERS_READY)
        allure.attach("\n".join(before_inprog) or "<пусто>", "До: 'В работе' (li)", allure.attachment_type.TEXT)
        allure.attach(before_inprog_text or "<пусто>", "До: 'В работе' <ul>.text", allure.attachment_type.TEXT)
        allure.attach("\n".join(before_ready) or "<пусто>", "До: 'Готовы'", allure.attachment_type.TEXT)

        # оформляем заказ
        main = MainPage(driver).open(BASE_URL)
        main.add_ingredient_to_order()
        assert main.place_order_if_enabled(), "Кнопка 'Оформить заказ' недоступна/не нажалась"
        order_number = _digits(main.try_get_order_number_from_modal())
        assert order_number, "Не получили номер из модалки — заказ мог не создаться"
        main.close_ingredient_modal()

        # ждём появления номера — без циклов в тесте
        appeared = wait_order_appearance(
            driver=driver,
            base_url=BASE_URL,
            order_number=order_number,
            before_inprog=before_inprog,
            before_ready=before_ready,
        )
        assert appeared, "Новые заказы не появились ни в 'В работе', ни в 'Готовы'"