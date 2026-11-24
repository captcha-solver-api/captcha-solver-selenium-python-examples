"""Solve callback-based reCAPTCHA v2 using the browser's proxy.

What it does:
    Opens the page through a configured proxy, extracts its site key, creates a
    ``RecaptchaV2Task`` with the same proxy and browser User-Agent, delivers the token to the
    page callback, and checks its success message with ``CaptchaClient.solve()``.

To use this example on another page, change the target URL and verify the site key and any
challenge-specific parameters required by that page. Token fields, callbacks, submission, and
success indicators are site-specific, so inspect the page before applying the token.

How it works:
    STEP-01 - Start browser and SDK client with one shared proxy.
    STEP-02 - Open the page through the proxy and extract its site key.
    STEP-03 - Create and solve the task through the same proxy.
    STEP-04 - Deliver the token to this demo's callback.
    STEP-05 - Verify successful callback handling on the page.
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
    logged_example,
    proxy_settings,
    required_env,
    selenium_proxy,
    show_success,
    wait_for_xpath,
)

URL = required_env("RECAPTCHA_V2_TARGET_URL", "TARGET_URL")
SITEKEY_LOCATOR = "//div[@id='g-recaptcha']"


@logged_example
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
        solution = client.solve(
            RecaptchaV2Task(
                websiteURL=URL,
                websiteKey=sitekey,
                userAgent=driver.execute_script("return navigator.userAgent"),
                **proxy_settings(),
            )
        )
        # STEP-04: Deliver the token to this demo's callback.
        # Token injection and submission are site-specific; adapt this step to the target page.
        driver.execute_script(
            "window.verifyDemoRecaptcha(arguments[0]);",
            solution["gRecaptchaResponse"],
        )
        print("The token is sent to the callback function")
        # STEP-05: Verify successful callback handling on the page.
        show_success(driver)
        time.sleep(5)


if __name__ == "__main__":
    main()
