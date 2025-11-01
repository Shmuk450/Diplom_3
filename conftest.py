import os
import time
import pytest
from contextlib import suppress

from helpers.browser_factory import make_chrome, make_firefox
from pages.login_page import LoginPage
from test_data.config import BASE_URL


# -------- driver для двух браузеров --------
@pytest.fixture(params=["chrome", "firefox"], scope="function")
def driver(request):
    """Создаёт драйвер Chrome/Firefox"""
    headless = os.getenv("HEADLESS") == "1"
    browser = request.param
    drv = make_chrome(headless) if browser == "chrome" else make_firefox(headless)
    drv.implicitly_wait(2)
    yield drv
    drv.quit()


# ---------- креды: файл -> ENV ----------
try:
    from test_data.credentials import (
        STELLAR_EMAIL as _FILE_EMAIL,
        STELLAR_PASSWORD as _FILE_PASSWORD,
    )
except ImportError:
    _FILE_EMAIL = _FILE_PASSWORD = None


@pytest.fixture
def auth_login(driver):
    """Авторизация с использованием файла или переменных окружения"""
    email = _FILE_EMAIL or os.getenv("STELLAR_EMAIL")
    password = _FILE_PASSWORD or os.getenv("STELLAR_PASSWORD")

    if not (email and password):
        pytest.skip(
            "Нет учётных данных. Укажи STELLAR_EMAIL/STELLAR_PASSWORD в env "
            "или подключи test_data/credentials.py."
        )

    LoginPage(driver).login(BASE_URL, email, password)
    yield


# -------- артефакты при падении --------
@pytest.hookimpl(hookwrapper=True, tryfirst=True)
def pytest_runtest_makereport(item, call):
    """Сохраняет скриншот и HTML при падении теста"""
    outcome = yield
    rep = outcome.get_result()

    if rep.when != "call" or not rep.failed:
        return

    drv = item.funcargs.get("driver")
    if not drv:
        return

    browser = getattr(getattr(item, "callspec", None), "params", {}).get("driver")
    suffix = f"_{browser}" if browser else ""

    ts = time.strftime("%Y%m%d-%H%M%S")
    name = f"{item.name}{suffix}_{ts}"

    os.makedirs("artifacts", exist_ok=True)

    # без try/except — используем suppress
    with suppress(Exception):
        drv.save_screenshot(f"artifacts/{name}.png")
    with suppress(Exception):
        with open(f"artifacts/{name}.html", "w", encoding="utf-8") as f:
            f.write(drv.page_source)