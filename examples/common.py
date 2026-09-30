"""Shared helpers for the Selenium examples."""

import os
from typing import Dict

from captcha_solver_api import CaptchaClient
from dotenv import load_dotenv
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

load_dotenv()


def required_env(name: str) -> str:
    value = os.getenv(name)
    if not value:
        raise RuntimeError(f"Set {name} in the environment or .env file")
    return value


def create_client() -> CaptchaClient:
    return CaptchaClient(required_env("CAPTCHA_API_KEY"))


def wait_for_css(driver, selector: str, timeout: int = 30):
    return WebDriverWait(driver, timeout).until(
        EC.presence_of_element_located((By.CSS_SELECTOR, selector))
    )


def wait_for_xpath(driver, locator: str, timeout: int = 30):
    return WebDriverWait(driver, timeout).until(EC.element_to_be_clickable((By.XPATH, locator)))


def show_success(driver) -> None:
    message = wait_for_xpath(driver, "//p[contains(@class,'successMessage')]")
    print(message.text)


def proxy_settings() -> Dict[str, object]:
    return {
        "proxyType": required_env("PROXY_TYPE"),
        "proxyAddress": required_env("PROXY_ADDRESS"),
        "proxyPort": int(required_env("PROXY_PORT")),
        "proxyLogin": os.getenv("PROXY_LOGIN"),
        "proxyPassword": os.getenv("PROXY_PASSWORD"),
    }


def selenium_proxy() -> str:
    settings = proxy_settings()
    address = settings["proxyAddress"]
    port = settings["proxyPort"]
    login = settings["proxyLogin"]
    password = settings["proxyPassword"]
    if login and password:
        return f"{login}:{password}@{address}:{port}"
    return f"{address}:{port}"


def fill_response_field(driver, field_name: str, token: str) -> None:
    driver.execute_script(
        """
        const field = document.querySelector(`[name="${arguments[0]}"]`);
        if (!field) throw new Error(`Response field ${arguments[0]} was not found`);
        field.value = arguments[1];
        field.innerHTML = arguments[1];
        field.dispatchEvent(new Event('input', {bubbles: true}));
        field.dispatchEvent(new Event('change', {bubbles: true}));
        """,
        field_name,
        token,
    )
