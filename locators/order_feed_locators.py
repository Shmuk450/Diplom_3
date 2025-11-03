from selenium.webdriver.common.by import By

class OrderFeedLocators:
    # Якоря секций
    HEADER_IN_PROGRESS = (By.XPATH, "//h2[normalize-space()='В работе']")
    HEADER_READY       = (By.XPATH, "//h2[normalize-space()='Готовы']")

    # Счётчики — привязка к надписи слева от числа
    TOTAL_ALL_TIME = (
        By.XPATH,
        "//p[contains(normalize-space(),'Выполнено за все время')]/following-sibling::p[contains(@class,'text_type_digits')][1]"
    )
    TOTAL_TODAY = (
        By.XPATH,
        "//p[contains(normalize-space(),'Выполнено за сегодня')]/following-sibling::p[contains(@class,'text_type_digits')][1]"
    )

    # «В работе»: либо <li> с номерами, либо текст «Все текущие заказы готовы!»
    IN_PROGRESS_SECTION = (
        By.XPATH,
        "//h2[normalize-space()='В работе']/following::ul[1]"
    )
    IN_PROGRESS_NUMBERS = (
        By.XPATH,
        "//h2[normalize-space()='В работе']/following::ul[1]/li"
    )

    # «Готовы»
    ORDERS_READY = (
        By.XPATH,
        "//h2[normalize-space()='Готовы']/following::ul[1]//li"
    )