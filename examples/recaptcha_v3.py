"""Request and apply a reCAPTCHA v3 token."""

import os
import time

from captcha_solver_api.tasks import RecaptchaV3TaskProxyless
from common import click_optional, create_client, fill_response_field, required_env
from seleniumbase import Driver


def main() -> None:
    target_url = required_env("TARGET_URL")
    website_key = required_env("WEBSITE_KEY")
    page_action = os.getenv("PAGE_ACTION", "submit")
    min_score = float(os.getenv("MIN_SCORE", "0.3"))

    with Driver(browser="chrome", headless=False) as driver, create_client() as client:
        driver.get(target_url)
        solution = client.solve(
            RecaptchaV3TaskProxyless(
                websiteURL=driver.current_url,
                websiteKey=website_key,
                minScore=min_score,
                pageAction=page_action,
            )
        )
        fill_response_field(driver, "g-recaptcha-response", solution["gRecaptchaResponse"])
        click_optional(driver, os.getenv("SUBMIT_SELECTOR"))
        time.sleep(5)


if __name__ == "__main__":
    main()
