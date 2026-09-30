"""Solve reCAPTCHA v2 with the same proxy in the browser and API task."""

import time

from captcha_solver_api.tasks import RecaptchaV2Task
from common import (
    create_client,
    fill_response_field,
    proxy_settings,
    selenium_proxy,
    show_success,
    wait_for_xpath,
)
from selenium.common.exceptions import TimeoutException
from seleniumbase import Driver

URL = "https://2captcha.com/demo/recaptcha-v2"
SITEKEY_LOCATOR = "//div[@id='g-recaptcha']"
SUBMIT_LOCATOR = "//button[@data-action='demo_action']"


def main() -> None:
    with (
        Driver(browser="chrome", headless=False, proxy=selenium_proxy()) as driver,
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
        solution = client.solve(
            RecaptchaV2Task(
                websiteURL=URL,
                websiteKey=sitekey,
                userAgent=driver.execute_script("return navigator.userAgent"),
                **proxy_settings(),
            )
        )
        fill_response_field(driver, "g-recaptcha-response", solution["gRecaptchaResponse"])
        wait_for_xpath(driver, SUBMIT_LOCATOR).click()
        show_success(driver)
        time.sleep(5)


if __name__ == "__main__":
    main()
