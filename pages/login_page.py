# pages/login_page.py
from __future__ import annotations
import allure

from pages.base_page import BasePage
from locators.login_page_locators import LoginPageLocators as L


class LoginPage(BasePage):

    @allure.step("Открыть страницу логина")
    def open_login(self, base_url: str) -> "LoginPage":
        self.open(base_url.rstrip("/") + "/login")
        self.wait_visible(L.LOGIN_HEADER)
        return self

    @allure.step("Заполнить логин/пароль и отправить форму (email={email})")
    def fill_credentials_and_submit(self, email: str, password: str) -> "LoginPage":
        self.type(L.EMAIL_INPUT, email)     # BasePage.type -> wait_visible + clear + send_keys
        self.type(L.PASS_INPUT, password)
        self.click(L.SUBMIT_BTN)            # BasePage.click -> safe_click с fallback JS-кликом
        return self

    @allure.step("Дождаться авторизации пользователя")
    def wait_logged_in(self) -> "LoginPage":
        self.wait_gone(L.SUBMIT_BTN)        # кнопка «Войти» исчезает
        self.wait_visible(L.ANY_MAIN_HEADER)
        # без assert в Page — тесты сами проверят состояние при необходимости
        return self

    @allure.step("Авторизоваться в приложении (email={email})")
    def login(self, base_url: str, email: str, password: str) -> "LoginPage":
        return (
            self.open_login(base_url)
                .fill_credentials_and_submit(email, password)
                .wait_logged_in()
        )