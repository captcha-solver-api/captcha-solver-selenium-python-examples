"""Solve reCAPTCHA v2 and invoke the callback known by the demo page."""

import time

from captcha_solver_api.tasks import RecaptchaV2TaskProxyless
from common import create_client, logged_example, required_env, show_success, wait_for_xpath
from seleniumbase import Driver

URL = required_env("TARGET_URL")
SITEKEY_LOCATOR = "//div[@id='g-recaptcha']"


@logged_example
def main() -> None:
    with Driver(browser="chrome", headless=False) as driver, create_client() as client:
        driver.get(URL)
        sitekey = wait_for_xpath(driver, SITEKEY_LOCATOR).get_attribute("data-sitekey")
        print(f"Sitekey received: {sitekey}")
        solution = client.solve(RecaptchaV2TaskProxyless(websiteURL=URL, websiteKey=sitekey))
        driver.execute_script(
            "window.verifyDemoRecaptcha(arguments[0]);",
            solution["gRecaptchaResponse"],
        )
        print("The token is sent to the callback function")
        show_success(driver)
        time.sleep(5)


if __name__ == "__main__":
    main()
