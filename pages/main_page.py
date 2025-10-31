from __future__ import annotations
from typing import Optional
from selenium.common.exceptions import TimeoutException
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
    def go_to_constructor(self) -> "MainPage":
        self.scroll_to_top()
        self.click(L.CONSTRUCTOR_TAB)
        return self

    def go_to_feed(self) -> "MainPage":
        self.scroll_to_top()
        self.click(L.FEED_TAB)
        return self

    def click_logo(self) -> "MainPage":
        self.scroll_to_top()
        self.click(L.LOGO)
        return self

    # --- ингредиенты / модалка ---
    def open_ingredient_modal(self) -> None:
        self.click(L.FIRST_INGREDIENT_CARD)

    def is_modal_open(self) -> bool:
        try:
            self.wait_visible(L.INGREDIENT_MODAL)
            return True
        except TimeoutException:
            return False

    def close_ingredient_modal(self) -> None:
        self.close_overlays_if_any()

    # --- счётчик и добавление в заказ ---
    def get_ingredient_counter(self) -> int:
        els = self.finds(L.FIRST_INGREDIENT_COUNTER)
        if not els:
            return 0
        txt = (els[0].text or "").strip()
        try:
            return int(txt)
        except Exception:
            return 0

    def _click_first_card_add_button_or_modal(self) -> None:
        # 1) Пытаемся нажать «плюс» на самой карточке
        try:
            self.click(L.FIRST_INGREDIENT_ADD_BTN)
            return
        except Exception:
            pass

        # 2) Если «плюса» нет/не кликается — тащим карточку в конструктор
        try:
            self.drag_and_drop_js(L.FIRST_INGREDIENT_CARD, L.CONSTRUCTOR_AREA)
            return
        except Exception:
            pass

        # 3) Фолбэк: через модалку без жёсткого wait_visible на кнопке
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

  
    def add_ingredient_to_order(self) -> None:
        self.scroll_to_top()
        # 1) Булка
        self.click(L.BUNS_TAB)
        self._click_first_card_add_button_or_modal()
        # 2) Начинка (или соус) — чтобы кнопка точно стала активной
        try:
            self.click(L.FILLINGS_TAB)   # если вкладка «Начинки» доступна
        except Exception:
            self.click(L.SAUCES_TAB)     # фолбэк — «Соусы»
        self._click_first_card_add_button_or_modal()

    # --- вспомогательные для потоков с лентой ---
    def place_order_if_enabled(self) -> bool:
        """
        Пытается нажать «Оформить заказ».
        True — если реально нажали; False — если кнопка недоступна или её перекрывает что-то безуспешно.
        """
        # прибираем модалки/оверлеи перед кликом
        try:
            self.close_overlays_if_any()
            self.wait_gone(L.MODAL_OVERLAY)
        except Exception:
            pass

        # находим кнопку
        try:
            btn = self.wait_clickable(L.PLACE_ORDER_BTN)
        except Exception:
            return False

        # если это «Войти в аккаунт» — оформление недоступно без логина
        text = (btn.text or "").strip().lower()
        if "войти" in text:
            return False

        # пробуем обычный клик, если перекрыто — закрываем оверлей и кликаем JS
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
        
    def try_get_order_number_from_modal(self) -> Optional[str]:
        from selenium.webdriver.common.by import By
        from selenium.webdriver.support.ui import WebDriverWait
        from selenium.webdriver.support import expected_conditions as EC
        try:
            num_el = WebDriverWait(self._driver, 8).until(
                EC.visibility_of_element_located(
                    (By.XPATH, "//section[contains(@class,'Modal')]//*[contains(@class,'text_type_digits-large')]")
                )
            )
            num = num_el.text.strip()
            return num if num else None
        except Exception:
            return None