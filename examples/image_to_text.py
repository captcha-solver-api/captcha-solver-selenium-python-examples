"""Screenshot an image captcha, solve it, and fill its answer field."""

import os
import time

from captcha_solver_api.tasks import ImageToTextTask
from common import click_optional, create_client, required_env, wait_for_css
from seleniumbase import Driver


def main() -> None:
    target_url = required_env("TARGET_URL")
    captcha_selector = os.getenv("CAPTCHA_SELECTOR", "img.captcha")
    answer_selector = os.getenv("ANSWER_SELECTOR", 'input[name="captcha-answer"]')

    with Driver(browser="chrome", headless=False) as driver, create_client() as client:
        driver.get(target_url)
        captcha = wait_for_css(driver, captcha_selector)
        solution = client.solve(ImageToTextTask(body=captcha.screenshot_as_base64))
        wait_for_css(driver, answer_selector).send_keys(solution["text"])
        click_optional(driver, os.getenv("SUBMIT_SELECTOR"))
        time.sleep(5)


if __name__ == "__main__":
    main()
