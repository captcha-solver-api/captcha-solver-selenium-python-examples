"""Solve Yandex SmartCaptcha on the official demo with SeleniumBase."""

import os

from captcha_solver_api.tasks import YandexSmartCaptchaTaskProxyless
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from seleniumbase import Driver

from examples.common import (
    create_client,
    fill_response_field,
    logged_example,
    wait_for_css,
    wait_for_xpath,
)

URL = os.getenv("TARGET_URL") or "https://captcha-api.yandex.ru/demo"
SITEKEY_SELECTOR = ".smart-captcha[data-sitekey]"
SUBMIT_LOCATOR = "//*[@id='smartcaptcha-demo-submit']"
SUCCESS_TEXT = "Hello, user!"


@logged_example
def main() -> None:
    # STEP-01: Start the browser and SDK client.
    with Driver(browser="chrome", headless=False) as driver, create_client() as client:
        # STEP-02: Read the public widget key from the page opened in this browser.
        # Read the public widget key from the page opened in this browser.
        driver.get(URL)
        widget = wait_for_css(driver, SITEKEY_SELECTOR)
        sitekey = widget.get_attribute("data-sitekey")
        if not sitekey:
            raise RuntimeError("No Yandex SmartCaptcha sitekey found")
        print(f"Sitekey received: {sitekey}")

        # STEP-03: Create the task; solve() submits it and waits for its solution.
        # The SDK creates the task and waits for its solution.
        solution = client.solve(
            YandexSmartCaptchaTaskProxyless(
                websiteURL=driver.current_url,
                websiteKey=sitekey,
                userAgent=driver.execute_script("return navigator.userAgent"),
            ),
            timeout=180,
        )
        token = solution.get("token")
        if not isinstance(token, str) or not token.strip():
            raise RuntimeError("Captcha Solver returned an empty SmartCaptcha token")

        # STEP-04: Token injection and submission are site-specific; adapt this step.
        # Token injection and submission are site-specific; adapt this step to the target page.
        # This demo submits the token through a hidden form field.
        wait_for_css(driver, 'input[name="smart-token"]')
        fill_response_field(driver, "smart-token", token)
        print("Token sent")
        wait_for_xpath(driver, SUBMIT_LOCATOR).click()
        print("Submitted the form")

        # STEP-05: Confirm acceptance by the site, not just receipt of an API token.
        # Confirm acceptance by the site, not just receipt of an API token.
        WebDriverWait(driver, 30).until(
            EC.text_to_be_present_in_element((By.TAG_NAME, "body"), SUCCESS_TEXT)
        )
        print(f"SUCCESS: the site accepted the token and returned '{SUCCESS_TEXT}'.")


if __name__ == "__main__":
    main()
