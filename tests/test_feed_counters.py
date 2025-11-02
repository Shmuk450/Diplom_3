import allure
import pytest

from pages.main_page import MainPage
from pages.order_feed_page import OrderFeedPage
from locators.order_feed_locators import OrderFeedLocators as L
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

        # 3) ждём рост счётчика (через Page Object)
        feed.open_feed(BASE_URL).wait_loaded().scroll_to_counters()
        feed.wait_until(
            lambda: feed.total_today() > before_today,
            timeout=20,
            message=f"'Выполнено за сегодня' не вырос за 20 c (было {before_today})",
        )
        after_today = feed.total_today()
        assert after_today > before_today, f"'За сегодня' не вырос: было {before_today}, стало {after_today}"

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

        feed.open_feed(BASE_URL).wait_loaded().scroll_to_counters()
        feed.wait_until(
            lambda: feed.total_all_time() > before_all,
            timeout=20,
            message=f"'Выполнено за всё время' не вырос за 20 c (было {before_all})",
        )
        after_all = feed.total_all_time()
        assert after_all > before_all, f"'За всё время' не вырос: было {before_all}, стало {after_all}"

    @allure.title("После оформления номер появляется в ленте (в 'В работе' или в 'Готовы')")
    def test_new_order_appears_in_work_list(self, driver):
        feed = OrderFeedPage(driver).open_feed(BASE_URL).wait_loaded()

        # снимем 'до'
        before_inprog = {el.text.strip() for el in feed.finds(L.IN_PROGRESS_NUMBERS)}
        before_ready = {el.text.strip() for el in feed.finds(L.ORDERS_READY)}

        # оформляем заказ
        main = MainPage(driver).open(BASE_URL)
        main.add_ingredient_to_order()
        assert main.place_order_if_enabled(), "Кнопка 'Оформить заказ' недоступна/не нажалась"
        order_number = (main.try_get_order_number_from_modal() or "").strip()
        assert order_number, "Не получили номер из модалки — заказ мог не создаться"
        main.close_ingredient_modal()

        # ждём появления номера (или в 'В работе', или сразу в 'Готовы')
        feed.open_feed(BASE_URL).wait_loaded()

        def appears() -> bool:
            if feed.has_order_in_progress(order_number):
                return True
            ready_now = {el.text.strip() for el in feed.finds(L.ORDERS_READY)}
            return (order_number in ready_now) and (ready_now != before_ready or before_inprog)

        feed.wait_until(
            appears,
            timeout=25,
            message=f"Номер заказа {order_number} не появился ни в 'В работе', ни в 'Готовы' за 25 c",
        )