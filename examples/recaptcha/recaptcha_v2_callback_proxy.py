"""Solve callback-based reCAPTCHA v2 using the same proxy as the browser.

What it does:
    Opens RECAPTCHA_V2_TARGET_URL through a proxy, extracts the site key, solves RecaptchaV2Task through the
    same proxy, passes its token to a known callback, and checks page acceptance.

To use this example on another page, change its type-specific target URL and inspect the
site key or challenge parameters, solution fields or callbacks, submission controls, and exact success
signal before applying the result.

How it works:
    STEP-01 - configures browser/client.
    STEP-02 - reads the site key.
    STEP-03 - solves the proxied
    task.
    STEP-04 - invokes the callback.
    STEP-05 - verifies the page result.
"""

import os
from pathlib import Path

from captcha_solver_api import CaptchaClient
from captcha_solver_api.tasks import RecaptchaV2Task
from dotenv import load_dotenv
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from seleniumbase import Driver

REPOSITORY_ROOT = Path(__file__).resolve().parents[2]
load_dotenv(REPOSITORY_ROOT / ".env")


def required_env(name: str) -> str:
    """Return a required environment value or explain how to configure it."""
    value = os.getenv(name)
    if not value:
        raise RuntimeError(f"Set {name} in the environment or .env file")
    return value


def create_client() -> CaptchaClient:
    """Create the SDK client with CAPTCHA_API_KEY."""
    return CaptchaClient(required_env("CAPTCHA_API_KEY"))


def wait_for_xpath(driver, locator: str, timeout: int = 30):
    """Wait until a target-specific XPath is visible and enabled."""
    return WebDriverWait(driver, timeout).until(EC.element_to_be_clickable((By.XPATH, locator)))


def show_success(driver) -> None:
    """Require the exact target-specific success text configured by the user."""
    expected_text = required_env("CAPTCHA_SUCCESS_TEXT")
    WebDriverWait(driver, 30).until(
        EC.text_to_be_present_in_element((By.TAG_NAME, "body"), expected_text)
    )
    print(f"Page confirmation: {expected_text}")


def proxy_settings() -> dict:
    """Build the SDK proxy options from the same values used by the browser."""
    return {
        "proxyType": required_env("PROXY_TYPE"),
        "proxyAddress": required_env("PROXY_ADDRESS"),
        "proxyPort": int(required_env("PROXY_PORT")),
        "proxyLogin": os.getenv("PROXY_LOGIN"),
        "proxyPassword": os.getenv("PROXY_PASSWORD"),
    }


def selenium_proxy() -> str:
    """Build SeleniumBase's proxy string from the configured proxy options."""
    settings = proxy_settings()
    address = settings["proxyAddress"]
    port = settings["proxyPort"]
    login = settings["proxyLogin"]
    password = settings["proxyPassword"]
    if login and password:
        return f"{login}:{password}@{address}:{port}"
    return f"{address}:{port}"


URL = required_env("RECAPTCHA_V2_TARGET_URL")
SITEKEY_LOCATOR = "//div[@id='g-recaptcha']"


def main() -> None:
    # STEP-01: Start browser and SDK client with one shared proxy.
    with (
        Driver(browser="chrome", headless=False, cft=True, proxy=selenium_proxy()) as driver,
        create_client() as client,
    ):
        # STEP-02: Open the page through the proxy and extract its site key.
        driver.get(URL)
        try:
            sitekey = wait_for_xpath(driver, SITEKEY_LOCATOR).get_attribute("data-sitekey")
        except TimeoutException as exc:
            raise RuntimeError(
                "The target page did not load through the configured proxy. "
                "Check the proxy address, credentials, and availability."
            ) from exc
        print("Got the callback function name and site key")
        # STEP-03: Create and solve the task through the same proxy.
        task = RecaptchaV2Task(
            websiteURL=URL,
            websiteKey=sitekey,
            userAgent=driver.execute_script("return navigator.userAgent"),
            **proxy_settings(),
        )
        solution = client.solve(task)
        print("Solution:", solution)
        # STEP-04: Deliver the token to this demo's callback.
        # Token injection and submission are site-specific; adapt this step to the target page.
        driver.execute_script(
            "window.verifyDemoRecaptcha(arguments[0]);",
            solution["gRecaptchaResponse"],
        )
        print("The token is sent to the callback function")
        # STEP-05: Verify successful callback handling on the page.
        show_success(driver)


if __name__ == "__main__":
    main()
