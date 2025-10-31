from __future__ import annotations
import re
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from pages.base_page import BasePage
from locators.order_feed_locators import OrderFeedLocators as L

def _to_int_safe(txt: str) -> int:
    return int(re.sub(r"\D", "", txt or "") or 0)

class OrderFeedPage(BasePage):
    def open_feed(self, base_url: str) -> "OrderFeedPage":
        self.open(f"{base_url}feed")
        return self

    def wait_loaded(self) -> "OrderFeedPage":
        # ждём любую опорную штуку ленты
        self.wait.until(EC.any_of(
            EC.visibility_of_element_located(L.HEADER_IN_PROGRESS),
            EC.visibility_of_element_located(L.TOTAL_ALL_TIME),
            EC.visibility_of_element_located(L.TOTAL_TODAY),
        ))
        return self

    def scroll_to_counters(self) -> "OrderFeedPage":
        # прокручиваем к одному из заголовков, чтобы ленивый рендер дорисовал цифры
        try:
            el = self.wait_visible(L.TOTAL_ALL_TIME)
        except Exception:
            el = self.wait_visible(L.HEADER_IN_PROGRESS)
        self._driver.execute_script("arguments[0].scrollIntoView({block:'center'})", el)
        return self

    def total_all_time(self) -> int:
        el = self.wait_visible(L.TOTAL_ALL_TIME)
        return _to_int_safe(el.text)

    def total_today(self) -> int:
        el = self.wait_visible(L.TOTAL_TODAY)
        return _to_int_safe(el.text)

    def has_order_in_progress(self, order_number: str) -> bool:
        nums = [el.text.strip() for el in self.finds(L.IN_PROGRESS_NUMBERS)]
        return order_number.strip() in {n.strip() for n in nums}