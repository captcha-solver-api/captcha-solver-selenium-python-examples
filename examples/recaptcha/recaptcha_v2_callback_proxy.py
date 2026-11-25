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
    wait_for_css,
)

URL = required_env("RECAPTCHA_V2_CALLBACK_TARGET_URL")
CALLBACK_NAME = required_env("RECAPTCHA_V2_CALLBACK_NAME")
SUCCESS_SELECTOR = required_env("RECAPTCHA_V2_CALLBACK_SUCCESS_SELECTOR")
SITEKEY_SELECTOR = "[data-sitekey]"


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
            sitekey = wait_for_css(driver, SITEKEY_SELECTOR).get_attribute("data-sitekey")
        except TimeoutException as exc:
            raise RuntimeError(
                "The target page did not load through the configured proxy. "
                "Check the proxy address, credentials, and availability."
            ) from exc
        if not sitekey:
            raise RuntimeError("No reCAPTCHA sitekey found on the callback page")
        print(f"Sitekey received: {sitekey}; callback: {CALLBACK_NAME}")
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
            """
            const callbackName = arguments[0];
            const callback = callbackName
              .split('.')
              .reduce((value, key) => value?.[key], window);
            if (typeof callback !== 'function') {
              throw new Error(`Callback ${callbackName} was not found`);
            }
            callback(arguments[1]);
            """,
            CALLBACK_NAME,
            solution["gRecaptchaResponse"],
        )
        print(f"The token is sent to callback {CALLBACK_NAME}")
        # STEP-05: Verify successful callback handling on the page.
        print(wait_for_css(driver, SUCCESS_SELECTOR).text)
        time.sleep(5)


if __name__ == "__main__":
    main()
