# pages/main_page.py
from __future__ import annotations
from typing import Optional

import allure
from selenium.common.exceptions import ElementClickInterceptedException

from pages.base_page import BasePage
from locators.main_page_locators import MainPageLocators as L


class MainPage(BasePage):

    # --- hook: закрытие перекрывающих оверлеев (модалка ингредиента) ---
    def close_overlays_if_any(self) -> None:
        if self.is_present(L.MODAL_OVERLAY):
            btns = self.finds(L.INGREDIENT_MODAL_CLOSE)
            if btns:
                self.js_click(btns[0])
            self.wait_gone(L.INGREDIENT_MODAL)

    # --- навигация ---
    @allure.step("Перейти на вкладку 'Конструктор'")
    def go_to_constructor(self) -> "MainPage":
        self.scroll_to_top()
        self.click(L.CONSTRUCTOR_TAB)
        return self

    @allure.step("Перейти на вкладку 'Лента заказов'")
    def go_to_feed(self) -> "MainPage":
        self.scroll_to_top()
        self.click(L.FEED_TAB)
        return self

    @allure.step("Клик по логотипу для перехода на главную")
    def click_logo(self) -> "MainPage":
        self.scroll_to_top()
        self.click(L.LOGO)
        return self

    # --- ингредиенты / модалка ---
    @allure.step("Открыть модалку ингредиента")
    def open_ingredient_modal(self) -> None:
        self.click(L.FIRST_INGREDIENT_CARD)

    @allure.step("Проверить, открыта ли модалка ингредиента")
    def is_modal_open(self) -> bool:
        return self.is_visible(L.INGREDIENT_MODAL)

    @allure.step("Закрыть модалку ингредиента")
    def close_ingredient_modal(self) -> None:
        self.close_overlays_if_any()

    # --- счётчик и добавление в заказ ---
    @allure.step("Получить текущее значение счётчика ингредиента")
    def get_ingredient_counter(self) -> int:
        els = self.finds(L.FIRST_INGREDIENT_COUNTER)
        if not els:
            return 0
        txt = (els[0].text or "").strip()
        return int(txt) if txt.isdigit() else 0

    @allure.step("Подождать, пока счётчик увеличится (было: {before})")
    def wait_counter_increases(self, before: int, timeout: int = 12) -> int:
        # используем инкапсулированное ожидание из BasePage
        self.wait_until(lambda: self.get_ingredient_counter() > before, timeout=timeout)
        return self.get_ingredient_counter()

    def _click_first_card_add_button_or_modal(self) -> None:
        """Вспомогательный метод добавления ингредиента: кнопкой, DnD или через модалку."""
        if self.is_present(L.FIRST_INGREDIENT_ADD_BTN):
            self.click(L.FIRST_INGREDIENT_ADD_BTN)
            return

        if self.is_present(L.FIRST_INGREDIENT_CARD) and self.is_present(L.CONSTRUCTOR_AREA):
            self.drag_and_drop_js(L.FIRST_INGREDIENT_CARD, L.CONSTRUCTOR_AREA)
            return

        # запасной путь — через модалку ингредиента
        self.open_ingredient_modal()
        btns = self.finds(L.MODAL_ADD_BUTTON)
        if btns:
            self.js_click(btns[0])
        self.close_overlays_if_any()

    @allure.step("Добавить ингредиент в заказ")
    def add_ingredient_to_order(self) -> None:
        self.scroll_to_top()
        self.click(L.BUNS_TAB)
        self._click_first_card_add_button_or_modal()

        # если вкладка "Начинки" недоступна — пробуем "Соусы"
        if self.is_visible(L.FILLINGS_TAB):
            self.click(L.FILLINGS_TAB)
        elif self.is_visible(L.SAUCES_TAB):
            self.click(L.SAUCES_TAB)

        self._click_first_card_add_button_or_modal()

    # --- оформление заказа ---
    @allure.step("Попытаться оформить заказ, если кнопка активна")
    def place_order_if_enabled(self) -> bool:
        self.close_overlays_if_any()
        self.wait_gone(L.MODAL_OVERLAY)

        btn = self.wait_clickable(L.PLACE_ORDER_BTN)
        text = (btn.text or "").strip().lower()

        if "войти" in text:
            return False

        try:
            btn.click()
            return True
        except ElementClickInterceptedException:
            self.close_overlays_if_any()
            self.wait_gone(L.MODAL_OVERLAY)
            self.js_click(btn)
            return True

    @allure.step("Попытаться получить номер заказа из модалки")
    def try_get_order_number_from_modal(self) -> Optional[str]:
        if not self.is_visible(L.MODAL_ORDER_NUMBER):
            return None
        num = (self.find(L.MODAL_ORDER_NUMBER).text or "").strip()
        return num or None