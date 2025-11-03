# helpers/feed_utils.py
from __future__ import annotations

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


@allure.step("Дождаться и проверить, что заказ №{order_number} появился в ленте")
def assert_order_appears(
    feed: OrderFeedPage,
    order_number: str,
    before_ready: set[str],
    before_inprog: set[str],
    timeout: int = 25,
) -> bool:
    """
    Инкапсулирует ожидание появления заказа в ленте.
    Возвращает True, если номер найден в 'В работе' или 'Готовы'.
    Никаких ассёртов внутри — финальная проверка остаётся в тесте.
    """
    # ждём появление через Page Object
    appeared = feed.order_appeared(
        order_number=order_number,
        before_ready=before_ready,
        before_inprog=before_inprog,
        timeout=timeout,
    )

    if not appeared:
        return False

    # финальная сверка после ожидания
    inprog_after = feed.get_in_progress_numbers()
    ready_after = feed.get_ready_numbers()
    return (order_number in inprog_after) or (order_number in ready_after)