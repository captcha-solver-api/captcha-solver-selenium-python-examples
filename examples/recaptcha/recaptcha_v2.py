"""Solve reCAPTCHA v2 in a SeleniumBase browser session.

What it does:
    Opens the official demo or TARGET_URL without a proxy, extracts the widget site key, solves
    RecaptchaV2TaskProxyless, injects the token, submits the form, and checks page acceptance.

How it works:
    STEP-01 starts the browser/client. STEP-02 reads the site key. STEP-03 creates and solves the
    SDK task. STEP-04 submits the token. STEP-05 requires the page's success message.
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
        task = RecaptchaV2TaskProxyless(
            websiteURL=URL,
            websiteKey=sitekey,
            userAgent=driver.execute_script("return navigator.userAgent"),
        )
        solution = client.solve(task)
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
