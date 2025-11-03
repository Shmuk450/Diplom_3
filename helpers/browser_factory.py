from __future__ import annotations

import os
from selenium import webdriver
from selenium.webdriver.chrome.options import Options as ChromeOptions
from selenium.webdriver.firefox.options import Options as FirefoxOptions


def make_chrome(headless: bool):
    opts = ChromeOptions()
    if headless or os.getenv("HEADLESS") == "1":
        opts.add_argument("--headless=new")
    opts.add_argument("--window-size=1280,900")
    opts.add_argument("--no-sandbox")
    opts.add_argument("--disable-dev-shm-usage")
    return webdriver.Chrome(options=opts)


def make_firefox(headless: bool):
    opts = FirefoxOptions()
    if headless or os.getenv("HEADLESS") == "1":
        opts.add_argument("-headless")
    drv = webdriver.Firefox(options=opts)
    drv.set_window_size(1280, 900)
    return drv