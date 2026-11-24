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
    show_success,
    wait_for_xpath,
)

URL = required_env("RECAPTCHA_V2_TARGET_URL", "TARGET_URL")
SITEKEY_LOCATOR = "//div[@id='g-recaptcha']"


@logged_example
def main() -> None:
    # STEP-01: Start the browser and SDK client.
    with Driver(browser="chrome", headless=False) as driver, create_client() as client:
        # STEP-02: Open the configured page and read its widget site key.
        driver.get(URL)
        sitekey = wait_for_xpath(driver, SITEKEY_LOCATOR).get_attribute("data-sitekey")
        print(f"Sitekey received: {sitekey}")
        # STEP-03: Create and solve the proxyless reCAPTCHA task.
        solution = client.solve(RecaptchaV2TaskProxyless(websiteURL=URL, websiteKey=sitekey))
        # STEP-04: Pass the token to the callback registered by this demo page.
        # Token injection and submission are site-specific; adapt this step to the target page.
        driver.execute_script(
            "window.verifyDemoRecaptcha(arguments[0]);",
            solution["gRecaptchaResponse"],
        )
        print("The token is sent to the callback function")
        # STEP-05: Confirm that the page handled the callback successfully.
        show_success(driver)
        time.sleep(5)


if __name__ == "__main__":
    main()
