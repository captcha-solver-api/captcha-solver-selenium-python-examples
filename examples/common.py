"""Shared helpers for the Selenium examples."""

import json
import os
from functools import wraps
from typing import Any, Dict, Optional

from captcha_solver_api import CaptchaClient
from dotenv import load_dotenv
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

load_dotenv()


class ConsoleCaptchaClient(CaptchaClient):
    """Captcha client that prints the complete solution returned by the API."""

    def solve(
        self,
        task: Any,
        language_pool: Optional[str] = None,
        timeout: Optional[int] = None,
    ) -> Dict[str, Any]:
        solution = super().solve(task, language_pool=language_pool, timeout=timeout)
        if "text" in solution:
            print(f"Captcha solved. Code: {solution['text']}")
        elif "coordinates" in solution:
            print("Captcha solved. Coordinates received")
        else:
            print("Captcha solved")
        print("API response:")
        print(json.dumps(solution, ensure_ascii=False, indent=2, sort_keys=True))
        return solution


def logged_example(function):
    """Print the same lifecycle messages as the reference Selenium examples."""

    @wraps(function)
    def wrapper(*args, **kwargs):
        print("Started")
        try:
            result = function(*args, **kwargs)
        except Exception as error:
            print(f"An error occurred: {error}")
            print("Failed to solve captcha")
            raise
        print("Finished")
        return result

    return wrapper


def required_env(*names: str) -> str:
    """Return the first configured variable, allowing specific-to-generic fallbacks."""
    for name in names:
        value = os.getenv(name)
        if value:
            return value
    expected = " or ".join(names)
    raise RuntimeError(f"Set {expected} in the environment or .env file")


def create_client() -> CaptchaClient:
    # SDK debug output includes sanitized task payloads, task IDs, polling updates,
    # request timing, and the final poll count without exposing credentials or images.
    return ConsoleCaptchaClient(required_env("CAPTCHA_API_KEY"), debug=True)


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
