import allure
from pages.main_page import MainPage
from test_data.config import BASE_URL


@allure.feature("Навигация по сайту")
class TestNavigation:
    """Тесты навигации по вкладкам и логотипу Stellar Burgers."""

    @allure.title("Переход по клику на 'Конструктор'")
    def test_go_to_constructor(self, driver):
        page = MainPage(driver).open(BASE_URL)
        page.go_to_feed().go_to_constructor()
        assert "feed" not in page.current_url.lower(), (
            f"Остались в разделе 'Лента заказов': {page.current_url}"
        )

    @allure.title("Переход по клику на 'Лента заказов'")
    def test_go_to_feed(self, driver):
        page = MainPage(driver).open(BASE_URL)
        page.go_to_feed()
        assert "feed" in page.current_url.lower(), (
            f"Не открылся раздел 'Лента заказов': {page.current_url}"
        )

    @allure.title("Переход по клику на логотип Stellar Burgers — домой")
    def test_go_to_home_by_logo(self, driver):
        page = MainPage(driver).open(f"{BASE_URL}feed")
        page.click_logo()
        assert BASE_URL.rstrip("/") in page.current_url.rstrip("/"), (
            f"Не вернулись на главную страницу: {page.current_url}"
        )