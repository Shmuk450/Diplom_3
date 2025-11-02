# pages/order_feed_page.py
from __future__ import annotations

import re
import allure

from pages.base_page import BasePage
from locators.order_feed_locators import OrderFeedLocators as L


def _to_int_safe(txt: str) -> int:
    """Достаёт число из строки (любой мусор отбрасывается)."""
    return int(re.sub(r"\D", "", txt or "") or 0)


class OrderFeedPage(BasePage):
    """Страница 'Лента заказов'."""

    @allure.step("Открыть ленту заказов")
    def open_feed(self, base_url: str) -> "OrderFeedPage":
        # на случай если base_url без завершающего '/'
        self.open(base_url.rstrip("/") + "/feed")
        return self

    @allure.step("Дождаться загрузки ленты заказов")
    def wait_loaded(self) -> "OrderFeedPage":
        # ждём, пока станет видим хотя бы один из «опорных» блоков ленты
        self.wait_any_visible(
            L.HEADER_IN_PROGRESS,
            L.TOTAL_ALL_TIME,
            L.TOTAL_TODAY,
        )
        return self

    @allure.step("Прокрутить к счётчикам заказов")
    def scroll_to_counters(self) -> "OrderFeedPage":
        # если виден блок с общим числом — скроллим к нему, иначе к «В работе»
        target = L.TOTAL_ALL_TIME if self.is_visible(L.TOTAL_ALL_TIME) else L.HEADER_IN_PROGRESS
        self.scroll_into_view(target)  # передаём ЛОКАТОР (не элемент)
        return self

    @allure.step("Получить общее количество заказов за всё время")
    def total_all_time(self) -> int:
        el = self.wait_visible(L.TOTAL_ALL_TIME)
        return _to_int_safe(el.text)

    @allure.step("Получить количество заказов за сегодня")
    def total_today(self) -> int:
        el = self.wait_visible(L.TOTAL_TODAY)
        return _to_int_safe(el.text)

    @allure.step("Проверить, есть ли заказ #{order_number} в списке 'В работе'")
    def has_order_in_progress(self, order_number: str) -> bool:
        nums = [el.text.strip() for el in self.finds(L.IN_PROGRESS_NUMBERS)]
        return order_number.strip() in {n.strip() for n in nums}