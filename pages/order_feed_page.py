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

    # ---------- Вспомогательные методы ----------

    def _get_texts_set(self, locator) -> set[str]:
        """Возвращает множество текстов элементов по локатору (без пустых строк)."""
        return {
            (el.text or "").strip()
            for el in self.finds(locator)
            if (el.text or "").strip()
        }

    # ---------- Основные действия ----------

    @allure.step("Открыть ленту заказов")
    def open_feed(self, base_url: str) -> OrderFeedPage:
        """Открывает страницу /feed, даже если base_url без завершающего /."""
        self.open(base_url.rstrip("/") + "/feed")
        return self

    @allure.step("Дождаться загрузки ленты заказов")
    def wait_loaded(self) -> OrderFeedPage:
        """Ждёт появления хотя бы одного ключевого элемента ленты."""
        self.wait_any_visible(
            L.HEADER_IN_PROGRESS,
            L.TOTAL_ALL_TIME,
            L.TOTAL_TODAY,
        )
        return self

    @allure.step("Прокрутить к счётчикам заказов")
    def scroll_to_counters(self) -> OrderFeedPage:
        """Прокручивает страницу к счётчикам заказов."""
        target = L.TOTAL_ALL_TIME if self.is_visible(L.TOTAL_ALL_TIME) else L.HEADER_IN_PROGRESS
        self.scroll_into_view(target)
        return self

    # ---------- Методы для данных ----------

    @allure.step("Получить общее количество заказов за всё время")
    def total_all_time(self) -> int:
        el = self.wait_visible(L.TOTAL_ALL_TIME)
        return _to_int_safe(el.text)

    @allure.step("Получить количество заказов за сегодня")
    def total_today(self) -> int:
        el = self.wait_visible(L.TOTAL_TODAY)
        return _to_int_safe(el.text)

    @allure.step("Проверить, есть ли заказ №{order_number} в списке 'В работе'")
    def has_order_in_progress(self, order_number: str) -> bool:
        """Проверяет наличие конкретного номера заказа в разделе 'В работе'."""
        return order_number.strip() in self._get_texts_set(L.IN_PROGRESS_NUMBERS)

    @allure.step("Получить номера заказов в 'В работе'")
    def get_in_progress_numbers(self) -> set[str]:
        """Возвращает множество номеров заказов из раздела 'В работе'."""
        return self._get_texts_set(L.IN_PROGRESS_NUMBERS)

    @allure.step("Получить номера заказов в 'Готовы'")
    def get_ready_numbers(self) -> set[str]:
        """Возвращает множество номеров заказов из раздела 'Готовы'."""
        return self._get_texts_set(L.ORDERS_READY)

    # ---------- Проверки и ожидания ----------

    @allure.step("Проверить, что 'Выполнено за сегодня' увеличилось (было: {before})")
    def today_counter_increased(self, before: int, timeout: int = 20) -> bool:
        """Ждёт и возвращает True, если счётчик 'за сегодня' вырос."""
        self.scroll_to_counters()
        self.wait_until(
            lambda: self.total_today() > before,
            timeout=timeout,
            message=f"'Выполнено за сегодня' не выросло за {timeout} c (было {before})",
        )
        return self.total_today() > before

    @allure.step("Проверить, что 'Выполнено за всё время' увеличилось (было: {before})")
    def total_counter_increased(self, before: int, timeout: int = 20) -> bool:
        """Ждёт и возвращает True, если счётчик 'за всё время' вырос."""
        self.scroll_to_counters()
        self.wait_until(
            lambda: self.total_all_time() > before,
            timeout=timeout,
            message=f"'Выполнено за всё время' не выросло за {timeout} c (было {before})",
        )
        return self.total_all_time() > before

    @allure.step("Дождаться появления заказа №{order_number} в 'В работе' или 'Готовы'")
    def order_appeared(
        self,
        order_number: str,
        before_ready: list[str] | set[str],
        before_inprog: list[str] | set[str],
        timeout: int = 25,
    ) -> bool:
        """Ждёт появления нового заказа в одном из списков и возвращает True, если найден."""
        prev_ready = set(before_ready)
        prev_inprog = set(before_inprog)

        def _appears() -> bool:
            if self.has_order_in_progress(order_number):
                return True
            ready_now = self.get_ready_numbers()
            if order_number in ready_now:
                return True
            inprog_now = self.get_in_progress_numbers()
            return ready_now != prev_ready or inprog_now != prev_inprog

        self.wait_until(
            _appears,
            timeout=timeout,
            message=f"Номер заказа {order_number} не появился ни в 'В работе', ни в 'Готовы' за {timeout} c",
        )

        # финальная проверка — действительно ли заказ появился
        now_ready = self.get_ready_numbers()
        now_inprog = self.get_in_progress_numbers()
        return (order_number in now_ready) or (order_number in now_inprog)