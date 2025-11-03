import allure
from pages.main_page import MainPage
from test_data.config import BASE_URL


@allure.feature("Конструктор бургеров")
class TestConstructor:

    @allure.title("Если кликнуть на ингредиент — открывается модалка с деталями")
    def test_ingredient_modal_opens(self, driver):
        page = MainPage(driver).open(BASE_URL)
        page.open_ingredient_modal()
        assert page.is_modal_open(), "Модалка не открылась"

    @allure.title("Модалка ингредиента закрывается по крестику")
    def test_ingredient_modal_closes(self, driver):
        page = MainPage(driver).open(BASE_URL)
        page.open_ingredient_modal()
        assert page.is_modal_open(), "Не удалось открыть модалку"
        page.close_ingredient_modal()
        assert not page.is_modal_open(), "Модалка не закрылась"

    @allure.title("При добавлении ингредиента в заказ счётчик увеличивается")
    def test_ingredient_counter_increases(self, driver):
        page = MainPage(driver).open(BASE_URL)
        before = page.get_ingredient_counter()
        page.add_ingredient_to_order()

        # ждём рост счётчика через метод страницы (без WebDriverWait в тесте)
        after = page.wait_counter_increases(before, timeout=12)

        delta = after - before
        assert delta in (1, 2), (
            f"Ожидали рост на 1 или 2 (булка даёт +2), "
            f"было {before}, стало {after}"
        )