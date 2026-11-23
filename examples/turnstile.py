"""Solve a standalone Cloudflare Turnstile widget."""

import time

from captcha_solver_api.tasks import TurnstileTaskProxyless
from common import (
    create_client,
    fill_response_field,
    logged_example,
    required_env,
    show_success,
    wait_for_xpath,
)
from seleniumbase import Driver

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
        solution = client.solve(TurnstileTaskProxyless(websiteURL=URL, websiteKey=sitekey))
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
