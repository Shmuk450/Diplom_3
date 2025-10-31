import allure
from pages.main_page import MainPage

@allure.feature("Навигация по сайту")
class TestNavigation:

    @allure.title("Переход по клику на 'Конструктор'")
    def test_go_to_constructor(self, driver, base_url):
        page = MainPage(driver).open(base_url)
        page.go_to_feed().go_to_constructor()
        assert "feed" not in driver.current_url.lower(), f"Остались в feed: {driver.current_url}"

    @allure.title("Переход по клику на 'Лента заказов'")
    def test_go_to_feed(self, driver, base_url):
        page = MainPage(driver).open(base_url)
        page.go_to_feed()
        assert "feed" in driver.current_url.lower(), f"Не открылся раздел 'Лента заказов': {driver.current_url}"

    @allure.title("Переход по клику на логотип Stellar Burgers — домой")
    def test_go_to_home_by_logo(self, driver, base_url):
        page = MainPage(driver).open(f"{base_url}feed")
        page.click_logo()
        assert base_url.rstrip('/') in driver.current_url.rstrip('/'), f"Не вернулись на главную: {driver.current_url}"