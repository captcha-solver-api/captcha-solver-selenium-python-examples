"""Solve callback-based reCAPTCHA v2 using the same proxy as the browser."""

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
    with (
        Driver(browser="chrome", headless=False, cft=True, proxy=selenium_proxy()) as driver,
        create_client() as client,
    ):
        driver.get(URL)
        try:
            sitekey = wait_for_xpath(driver, SITEKEY_LOCATOR).get_attribute("data-sitekey")
        except TimeoutException as exc:
            raise RuntimeError(
                "The target page did not load through the configured proxy. "
                "Check the proxy address, credentials, and availability."
            ) from exc
        print("Got the callback function name and site key")
        solution = client.solve(
            RecaptchaV2Task(
                websiteURL=URL,
                websiteKey=sitekey,
                userAgent=driver.execute_script("return navigator.userAgent"),
                **proxy_settings(),
            )
        )
        driver.execute_script(
            "window.verifyDemoRecaptcha(arguments[0]);",
            solution["gRecaptchaResponse"],
        )
        print("The token is sent to the callback function")
        show_success(driver)
        time.sleep(5)


if __name__ == "__main__":
    main()
