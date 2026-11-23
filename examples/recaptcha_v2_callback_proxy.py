"""Solve callback-based reCAPTCHA v2 using the same proxy as the browser.

What it does:
    Opens TARGET_URL through a proxy, extracts the site key, solves RecaptchaV2Task through the
    same proxy, passes its token to a known callback, and checks page acceptance.

How it works:
    STEP-01 configures browser/client. STEP-02 reads the site key. STEP-03 solves the proxied
    task. STEP-04 invokes the callback. STEP-05 verifies the page result.
"""

import time

from captcha_solver_api.tasks import RecaptchaV2Task
from common import (
    create_client,
    logged_example,
    proxy_settings,
    required_env,
    selenium_proxy,
    show_success,
    wait_for_xpath,
)
from selenium.common.exceptions import TimeoutException
from seleniumbase import Driver

URL = required_env("TARGET_URL")
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
        task = RecaptchaV2Task(
            websiteURL=URL,
            websiteKey=sitekey,
            userAgent=driver.execute_script("return navigator.userAgent"),
            **proxy_settings(),
        )
        solution = client.solve(task)
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
