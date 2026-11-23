"""Solve an image CAPTCHA with additional recognition hints.

What it does:
    Screenshots the CAPTCHA on TARGET_URL, creates ImageToTextTask with character and length
    hints, enters the recognized answer, submits the form, and checks acceptance.

How it works:
    STEP-01 starts browser/client. STEP-02 captures the image. STEP-03 adds hints and solves it.
    STEP-04 enters/submits the text. STEP-05 checks the page result.
"""

import time

from captcha_solver_api.tasks import ImageToTextTask
from seleniumbase import Driver

from examples.common import (
    create_client,
    logged_example,
    required_env,
    show_success,
    wait_for_xpath,
)

URL = required_env("TARGET_URL")
IMAGE_LOCATOR = "//img[contains(@class,'captchaImage')]"
ANSWER_LOCATOR = "//input[@id='simple-captcha-field']"
SUBMIT_LOCATOR = "//button[@type='submit']"


@logged_example
def main() -> None:
    # STEP-01: Start the browser and SDK client.
    with Driver(browser="chrome", headless=False) as driver, create_client() as client:
        # STEP-02: Open the page and capture the CAPTCHA image as Base64.
        driver.get(URL)
        image = wait_for_xpath(driver, IMAGE_LOCATOR).screenshot_as_base64
        # STEP-03: Add recognition hints when constructing the image task.
        task = ImageToTextTask(
            body=image,
            numeric=4,
            minLength=4,
            maxLength=10,
        )
        solution = client.solve(task)
        # STEP-04: Fill and submit the recognized answer.
        wait_for_xpath(driver, ANSWER_LOCATOR).send_keys(solution["text"])
        print("Entered the answer to the captcha")
        wait_for_xpath(driver, SUBMIT_LOCATOR).click()
        print("Pressed the Check button")
        # STEP-05: Verify the page accepted the answer.
        show_success(driver)
        time.sleep(5)


if __name__ == "__main__":
    main()
