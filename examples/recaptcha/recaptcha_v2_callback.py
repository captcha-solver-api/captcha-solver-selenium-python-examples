"""Solve reCAPTCHA v2 and invoke a callback known by the page.

What it does:
    Reads the widget site key, solves ``RecaptchaV2TaskProxyless`` without a proxy, passes the
    returned token to the page's named callback, and checks its success message. The SDK task is
    submitted and awaited by ``CaptchaClient.solve()``.

To use this example on another page, change the target URL and verify the site key and any
challenge-specific parameters required by that page. Token fields, callbacks, submission, and
success indicators are site-specific, so inspect the page before applying the token.

How it works:
    STEP-01 - Start the browser and SDK client.
    STEP-02 - Open the configured page and read its widget site key.
    STEP-03 - Create and solve the proxyless reCAPTCHA task.
    STEP-04 - Pass the token to the callback registered by this demo page.
    STEP-05 - Confirm that the page handled the callback successfully.
"""

import sys
import time
from pathlib import Path

from captcha_solver_api.tasks import RecaptchaV2TaskProxyless
from seleniumbase import Driver

if __package__ in {None, ""}:
    sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from examples.common import (  # noqa: E402
    create_client,
    logged_example,
    required_env,
    wait_for_css,
)

URL = required_env("RECAPTCHA_V2_CALLBACK_TARGET_URL")
CALLBACK_NAME = required_env("RECAPTCHA_V2_CALLBACK_NAME")
SUCCESS_SELECTOR = required_env("RECAPTCHA_V2_CALLBACK_SUCCESS_SELECTOR")
SITEKEY_SELECTOR = "[data-sitekey]"


@logged_example
def main() -> None:
    # STEP-01: Start the browser and SDK client.
    with Driver(browser="chrome", headless=False) as driver, create_client() as client:
        # STEP-02: Open the configured page and read its widget site key.
        driver.get(URL)
        sitekey = wait_for_css(driver, SITEKEY_SELECTOR).get_attribute("data-sitekey")
        if not sitekey:
            raise RuntimeError("No reCAPTCHA sitekey found on the callback page")
        print(f"Sitekey received: {sitekey}")
        # STEP-03: Create and solve the proxyless reCAPTCHA task.
        solution = client.solve(RecaptchaV2TaskProxyless(websiteURL=URL, websiteKey=sitekey))
        # STEP-04: Pass the token to the callback registered by this demo page.
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
        # STEP-05: Confirm that the page handled the callback successfully.
        print(wait_for_css(driver, SUCCESS_SELECTOR).text)
        time.sleep(5)


if __name__ == "__main__":
    main()
