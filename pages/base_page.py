# pages/base_page.py
from __future__ import annotations

import time
from typing import Tuple, Optional, Iterable, Union, Callable
from contextlib import suppress

from selenium.webdriver.remote.webdriver import WebDriver, WebElement
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import (
    TimeoutException,
    ElementClickInterceptedException,
    StaleElementReferenceException,
)

Locator = Tuple[str, str]
MaybeEl = Union[Locator, WebElement]

DEFAULT_TIMEOUT = 12
DEFAULT_POLL = 0.2


class BasePage:
    """Базовый класс Page Object: все ожидания/клики/скроллы инкапсулированы здесь."""

    def __init__(self, driver: WebDriver, timeout: int = DEFAULT_TIMEOUT):
        self.driver = driver
        self.wait = WebDriverWait(driver, timeout, poll_frequency=DEFAULT_POLL)

    # ---------- utils ----------
    def _as_element(self, maybe: MaybeEl) -> WebElement:
        """Принимает локатор или элемент и возвращает элемент."""
        if isinstance(maybe, tuple) and len(maybe) == 2:
            return self.driver.find_element(*maybe)
        return maybe  # уже WebElement

    @property
    def current_url(self) -> str:
        return self.driver.current_url

    # ---------- navigation ----------
    def open(self, url: str) -> "BasePage":
        self.driver.get(url)
        return self

    # ---------- find/waits ----------
    def find(self, locator: Locator) -> WebElement:
        return self.driver.find_element(*locator)

    def finds(self, locator: Locator) -> list[WebElement]:
        return self.driver.find_elements(*locator)

    def wait_visible(self, locator: Locator) -> WebElement:
        return self.wait.until(EC.visibility_of_element_located(locator))

    def wait_clickable(self, locator: Locator) -> WebElement:
        return self.wait.until(EC.element_to_be_clickable(locator))

    def wait_gone(self, locator: Locator) -> bool:
        with suppress(TimeoutException):
            return bool(self.wait.until(EC.invisibility_of_element_located(locator)))
        return False

    def wait_any_visible(
        self, *locators: Iterable[Locator], timeout: Optional[int] = None
    ) -> WebElement:
        """Ждём, пока станет видим хотя бы один из переданных локаторов. Возвращает найденный элемент."""
        tw = self.wait if timeout is None else WebDriverWait(
            self.driver, timeout, poll_frequency=DEFAULT_POLL
        )
        conditions = [EC.visibility_of_element_located(loc) for loc in locators]
        return tw.until(EC.any_of(*conditions))

    def wait_until(
        self,
        condition: Callable[[], bool],
        timeout: Optional[int] = None,
        message: Optional[str] = None,
    ):
        """
        Ждём произвольное булево-условие.
        При таймауте выбрасывает AssertionError с понятным сообщением (если message задан).
        """
        tw = self.wait if timeout is None else WebDriverWait(
            self.driver, timeout, poll_frequency=DEFAULT_POLL
        )
        try:
            return tw.until(lambda d: condition())
        except TimeoutException:
            if message:
                raise AssertionError(message)
            raise

    def is_present(self, locator: Locator) -> bool:
        with suppress(Exception):
            self.driver.find_element(*locator)
            return True
        return False

    def is_visible(self, locator: Locator) -> bool:
        with suppress(Exception):
            self.wait_visible(locator)
            return True
        return False

    # ---------- high-level actions ----------
    def click(self, locator: Locator) -> None:
        self.safe_click(locator)

    def type(self, locator: Locator, text: str, clear: bool = True) -> WebElement:
        el = self.wait_visible(locator)
        if clear:
            el.clear()
        el.send_keys(text)
        return el

    def get_text(self, locator: Locator) -> str:
        return self.wait_visible(locator).text

    # ---------- view helpers ----------
    def scroll_into_view(self, target: MaybeEl) -> None:
        """Принимает локатор или элемент; скроллит к нему по центру."""
        el = self._as_element(target)
        with suppress(Exception):
            self.driver.execute_script("arguments[0].scrollIntoView({block:'center'});", el)

    def scroll_to_top(self) -> None:
        with suppress(Exception):
            self.driver.execute_script("window.scrollTo(0, 0);")

    def js_click(self, target: MaybeEl) -> None:
        el = self._as_element(target)
        self.driver.execute_script("arguments[0].click();", el)

    # ---------- safe click ----------
    def safe_click(self, locator: Locator) -> None:
        last_err: Optional[Exception] = None
        for _ in range(2):
            try:
                el = self.wait_visible(locator)
                self.scroll_into_view(el)
                self.wait_clickable(locator).click()
                return
            except (ElementClickInterceptedException, StaleElementReferenceException) as e:
                last_err = e
                time.sleep(0.25)
                with suppress(Exception):
                    self.close_overlays_if_any()
                    self.scroll_to_top()

        # финальный JS-клик как «план Б»
        with suppress(Exception):
            el = self.find(locator)
            self.scroll_into_view(el)
            self.js_click(el)
            return

        if last_err:
            raise last_err

    # ---------- DnD через JS (универсально для FF/Chrome) ----------
    def drag_and_drop_js(self, source: Locator, target: Locator) -> None:
        self.wait_visible(source)
        self.wait_visible(target)
        src_el = self.find(source)
        tgt_el = self.find(target)
        self.scroll_into_view(src_el)
        self.scroll_into_view(tgt_el)
        self.driver.execute_script(
            """
            var s = arguments[0], t = arguments[1];
            function fire(el, type, dt){
              var e = document.createEvent('CustomEvent');
              e.initCustomEvent(type, true, true, null);
              e.dataTransfer = dt;
              el.dispatchEvent(e);
            }
            var dt = {data:{}, setData(k,v){this.data[k]=v}, getData(k){return this.data[k]}};
            fire(s,'dragstart',dt); fire(t,'dragenter',dt); fire(t,'dragover',dt); fire(t,'drop',dt); fire(s,'dragend',dt);
            """,
            src_el, tgt_el,
        )

    # ---------- hook ----------
    def close_overlays_if_any(self) -> None:
        """Переопределяй на страницах с модалками/оверлеями, если нужно что-то закрывать перед кликом."""
        pass