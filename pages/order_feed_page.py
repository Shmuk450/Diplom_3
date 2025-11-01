from __future__ import annotations
import re
import allure
from pages.base_page import BasePage
from locators.order_feed_locators import OrderFeedLocators as L


def _to_int_safe(txt: str) -> int:
    return int(re.sub(r"\D", "", txt or "") or 0)


class OrderFeedPage(BasePage):

    @allure.step("Открыть ленту заказов")
    def open_feed(self, base_url: str) -> "OrderFeedPage":
        self.open(f"{base_url}feed")
        return self

    @allure.step("Дождаться загрузки ленты заказов")
    def wait_loaded(self) -> "OrderFeedPage":
        # ждём любую опорную штуку ленты (через встроенные методы BasePage)
        try:
            self.wait_visible(L.HEADER_IN_PROGRESS)
        except Exception:
            try:
                self.wait_visible(L.TOTAL_ALL_TIME)
            except Exception:
                self.wait_visible(L.TOTAL_TODAY)
        return self

    @allure.step("Прокрутить к счётчикам заказов")
    def scroll_to_counters(self) -> "OrderFeedPage":
        # прокручиваем к одному из заголовков, чтобы ленивый рендер дорисовал цифры
        try:
            el = self.wait_visible(L.TOTAL_ALL_TIME)
        except Exception:
            el = self.wait_visible(L.HEADER_IN_PROGRESS)
        self.scroll_into_view(el)
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