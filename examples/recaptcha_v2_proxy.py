"""Solve reCAPTCHA v2 with the same proxy in the browser and API task."""

import time

from captcha_solver_api.tasks import RecaptchaV2Task
from common import (
    create_client,
    fill_response_field,
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
SUBMIT_LOCATOR = "//button[@data-action='demo_action']"


@logged_example
def main() -> None:
    # STEP-01: Start browser and SDK client with one shared proxy configuration.
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
        print(f"Sitekey received: {sitekey}")
        # STEP-03: Create the proxied task with the browser's User-Agent.
        task = RecaptchaV2Task(
            websiteURL=URL,
            websiteKey=sitekey,
            userAgent=driver.execute_script("return navigator.userAgent"),
            **proxy_settings(),
        )
        solution = client.solve(task)
        # STEP-04: Apply the token and submit this page's form.
        # Token injection and submission are site-specific; adapt this step to the target page.
        fill_response_field(driver, "g-recaptcha-response", solution["gRecaptchaResponse"])
        print("Token sent")
        wait_for_xpath(driver, SUBMIT_LOCATOR).click()
        print("Pressed the Check button")
        # STEP-05: Require the page's success message.
        show_success(driver)
        time.sleep(5)


if __name__ == "__main__":
    main()
