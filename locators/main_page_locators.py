from selenium.webdriver.common.by import By

class MainPageLocators:
    # Навигация
    CONSTRUCTOR_TAB = (
        By.XPATH,
        "//a[@href='/' or contains(@href,'constructor')]//p[normalize-space()='Конструктор']"
        " | //p[normalize-space()='Конструктор']/parent::*"
    )
    FEED_TAB = (
        By.XPATH,
        "//a[@href='/feed'] | //p[normalize-space()='Лента заказов' or normalize-space()='Лента Заказов']/parent::*"
    )
    LOGO = (By.XPATH, "//a[contains(@class,'AppHeader_header__logo') or @href='/']")

    # Вкладки ингредиентов
    BUNS_TAB     = (By.XPATH, "//span[normalize-space()='Булки']/parent::div")
    SAUCES_TAB   = (By.XPATH, "//span[normalize-space()='Соусы']/parent::div")
    FILLINGS_TAB = (By.XPATH, "//span[normalize-space()='Начинки']/parent::div")
    ACTIVE_TAB   = (By.XPATH, "//div[contains(@class,'tab_tab_type_current')]")

    # Карточки ингредиентов (первая карточка)
    FIRST_INGREDIENT_CARD    = (By.XPATH, "(//a[contains(@href,'/ingredient')])[1]")
    FIRST_INGREDIENT_ADD_BTN = (By.XPATH, "(//a[contains(@href,'/ingredient')])[1]//button")
    FIRST_INGREDIENT_COUNTER = (
        By.XPATH,
        "(//a[contains(@href,'/ingredient')])[1]"
        "//*[contains(@class,'counter_counter__num') or contains(@class,'text_type_digits-default')]"
    )

    # Модалка ингредиента
    INGREDIENT_MODAL       = (By.XPATH, "//section[contains(@class,'Modal') and .//h2]")
    INGREDIENT_MODAL_CLOSE = (By.XPATH, "//section[contains(@class,'Modal')]//button[contains(@class,'close') or @aria-label='Закрыть']")
    MODAL_OVERLAY          = (By.XPATH, "//div[contains(@class,'Modal_modal_overlay')]")
    MODAL_ADD_BUTTON       = (By.XPATH, "//section[contains(@class,'Modal')]//button[contains(normalize-space(.),'Добавить')]")

    # Конструктор/оформление
    CONSTRUCTOR_AREA = (By.XPATH, "//section[contains(@class,'BurgerConstructor')]")
    PLACE_ORDER_BTN  = (By.XPATH, "//button[contains(@class,'button') and contains(normalize-space(.),'Оформить')]")