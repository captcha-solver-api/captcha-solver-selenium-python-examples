"""Solve a standalone Cloudflare Turnstile widget.

What it does:
    Reads a widget site key from a user-configured page, solves a proxyless Turnstile task,
    places the returned token in the demo form, and verifies that the page accepts it. The
    example uses ``TurnstileTaskProxyless`` and ``CaptchaClient.solve()``.

To use this example on another page, change the target URL and verify the site key and any
challenge-specific parameters required by that page. Token fields, callbacks, submission, and
success indicators are site-specific, so inspect the page before applying the token.

How it works:
    STEP-01 - Start the browser and SDK client.
    STEP-02 - Open the page and extract the widget's public site key.
    STEP-03 - Create and solve the proxyless Turnstile task.
    STEP-04 - Put the token into this demo's response field.
    STEP-05 - Require the page's success message after submission.
"""

import sys
import time
from pathlib import Path

from captcha_solver_api.tasks import TurnstileTaskProxyless
from selenium.common.exceptions import ElementClickInterceptedException
from seleniumbase import Driver

if __package__ in {None, ""}:
    sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from examples.common import (  # noqa: E402
    create_client,
    fill_response_field,
    logged_example,
    required_env,
    show_success,
    wait_for_xpath,
)

URL = required_env("TURNSTILE_TARGET_URL", "TARGET_URL")
SITEKEY_LOCATOR = "//div[@id='cf-turnstile']"
SUBMIT_LOCATOR = "//button[@type='submit']"


@logged_example
def main() -> None:
    # STEP-01: Start the browser and SDK client.
    with Driver(browser="chrome", headless=False) as driver, create_client() as client:
        # STEP-02: Open the page and extract the widget's public site key.
        driver.get(URL)
        widget = wait_for_xpath(driver, SITEKEY_LOCATOR)
        sitekey = widget.get_attribute("data-sitekey")
        if not sitekey:
            raise RuntimeError("No Turnstile sitekey found")
        print(f"Sitekey received: {sitekey}")

        # STEP-03: Create and solve the proxyless Turnstile task.
        solution = client.solve(TurnstileTaskProxyless(websiteURL=URL, websiteKey=sitekey))
        # STEP-04: Put the token into this demo's response field.
        # Token injection and submission are site-specific; adapt this step to the target page.
        fill_response_field(driver, "cf-turnstile-response", solution["token"])
        print("Token sent")
        submit = wait_for_xpath(driver, SUBMIT_LOCATOR)
        driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", submit)
        try:
            submit.click()
        except ElementClickInterceptedException:
            # Some demo layouts leave the Turnstile iframe over the submit button.
            # Dispatch the same button click after confirming the intended element.
            print("Native click was intercepted; submitting with JavaScript")
            driver.execute_script("arguments[0].click();", submit)
        print("Pressed the Check button")
        # STEP-05: Require the page's success message after submission.
        show_success(driver)
        time.sleep(5)


if __name__ == "__main__":
    main()
