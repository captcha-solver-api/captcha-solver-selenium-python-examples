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
    with Driver(browser="chrome", headless=False) as driver, create_client() as client:
        driver.get(URL)
        widget = wait_for_xpath(driver, SITEKEY_LOCATOR)
        sitekey = widget.get_attribute("data-sitekey")
        if not sitekey:
            raise RuntimeError("No Turnstile sitekey found")
        print(f"Sitekey received: {sitekey}")

        solution = client.solve(TurnstileTaskProxyless(websiteURL=URL, websiteKey=sitekey))
        fill_response_field(driver, "cf-turnstile-response", solution["token"])
        print("Token sent")
        wait_for_xpath(driver, SUBMIT_LOCATOR).click()
        print("Pressed the Check button")
        show_success(driver)
        time.sleep(5)


if __name__ == "__main__":
    main()
