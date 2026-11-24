"""Solve reCAPTCHA v2 in a SeleniumBase browser session.

What it does:
    Extracts the widget site key, solves ``RecaptchaV2TaskProxyless``, injects the returned
    ``gRecaptchaResponse`` into the demo form, submits it, and checks page acceptance. No proxy
    is used; ``CaptchaClient.solve()`` creates the task and waits for its result.

To use this example on another page, change the target URL and verify the site key and any
challenge-specific parameters required by that page. Token fields, callbacks, submission, and
success indicators are site-specific, so inspect the page before applying the token.

How it works:
    STEP-01 - Start the browser and SDK client; the client reads CAPTCHA_API_KEY.
    STEP-02 - Open the page and extract the site key rendered by its widget.
    STEP-03 - Build the proxyless task and let solve() create and poll it.
    STEP-04 - Apply the token using this page's response field and submit the form.
    STEP-05 - Require the page's success message; receiving a token is not acceptance.
"""

import os
import time

from captcha_solver_api.tasks import RecaptchaV2TaskProxyless
from seleniumbase import Driver

from examples.common import (
    create_client,
    fill_response_field,
    logged_example,
    wait_for_css,
    wait_for_xpath,
)

URL = os.getenv("TARGET_URL") or "https://www.google.com/recaptcha/api2/demo"
SITEKEY_LOCATOR = "//*[@data-sitekey]"
SUBMIT_LOCATOR = "//*[@type='submit']"
SUCCESS_SELECTOR = ".recaptcha-success, p.successMessage"


@logged_example
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
        solution = client.solve(
            RecaptchaV2TaskProxyless(
                websiteURL=URL,
                websiteKey=sitekey,
                userAgent=driver.execute_script("return navigator.userAgent"),
            )
        )
        # STEP-04: Apply the token using this page's response field and submit the form.
        # Token injection and submission are site-specific; adapt this step to the target page.
        fill_response_field(driver, "g-recaptcha-response", solution["gRecaptchaResponse"])
        print("Token sent")
        wait_for_xpath(driver, SUBMIT_LOCATOR).click()
        print("Pressed the Check button")
        # STEP-05: Require the page's success message; receiving a token is not acceptance.
        print(wait_for_css(driver, SUCCESS_SELECTOR).text)
        time.sleep(5)


if __name__ == "__main__":
    main()
