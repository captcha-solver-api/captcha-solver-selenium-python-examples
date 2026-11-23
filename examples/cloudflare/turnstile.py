"""Solve a standalone Cloudflare Turnstile widget.

What it does:
    Extracts the widget site key from TARGET_URL, solves TurnstileTaskProxyless, inserts the
    returned token into the page response field, submits the form, and checks acceptance.

How it works:
    STEP-01 starts browser/client. STEP-02 extracts the site key. STEP-03 solves the SDK task.
    STEP-04 submits the token. STEP-05 requires the page's success message.
"""

import time

from captcha_solver_api.tasks import TurnstileTaskProxyless
from seleniumbase import Driver

from examples.common import (
    create_client,
    fill_response_field,
    logged_example,
    required_env,
    show_success,
    wait_for_xpath,
)

URL = required_env("TARGET_URL")
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
        task = TurnstileTaskProxyless(websiteURL=URL, websiteKey=sitekey)
        solution = client.solve(task)
        # STEP-04: Put the token into this demo's response field.
        # Token injection and submission are site-specific; adapt this step to the target page.
        fill_response_field(driver, "cf-turnstile-response", solution["token"])
        print("Token sent")
        wait_for_xpath(driver, SUBMIT_LOCATOR).click()
        print("Pressed the Check button")
        # STEP-05: Require the page's success message after submission.
        show_success(driver)
        time.sleep(5)


if __name__ == "__main__":
    main()
