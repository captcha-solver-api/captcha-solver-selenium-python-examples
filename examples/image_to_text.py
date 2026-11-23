"""Screenshot an image CAPTCHA, solve it, and fill its answer field.

What it does:
    Captures the CAPTCHA element on TARGET_URL, solves ImageToTextTask without a proxy, enters
    the recognized text, submits the form, and checks that the page accepted it.

How it works:
    STEP-01 starts browser/client. STEP-02 captures Base64 pixels. STEP-03 solves the image task.
    STEP-04 enters/submits the text. STEP-05 checks the page result.
"""

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
    # STEP-01: Start the browser and SDK client.
    with Driver(browser="chrome", headless=False) as driver, create_client() as client:
        # STEP-02: Open the page and capture only the CAPTCHA image as Base64.
        driver.get(URL)
        captcha = wait_for_xpath(driver, IMAGE_LOCATOR)
        # STEP-03: Create the image task and wait for recognized text.
        task = ImageToTextTask(body=captcha.screenshot_as_base64)
        solution = client.solve(task)
        # STEP-04: Enter the returned text and submit this demo's form.
        wait_for_xpath(driver, ANSWER_LOCATOR).send_keys(solution["text"])
        print("Entered the answer to the captcha")
        wait_for_xpath(driver, SUBMIT_LOCATOR).click()
        print("Pressed the Check button")
        # STEP-05: Verify the page accepted the answer.
        show_success(driver)
        time.sleep(5)


if __name__ == "__main__":
    main()
