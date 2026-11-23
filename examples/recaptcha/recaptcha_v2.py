"""Solve reCAPTCHA v2 in a SeleniumBase browser session.

What it does:
    Opens the official demo or RECAPTCHA_V2_TARGET_URL without a proxy, extracts the widget site key, solves
    RecaptchaV2TaskProxyless, injects the token, submits the form, and checks page acceptance.

To use this example on another page, change its type-specific target URL and inspect the
site key or challenge parameters, solution fields or callbacks, submission controls, and exact success
signal before applying the result.

How it works:
    STEP-01 - starts the browser/client.
    STEP-02 - reads the site key.
    STEP-03 - creates and solves the
    SDK task.
    STEP-04 - submits the token.
    STEP-05 - requires the page's success message.
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


def fill_response_field(driver, field_name: str, token: str) -> None:
    """Set a target-specific response field and dispatch its input/change events."""
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


URL = os.getenv("RECAPTCHA_V2_TARGET_URL") or "https://www.google.com/recaptcha/api2/demo"
SITEKEY_LOCATOR = "//*[@data-sitekey]"
SUBMIT_LOCATOR = "//*[@type='submit']"


def main() -> None:
    # STEP-01: Start the browser and SDK client; the client reads CAPTCHA_API_KEY.
    with Driver(browser="chrome", headless=False) as driver, create_client() as client:
        # STEP-02: Open the page and extract the site key rendered by its widget.
        driver.get(URL)
        widget = wait_for_xpath(driver, SITEKEY_LOCATOR)
        sitekey = widget.get_attribute("data-sitekey")
        if not sitekey:
            raise RuntimeError("No reCAPTCHA sitekey found")
        print(f"Sitekey received: {sitekey}")

        # STEP-03: Build the proxyless task and let solve() create and poll it.
        task = RecaptchaV2TaskProxyless(
            websiteURL=URL,
            websiteKey=sitekey,
            userAgent=driver.execute_script("return navigator.userAgent"),
        )
        solution = client.solve(task)
        print("Solution:", solution)
        # STEP-04: Apply the token using this page's response field and submit the form.
        # Token injection and submission are site-specific; adapt this step to the target page.
        fill_response_field(driver, "g-recaptcha-response", solution["gRecaptchaResponse"])
        print("Token sent")
        wait_for_xpath(driver, SUBMIT_LOCATOR).click()
        print("Pressed the Check button")
        # STEP-05: Require the page's success message; receiving a token is not acceptance.
        show_success(driver)


if __name__ == "__main__":
    main()
