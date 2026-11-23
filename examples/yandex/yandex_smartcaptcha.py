"""Solve Yandex SmartCaptcha on the official demo with SeleniumBase.

What it does:
    Opens the official demo or YANDEX_SMARTCAPTCHA_TARGET_URL without a proxy, extracts its site key, solves
    YandexSmartCaptchaTaskProxyless, submits the token, and requires the demo's success text.

To use this example on another page, change its type-specific target URL and inspect the
site key or challenge parameters, solution fields or callbacks, submission controls, and exact success
signal before applying the result.

How it works:
    STEP-01 - starts browser/client.
    STEP-02 - reads the site key.
    STEP-03 - solves the SDK task.
    STEP-04 - submits the token.
    STEP-05 - verifies acceptance independently of SDK completion.
"""

import os
from pathlib import Path

from captcha_solver_api import CaptchaClient
from captcha_solver_api.tasks import YandexSmartCaptchaTaskProxyless
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
    return CaptchaClient(required_env("CAPTCHA_API_KEY"), debug=True)


def wait_for_css(driver, selector: str, timeout: int = 30):
    """Wait until a target-specific CSS selector exists."""
    return WebDriverWait(driver, timeout).until(
        EC.presence_of_element_located((By.CSS_SELECTOR, selector))
    )


def wait_for_xpath(driver, locator: str, timeout: int = 30):
    """Wait until a target-specific XPath is visible and enabled."""
    return WebDriverWait(driver, timeout).until(EC.element_to_be_clickable((By.XPATH, locator)))


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


URL = os.getenv("YANDEX_SMARTCAPTCHA_TARGET_URL") or "https://captcha-api.yandex.ru/demo"
SITEKEY_SELECTOR = ".smart-captcha[data-sitekey]"
SUBMIT_LOCATOR = "//*[@id='smartcaptcha-demo-submit']"
SUCCESS_TEXT = "Hello, user!"


def main() -> None:
    # STEP-01: Start the browser and SDK client.
    print("\n[STEP-01] Start the browser and SDK client.", flush=True)
    with Driver(browser="chrome", headless=False) as driver, create_client() as client:
        # STEP-02: Read the public widget key from the page opened in this browser.
        print(
            "\n[STEP-02] Read the public widget key from the page opened in this browser.",
            flush=True,
        )
        driver.get(URL)
        widget = wait_for_css(driver, SITEKEY_SELECTOR)
        sitekey = widget.get_attribute("data-sitekey")
        if not sitekey:
            raise RuntimeError("No Yandex SmartCaptcha sitekey found")
        print(f"Sitekey received: {sitekey}")

        # STEP-03: Create the task; solve() submits it and waits for its solution.

        print(
            "\n[STEP-03] Create the task; solve() submits it and waits for its solution.",
            flush=True,
        )
        task = YandexSmartCaptchaTaskProxyless(
            websiteURL=driver.current_url,
            websiteKey=sitekey,
            userAgent=driver.execute_script("return navigator.userAgent"),
        )
        solution = client.solve(task, timeout=180)
        print("Solution received; fields:", ", ".join(solution), flush=True)
        token = solution.get("token")
        if not isinstance(token, str) or not token.strip():
            raise RuntimeError("Captcha Solver returned an empty SmartCaptcha token")

        # STEP-04: Token injection and submission are site-specific; adapt this step.

        print(
            "\n[STEP-04] Token injection and submission are site-specific; adapt this step.",
            flush=True,
        )
        # This demo submits the token through a hidden form field.
        wait_for_css(driver, 'input[name="smart-token"]')
        fill_response_field(driver, "smart-token", token)
        print("Token sent")
        wait_for_xpath(driver, SUBMIT_LOCATOR).click()
        print("Submitted the form")

        # STEP-05: Confirm acceptance by the site, not just receipt of an API token.

        print(
            "\n[STEP-05] Confirm acceptance by the site, not just receipt of an API token.",
            flush=True,
        )
        WebDriverWait(driver, 30).until(
            EC.text_to_be_present_in_element((By.TAG_NAME, "body"), SUCCESS_TEXT)
        )
        print(f"SUCCESS: the site accepted the token and returned '{SUCCESS_TEXT}'.")


if __name__ == "__main__":
    main()
