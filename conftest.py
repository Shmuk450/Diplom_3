# conftest.py
import os
import time
import pytest

from selenium import webdriver
from selenium.webdriver.chrome.options import Options as ChromeOptions
from selenium.webdriver.firefox.options import Options as FirefoxOptions
from pages.login_page import LoginPage



# -------- базовый URL --------
@pytest.fixture(scope="session")
def base_url() -> str:
    return "https://stellarburgers.education-services.ru/"


# -------- фабрики браузеров (без webdriver_manager) --------
def _make_chrome(headless: bool):
    opts = ChromeOptions()
    if headless or os.getenv("HEADLESS") == "1":
        # новый headless у Chrome
        opts.add_argument("--headless=new")
    opts.add_argument("--window-size=1280,900")
    opts.add_argument("--no-sandbox")
    opts.add_argument("--disable-dev-shm-usage")
    # Selenium Manager сам подтянет подходящий chromedriver
    return webdriver.Chrome(options=opts)

def _make_firefox(headless: bool):
    opts = FirefoxOptions()
    if headless or os.getenv("HEADLESS") == "1":
        opts.add_argument("-headless")
    drv = webdriver.Firefox(options=opts)  # geckodriver подтянет Selenium Manager
    try:
        drv.set_window_size(1280, 900)
    except Exception:
        pass
    return drv


# -------- driver для двух браузеров --------
@pytest.fixture(params=["chrome", "firefox"], scope="function")
def driver(request):
    headless = os.getenv("HEADLESS") == "1"
    browser = request.param
    drv = _make_chrome(headless) if browser == "chrome" else _make_firefox(headless)
    drv.implicitly_wait(2)
    yield drv
    try:
        drv.quit()
    except Exception:
        pass


# -------- артефакты при падении --------
@pytest.hookimpl(hookwrapper=True, tryfirst=True)
def pytest_runtest_makereport(item, call):
    outcome = yield
    rep = outcome.get_result()

    if rep.when == "call" and rep.failed:
        drv = item.funcargs.get("driver")
        if not drv:
            return

        # имя браузера в имени файла
        browser = None
        cs = getattr(item, "callspec", None)
        if cs:
            browser = cs.params.get("driver")
        suffix = f"_{browser}" if browser else ""

        ts = time.strftime("%Y%m%d-%H%M%S")
        name = f"{item.name}{suffix}_{ts}"

        os.makedirs("artifacts", exist_ok=True)
        try:
            drv.save_screenshot(f"artifacts/{name}.png")
        except Exception:
            pass
        try:
            with open(f"artifacts/{name}.html", "w", encoding="utf-8") as f:
                f.write(drv.page_source)
        except Exception:
            pass

    
# ---------- креды: файл -> ENV ----------
try:
    from test_data.credentials import STELLAR_EMAIL as _FILE_EMAIL, STELLAR_PASSWORD as _FILE_PASSWORD
except ImportError:
    _FILE_EMAIL = _FILE_PASSWORD = None


@pytest.fixture
def auth_login(driver, base_url):
    # сначала берём из файла, иначе из ENV
    email = _FILE_EMAIL or os.getenv("STELLAR_EMAIL")
    password = _FILE_PASSWORD or os.getenv("STELLAR_PASSWORD")

    if not (email and password):
        pytest.skip("Нет учётных данных. Укажи STELLAR_EMAIL/STELLAR_PASSWORD в env "
                    "или подключи test_data/credentials.py.")

    # важно: передаём base_url, email, password
    LoginPage(driver).login(base_url, email, password)
    yield