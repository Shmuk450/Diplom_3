import allure
import pytest

from pages.main_page import MainPage
from pages.order_feed_page import OrderFeedPage
from helpers.feed_utils import (
    get_in_progress_numbers,
    get_ready_numbers,
    assert_order_appears,
)
from test_data.config import BASE_URL


@allure.suite("Лента заказов — счётчики и появление номера (UI)")
@pytest.mark.usefixtures("auth_login")
class TestFeedCounters:
    """Все тесты оформляют заказ через UI, а затем проверяют ленту."""

    @allure.title("Рост 'Выполнено за сегодня' после оформления заказа (UI)")
    def test_today_orders_counter(self, driver):
        # 1) базовое значение
        feed = (
            OrderFeedPage(driver)
            .open_feed(BASE_URL)
            .wait_loaded()
            .scroll_to_counters()
        )
        before_today = feed.total_today()

        # 2) оформляем заказ
        main = MainPage(driver).open(BASE_URL)
        main.add_ingredient_to_order()
        assert main.place_order_if_enabled(), "Кнопка 'Оформить заказ' недоступна/не нажалась"
        assert main.try_get_order_number_from_modal(), "Не получили номер из модалки — заказ мог не создаться"
        main.close_ingredient_modal()

        # 3) проверяем рост счётчика (ожидание инкапсулировано в Page)
        feed.open_feed(BASE_URL).wait_loaded()
        increased = feed.today_counter_increased(before_today, timeout=20)

        # финальная проверка
        assert increased, f"'За сегодня' не вырос (было {before_today}, стало {feed.total_today()})"

    @allure.title("Рост 'Выполнено за всё время' после оформления заказа (UI)")
    def test_total_orders_counter(self, driver):
        feed = (
            OrderFeedPage(driver)
            .open_feed(BASE_URL)
            .wait_loaded()
            .scroll_to_counters()
        )
        before_all = feed.total_all_time()

        main = MainPage(driver).open(BASE_URL)
        main.add_ingredient_to_order()
        assert main.place_order_if_enabled(), "Кнопка 'Оформить заказ' недоступна/не нажалась"
        assert main.try_get_order_number_from_modal(), "Не получили номер из модалки — заказ мог не создаться"
        main.close_ingredient_modal()

        feed.open_feed(BASE_URL).wait_loaded()
        increased = feed.total_counter_increased(before_all, timeout=20)

        # финальная проверка
        assert increased, f"'За всё время' не вырос (было {before_all}, стало {feed.total_all_time()})"

    @allure.title("После оформления номер появляется в ленте (в 'В работе' или в 'Готовы')")
    def test_new_order_appears_in_work_list(self, driver):
        # 1) открыли ленту и сняли 'до' через helpers (никаких циклов в тесте)
        feed = OrderFeedPage(driver).open_feed(BASE_URL).wait_loaded()
        before_inprog = get_in_progress_numbers(feed)
        before_ready = get_ready_numbers(feed)

        # 2) оформили заказ и получили номер
        main = MainPage(driver).open(BASE_URL)
        main.add_ingredient_to_order()
        assert main.place_order_if_enabled(), "Кнопка 'Оформить заказ' недоступна/не нажалась"
        order_number = (main.try_get_order_number_from_modal() or "").strip()
        assert order_number, "Не получили номер из модалки — заказ мог не создаться"
        main.close_ingredient_modal()

        # 3) ждём появления номера в ленте через helper (никаких внутренних def в тесте)
        feed.open_feed(BASE_URL).wait_loaded()
        appeared = assert_order_appears(
            feed=feed,
            order_number=order_number,
            before_ready=before_ready,
            before_inprog=before_inprog,
            timeout=25,
        )

        # финальная проверка
        assert appeared, f"Номер заказа {order_number} не найден в ленте после ожидания"