"""Solve reCAPTCHA v2 in a SeleniumBase browser session."""

import os
import time

from captcha_solver_api.tasks import RecaptchaV2TaskProxyless
from common import (
    click_optional,
    create_client,
    fill_response_field,
    required_env,
    wait_for_css,
)
from seleniumbase import Driver


def main() -> None:
    target_url = required_env("TARGET_URL")
    captcha_selector = os.getenv("CAPTCHA_SELECTOR", ".g-recaptcha[data-sitekey]")

    with Driver(browser="chrome", headless=False) as driver, create_client() as client:
        driver.get(target_url)
        widget = wait_for_css(driver, captcha_selector)
        sitekey = widget.get_attribute("data-sitekey")
        if not sitekey:
            raise RuntimeError(f"No data-sitekey found on {captcha_selector}")

        solution = client.solve(
            RecaptchaV2TaskProxyless(
                websiteURL=driver.current_url,
                websiteKey=sitekey,
                userAgent=driver.execute_script("return navigator.userAgent"),
            )
        )
        fill_response_field(driver, "g-recaptcha-response", solution["gRecaptchaResponse"])
        click_optional(driver, os.getenv("SUBMIT_SELECTOR"))
        time.sleep(5)


if __name__ == "__main__":
    main()
