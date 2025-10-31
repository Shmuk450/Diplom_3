import allure
from pages.main_page import MainPage
from selenium.webdriver.support.ui import WebDriverWait

@allure.feature("Конструктор бургеров")
class TestConstructor:

    @allure.title("Если кликнуть на ингредиент — открывается модалка с деталями")
    def test_ingredient_modal_opens(self, driver, base_url):
        page = MainPage(driver).open(base_url)
        page.open_ingredient_modal()
        assert page.is_modal_open(), "Модалка не открылась"

    @allure.title("Модалка ингредиента закрывается по крестику")
    def test_ingredient_modal_closes(self, driver, base_url):
        page = MainPage(driver).open(base_url)
        page.open_ingredient_modal()
        assert page.is_modal_open(), "Не удалось открыть модалку"
        page.close_ingredient_modal()
        assert not page.is_modal_open(), "Модалка не закрылась"

    @allure.title("При добавлении ингредиента в заказ счётчик увеличивается")
    def test_ingredient_counter_increases(self, driver, base_url):
        page = MainPage(driver).open(base_url)
        before = page.get_ingredient_counter()
        page.add_ingredient_to_order()

        # ✅ Исправлено: ждём не просто >, а пока значение реально изменится и станет больше
        WebDriverWait(driver, 12).until(
            lambda d: (new := page.get_ingredient_counter()) != before and new > before
        )

        after = page.get_ingredient_counter()
        delta = after - before
        assert delta in (1, 2), f"Ожидали рост на 1 или 2 (булка даёт +2), было {before}, стало {after}"