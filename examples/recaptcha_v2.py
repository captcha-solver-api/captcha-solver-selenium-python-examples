"""Solve reCAPTCHA v2 in a SeleniumBase browser session."""

import os
import time

from captcha_solver_api.tasks import RecaptchaV2TaskProxyless
from common import (
    create_client,
    fill_response_field,
    logged_example,
    wait_for_css,
    wait_for_xpath,
)
from seleniumbase import Driver

URL = os.getenv("TARGET_URL") or "https://www.google.com/recaptcha/api2/demo"
SITEKEY_LOCATOR = "//*[@data-sitekey]"
SUBMIT_LOCATOR = "//*[@type='submit']"
SUCCESS_SELECTOR = ".recaptcha-success, p.successMessage"


@logged_example
def main() -> None:
    with Driver(browser="chrome", headless=False) as driver, create_client() as client:
        driver.get(URL)
        widget = wait_for_xpath(driver, SITEKEY_LOCATOR)
        sitekey = widget.get_attribute("data-sitekey")
        if not sitekey:
            raise RuntimeError("No reCAPTCHA sitekey found")
        print(f"Sitekey received: {sitekey}")

        solution = client.solve(
            RecaptchaV2TaskProxyless(
                websiteURL=URL,
                websiteKey=sitekey,
                userAgent=driver.execute_script("return navigator.userAgent"),
            )
        )
        fill_response_field(driver, "g-recaptcha-response", solution["gRecaptchaResponse"])
        print("Token sent")
        wait_for_xpath(driver, SUBMIT_LOCATOR).click()
        print("Pressed the Check button")
        print(wait_for_css(driver, SUCCESS_SELECTOR).text)
        time.sleep(5)


if __name__ == "__main__":
    main()
