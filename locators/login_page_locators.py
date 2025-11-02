# locators/login_page_locators.py
from selenium.webdriver.common.by import By

class LoginPageLocators:
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