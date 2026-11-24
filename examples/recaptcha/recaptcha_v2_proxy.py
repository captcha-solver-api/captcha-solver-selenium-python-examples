"""Solve reCAPTCHA v2 with the same proxy in the browser and task.

What it does:
    Opens the target through a configured proxy, extracts the site key, solves a
    ``RecaptchaV2Task`` with matching proxy and User-Agent values, injects the token, submits
    the form, and verifies acceptance through ``CaptchaClient.solve()``.

To use this example on another page, change the target URL and verify the site key and any
challenge-specific parameters required by that page. Token fields, callbacks, submission, and
success indicators are site-specific, so inspect the page before applying the token.

How it works:
    STEP-01 - Start browser and SDK client with one shared proxy configuration.
    STEP-02 - Open the page through the proxy and extract its site key.
    STEP-03 - Create the proxied task with the browser's User-Agent.
    STEP-04 - Apply the token and submit this page's form.
    STEP-05 - Require the page's success message.
"""

import sys
import time
from pathlib import Path

from captcha_solver_api.tasks import RecaptchaV2Task
from selenium.common.exceptions import TimeoutException
from seleniumbase import Driver

if __package__ in {None, ""}:
    sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from examples.common import (  # noqa: E402
    create_client,
    fill_response_field,
    logged_example,
    proxy_settings,
    required_env,
    selenium_proxy,
    show_success,
    wait_for_xpath,
)

URL = required_env("RECAPTCHA_V2_TARGET_URL", "TARGET_URL")
SITEKEY_LOCATOR = "//div[@id='g-recaptcha']"
SUBMIT_LOCATOR = "//button[@data-action='demo_action']"


@logged_example
def main() -> None:
    # STEP-01: Start browser and SDK client with one shared proxy configuration.
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
        print(f"Sitekey received: {sitekey}")
        # STEP-03: Create the proxied task with the browser's User-Agent.
        solution = client.solve(
            RecaptchaV2Task(
                websiteURL=URL,
                websiteKey=sitekey,
                userAgent=driver.execute_script("return navigator.userAgent"),
                **proxy_settings(),
            )
        )
        # STEP-04: Apply the token and submit this page's form.
        # Token injection and submission are site-specific; adapt this step to the target page.
        fill_response_field(driver, "g-recaptcha-response", solution["gRecaptchaResponse"])
        print("Token sent")
        wait_for_xpath(driver, SUBMIT_LOCATOR).click()
        print("Pressed the Check button")
        # STEP-05: Require the page's success message.
        show_success(driver)
        time.sleep(5)


if __name__ == "__main__":
    main()
