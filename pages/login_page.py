# pages/login_page.py
from __future__ import annotations
import allure
from selenium.webdriver.common.by import By
from pages.base_page import BasePage


class LoginLocators:
    LOGIN_HEADER = (By.XPATH, "//h2[normalize-space()='Вход']")
    EMAIL_INPUT = (
        By.XPATH,
        "//label[contains(normalize-space(),'Email')]/following-sibling::input"
        " | //input[@type='email' or @name='email']"
    )
    PASS_INPUT = (
        By.XPATH,
        "//label[contains(normalize-space(),'Пароль')]/following-sibling::input"
        " | //input[@type='password']"
    )
    SUBMIT_BTN = (
        By.XPATH,
        "//button[normalize-space()='Войти' or .//p[normalize-space()='Войти']]"
    )
    ANY_MAIN_HEADER = (By.XPATH, "//main")


class LoginPage(BasePage):

    @allure.step("Открыть страницу логина")
    def open_login(self, base_url: str) -> "LoginPage":
        self.open(f"{base_url}login")
        self.wait_visible(LoginLocators.LOGIN_HEADER)
        return self

    @allure.step("Заполнить логин/пароль и отправить форму (email={email})")
    def fill_credentials_and_submit(self, email: str, password: str) -> "LoginPage":
        email_el = self.wait_visible(LoginLocators.EMAIL_INPUT)
        email_el.clear()
        email_el.send_keys(email)

        pass_el = self.wait_visible(LoginLocators.PASS_INPUT)
        pass_el.clear()
        pass_el.send_keys(password)

        try:
            self.wait_clickable(LoginLocators.SUBMIT_BTN).click()
        except Exception:
            # запасной JS-клик, если кнопку перекрыл слой
            btn = self.find(LoginLocators.SUBMIT_BTN)
            self.js_click(btn)
        return self

    @allure.step("Дождаться авторизации пользователя")
    def wait_logged_in(self, base_url: str) -> "LoginPage":
        """
        Ждём, пока кнопка 'Войти' исчезнет, а основная страница загрузится.
        """
        # проверяем исчезновение кнопки и наличие основного контента
        self.wait_gone(LoginLocators.SUBMIT_BTN)
        self.wait_visible(LoginLocators.ANY_MAIN_HEADER)
        # опционально: убедимся, что URL изменился
        assert not self.current_url.endswith("login"), "URL не изменился — авторизация не выполнена"
        return self

    @allure.step("Авторизоваться в приложении (email={email})")
    def login(self, base_url: str, email: str, password: str) -> "LoginPage":
        return (
            self.open_login(base_url)
                .fill_credentials_and_submit(email, password)
                .wait_logged_in(base_url)
        )