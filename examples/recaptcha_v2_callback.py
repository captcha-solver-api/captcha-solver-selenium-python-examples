"""Solve reCAPTCHA v2 and invoke the callback known by the demo page."""

import time

from captcha_solver_api.tasks import RecaptchaV2TaskProxyless
from common import create_client, show_success, wait_for_xpath
from seleniumbase import Driver

URL = "https://2captcha.com/demo/recaptcha-v2-callback"
SITEKEY_LOCATOR = "//div[@id='g-recaptcha']"


def main() -> None:
    with Driver(browser="chrome", headless=False) as driver, create_client() as client:
        driver.get(URL)
        sitekey = wait_for_xpath(driver, SITEKEY_LOCATOR).get_attribute("data-sitekey")
        solution = client.solve(RecaptchaV2TaskProxyless(websiteURL=URL, websiteKey=sitekey))
        driver.execute_script(
            "window.verifyDemoRecaptcha(arguments[0]);",
            solution["gRecaptchaResponse"],
        )
        show_success(driver)
        time.sleep(5)


if __name__ == "__main__":
    main()
