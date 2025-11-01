from __future__ import annotations
from typing import Optional
import allure
from selenium.webdriver.common.by import By
from selenium.common.exceptions import TimeoutException, ElementClickInterceptedException

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
        try:
            self.wait_visible(L.INGREDIENT_MODAL)
            return True
        except TimeoutException:
            return False

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
        try:
            return int(txt)
        except Exception:
            return 0

    @allure.step("Подождать, пока счётчик увеличится (было: {before})")
    def wait_counter_increases(self, before: int, timeout: int = 12) -> int:
        self.wait._timeout = timeout
        self.wait.until(lambda d: (new := self.get_ingredient_counter()) != before and new > before)
        return self.get_ingredient_counter()

    def _click_first_card_add_button_or_modal(self) -> None:
        # вспомогательный метод — степ не нужен
        try:
            self.click(L.FIRST_INGREDIENT_ADD_BTN)
            return
        except Exception:
            pass
        try:
            self.drag_and_drop_js(L.FIRST_INGREDIENT_CARD, L.CONSTRUCTOR_AREA)
            return
        except Exception:
            pass
        try:
            self.open_ingredient_modal()
            btns = self.finds(L.MODAL_ADD_BUTTON)
            if btns:
                self.js_click(btns[0])
        finally:
            try:
                self.close_overlays_if_any()
            except Exception:
                pass

    @allure.step("Добавить ингредиент в заказ")
    def add_ingredient_to_order(self) -> None:
        self.scroll_to_top()
        self.click(L.BUNS_TAB)
        self._click_first_card_add_button_or_modal()
        try:
            self.click(L.FILLINGS_TAB)
        except Exception:
            self.click(L.SAUCES_TAB)
        self._click_first_card_add_button_or_modal()

    # --- оформление заказа ---
    @allure.step("Попытаться оформить заказ, если кнопка активна")
    def place_order_if_enabled(self) -> bool:
        """
        True — если реально нажали; False — если кнопка недоступна.
        """
        try:
            self.close_overlays_if_any()
            self.wait_gone(L.MODAL_OVERLAY)
        except Exception:
            pass

        try:
            btn = self.wait_clickable(L.PLACE_ORDER_BTN)
        except Exception:
            return False

        text = (btn.text or "").strip().lower()
        if "войти" in text:
            return False

        try:
            btn.click()
            return True
        except ElementClickInterceptedException:
            try:
                self.close_overlays_if_any()
                self.wait_gone(L.MODAL_OVERLAY)
                self.js_click(btn)
                return True
            except Exception:
                return False
        except Exception:
            return False

    @allure.step("Попытаться получить номер заказа из модалки")
    def try_get_order_number_from_modal(self) -> Optional[str]:
        try:
            el = self.wait_visible(L.MODAL_ORDER_NUMBER)
            num = (el.text or "").strip()
            return num if num else None
        except Exception:
            return None