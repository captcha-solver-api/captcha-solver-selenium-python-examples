"""Solve reCAPTCHA v2 and invoke the callback known by the demo page.

What it does:
    Reads a widget site key from RECAPTCHA_V2_TARGET_URL, solves RecaptchaV2TaskProxyless, delivers the token
    to the page's known callback, and checks the page's success message.

To use this example on another page, change its type-specific target URL and inspect the
site key or challenge parameters, solution fields or callbacks, submission controls, and exact success
signal before applying the result.

How it works:
    STEP-01 - starts browser/client.
    STEP-02 - extracts the site key.
    STEP-03 - solves the SDK task.
    STEP-04 - invokes the site-specific callback.
    STEP-05 - verifies callback handling.
"""

import os
from pathlib import Path

from captcha_solver_api import CaptchaClient
from captcha_solver_api.tasks import RecaptchaV2TaskProxyless
from dotenv import load_dotenv
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


URL = required_env("RECAPTCHA_V2_TARGET_URL")
SITEKEY_LOCATOR = "//div[@id='g-recaptcha']"


def main() -> None:
    # STEP-01: Start the browser and SDK client.
    with Driver(browser="chrome", headless=False) as driver, create_client() as client:
        # STEP-02: Open the configured page and read its widget site key.
        driver.get(URL)
        sitekey = wait_for_xpath(driver, SITEKEY_LOCATOR).get_attribute("data-sitekey")
        print(f"Sitekey received: {sitekey}")
        # STEP-03: Create and solve the proxyless reCAPTCHA task.
        task = RecaptchaV2TaskProxyless(websiteURL=URL, websiteKey=sitekey)
        solution = client.solve(task)
        print("Solution:", solution)
        # STEP-04: Pass the token to the callback registered by this demo page.
        # Token injection and submission are site-specific; adapt this step to the target page.
        driver.execute_script(
            "window.verifyDemoRecaptcha(arguments[0]);",
            solution["gRecaptchaResponse"],
        )
        print("The token is sent to the callback function")
        # STEP-05: Confirm that the page handled the callback successfully.
        show_success(driver)


if __name__ == "__main__":
    main()
