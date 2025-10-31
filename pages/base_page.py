from __future__ import annotations
import time
from typing import Tuple, Optional

from selenium.webdriver.remote.webdriver import WebDriver, WebElement
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import (
    TimeoutException,
    ElementClickInterceptedException,
    StaleElementReferenceException,
)

DEFAULT_TIMEOUT = 12
DEFAULT_POLL = 0.2


class BasePage:
    def __init__(self, driver: WebDriver, timeout: int = DEFAULT_TIMEOUT):
        self._driver = driver
        self.wait = WebDriverWait(driver, timeout, poll_frequency=DEFAULT_POLL)

    # ---------- navigation ----------
    def open(self, url: str) -> "BasePage":
        self._driver.get(url)
        return self

    # ---------- find/waits ----------
    def find(self, locator: Tuple[str, str]) -> WebElement:
        return self._driver.find_element(*locator)

    def finds(self, locator: Tuple[str, str]):
        return self._driver.find_elements(*locator)

    def wait_visible(self, locator: Tuple[str, str]) -> WebElement:
        return self.wait.until(EC.visibility_of_element_located(locator))

    def wait_clickable(self, locator: Tuple[str, str]) -> WebElement:
        return self.wait.until(EC.element_to_be_clickable(locator))

    def wait_gone(self, locator: Tuple[str, str]) -> bool:
        try:
            return self.wait.until(EC.invisibility_of_element_located(locator))
        except TimeoutException:
            return False

    def is_present(self, locator: Tuple[str, str]) -> bool:
        try:
            self._driver.find_element(*locator)
            return True
        except Exception:
            return False

    # ---------- view helpers ----------
    def scroll_into_view(self, element: WebElement) -> None:
        try:
            self._driver.execute_script("arguments[0].scrollIntoView({block:'center'});", element)
        except Exception:
            pass

    def scroll_to_top(self) -> None:
        try:
            self._driver.execute_script("window.scrollTo(0, 0);")
        except Exception:
            pass

    def js_click(self, element: WebElement) -> None:
        self._driver.execute_script("arguments[0].click();", element)

    # ---------- safe click ----------
    def safe_click(self, locator: Tuple[str, str]) -> None:
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
                try:
                    self.close_overlays_if_any()
                    self.scroll_to_top()
                except Exception:
                    pass
        # финальный JS-клик
        try:
            el = self.find(locator)
            self.scroll_into_view(el)
            self.js_click(el)
            return
        except Exception:
            if last_err:
                raise last_err
            raise

    def click(self, locator: Tuple[str, str]) -> None:
        self.safe_click(locator)

    # ---------- DnD через JS (универсально для FF/Chrome) ----------
    def drag_and_drop_js(self, source_locator: Tuple[str, str], target_locator: Tuple[str, str]) -> None:
        self.wait_visible(source_locator)
        self.wait_visible(target_locator)
        source_el = self.find(source_locator)
        target_el = self.find(target_locator)
        self.scroll_into_view(source_el)
        self.scroll_into_view(target_el)
        self._driver.execute_script("""
            var s = arguments[0], t = arguments[1];
            function fire(el, type, dt){
              var e = document.createEvent('CustomEvent');
              e.initCustomEvent(type, true, true, null);
              e.dataTransfer = dt;
              el.dispatchEvent(e);
            }
            var dt = {data:{}, setData(k,v){this.data[k]=v}, getData(k){return this.data[k]}};
            fire(s,'dragstart',dt); fire(t,'dragenter',dt); fire(t,'dragover',dt); fire(t,'drop',dt); fire(s,'dragend',dt);
        """, source_el, target_el)

    # ---------- hook ----------
    def close_overlays_if_any(self) -> None:
        """Переопределяется на страницах с модалками."""
        pass