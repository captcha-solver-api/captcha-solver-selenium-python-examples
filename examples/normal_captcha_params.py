"""Solve the demo image captcha with additional recognition hints."""

import time

from captcha_solver_api.tasks import ImageToTextTask
from common import create_client, show_success, wait_for_xpath
from seleniumbase import Driver

URL = "https://2captcha.com/demo/normal"
IMAGE_LOCATOR = "//img[contains(@class,'captchaImage')]"
ANSWER_LOCATOR = "//input[@id='simple-captcha-field']"
SUBMIT_LOCATOR = "//button[@type='submit']"


def main() -> None:
    with Driver(browser="chrome", headless=False) as driver, create_client() as client:
        driver.get(URL)
        image = wait_for_xpath(driver, IMAGE_LOCATOR).screenshot_as_base64
        solution = client.solve(
            ImageToTextTask(
                body=image,
                numeric=4,
                minLength=4,
                maxLength=10,
            )
        )
        wait_for_xpath(driver, ANSWER_LOCATOR).send_keys(solution["text"])
        wait_for_xpath(driver, SUBMIT_LOCATOR).click()
        show_success(driver)
        time.sleep(5)


if __name__ == "__main__":
    main()
