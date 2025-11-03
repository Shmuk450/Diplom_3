# helpers/feed_utils.py
import allure
from pages.order_feed_page import OrderFeedPage


@allure.step("Получить номера заказов в разделе 'В работе'")
def get_in_progress_numbers(feed: OrderFeedPage) -> set[str]:
    """Возвращает множество номеров заказов, находящихся 'В работе'."""
    return feed.get_in_progress_numbers()


@allure.step("Получить номера заказов в разделе 'Готовы'")
def get_ready_numbers(feed: OrderFeedPage) -> set[str]:
    """Возвращает множество номеров заказов, находящихся 'Готовы'."""
    return feed.get_ready_numbers()


@allure.step("Проверить, что заказ №{order_number} появился в ленте")
def assert_order_appears(
    feed: OrderFeedPage,
    order_number: str,
    before_ready: set[str],
    before_inprog: set[str],
    timeout: int = 25,
) -> bool:
    """
    Ждёт появления номера в ленте заказов и выполняет финальную проверку.
    Используется в тестах вместо прямой логики ожидания.
    """
    # Ждём появления через новый метод страницы
    appeared = feed.order_appeared(
        order_number=order_number,
        before_ready=before_ready,
        before_inprog=before_inprog,
        timeout=timeout,
    )

    # После ожидания выполняем явную финальную проверку
    inprog_after = feed.get_in_progress_numbers()
    ready_after = feed.get_ready_numbers()

    assert appeared and (
        order_number in inprog_after or order_number in ready_after
    ), f"Номер заказа {order_number} не найден в ленте после ожидания"

    return True