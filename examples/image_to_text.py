"""Screenshot an image captcha, solve it, and fill its answer field."""

import time

from captcha_solver_api.tasks import ImageToTextTask
from common import create_client, logged_example, required_env, show_success, wait_for_xpath
from seleniumbase import Driver

URL = required_env("TARGET_URL")
IMAGE_LOCATOR = "//img[contains(@class,'captchaImage')]"
ANSWER_LOCATOR = "//input[@id='simple-captcha-field']"
SUBMIT_LOCATOR = "//button[@type='submit']"


@logged_example
def main() -> None:
    with Driver(browser="chrome", headless=False) as driver, create_client() as client:
        driver.get(URL)
        captcha = wait_for_xpath(driver, IMAGE_LOCATOR)
        solution = client.solve(ImageToTextTask(body=captcha.screenshot_as_base64))
        wait_for_xpath(driver, ANSWER_LOCATOR).send_keys(solution["text"])
        print("Entered the answer to the captcha")
        wait_for_xpath(driver, SUBMIT_LOCATOR).click()
        print("Pressed the Check button")
        show_success(driver)
        time.sleep(5)


if __name__ == "__main__":
    main()
