from __future__ import annotations
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
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
    SUBMIT_BTN = (By.XPATH, "//button[normalize-space()='Войти' or .//p[normalize-space()='Войти']]")
    ANY_MAIN_HEADER = (By.XPATH, "//main")

class LoginPage(BasePage):
    def open_login(self, base_url: str) -> "LoginPage":
        self.open(f"{base_url}login")   # если у тебя метод называется иначе (open_url) — замени
        WebDriverWait(self._driver, 10).until(
            EC.visibility_of_element_located(LoginLocators.LOGIN_HEADER)
        )
        return self

    def fill_credentials_and_submit(self, email: str, password: str) -> "LoginPage":
        email_el = self.wait_visible(LoginLocators.EMAIL_INPUT)
        email_el.clear(); email_el.send_keys(email)
        pass_el = self.wait_visible(LoginLocators.PASS_INPUT)
        pass_el.clear(); pass_el.send_keys(password)
        try:
            self.wait_clickable(LoginLocators.SUBMIT_BTN).click()
        except Exception:
            btn = self.find(LoginLocators.SUBMIT_BTN)
            self.js_click(btn)
        return self

    def wait_logged_in(self, base_url: str) -> "LoginPage":
        WebDriverWait(self._driver, 12).until(
            EC.any_of(
                EC.url_changes(f"{base_url}login"),
                EC.invisibility_of_element_located(LoginLocators.SUBMIT_BTN),
            )
        )
        WebDriverWait(self._driver, 10).until(
            EC.presence_of_element_located(LoginLocators.ANY_MAIN_HEADER)
        )
        return self

    def login(self, base_url: str, email: str, password: str) -> "LoginPage":
        return self.open_login(base_url).fill_credentials_and_submit(email, password).wait_logged_in(base_url)