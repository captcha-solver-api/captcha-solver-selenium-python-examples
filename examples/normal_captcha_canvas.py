"""Extract the demo image captcha through canvas and submit its solution."""

import time

from captcha_solver_api.tasks import ImageToTextTask
from common import (
    create_client,
    logged_example,
    required_env,
    show_success,
    wait_for_css,
    wait_for_xpath,
)
from seleniumbase import Driver

URL = required_env("TARGET_URL")
IMAGE_SELECTOR = "img[class*='captchaImage']"
ANSWER_LOCATOR = "//input[@id='simple-captcha-field']"
SUBMIT_LOCATOR = "//button[@type='submit']"

CANVAS_SCRIPT = """
const image = document.querySelector(arguments[0]);
const canvas = document.createElement('canvas');
canvas.width = image.naturalWidth || image.width;
canvas.height = image.naturalHeight || image.height;
canvas.getContext('2d').drawImage(image, 0, 0, canvas.width, canvas.height);
return canvas.toDataURL('image/png').split(',', 2)[1];
"""


@logged_example
def main() -> None:
    # STEP-01: Start the browser and SDK client.
    with Driver(browser="chrome", headless=False) as driver, create_client() as client:
        # STEP-02: Open the page and copy the rendered CAPTCHA pixels through a canvas.
        driver.get(URL)
        wait_for_css(driver, IMAGE_SELECTOR)
        image = driver.execute_script(CANVAS_SCRIPT, IMAGE_SELECTOR)
        # STEP-03: Create the image task and wait for recognized text.
        task = ImageToTextTask(body=image)
        solution = client.solve(task)
        # STEP-04: Fill and submit the answer using this demo's controls.
        wait_for_xpath(driver, ANSWER_LOCATOR).send_keys(solution["text"])
        print("Entered the answer to the captcha")
        wait_for_xpath(driver, SUBMIT_LOCATOR).click()
        print("Pressed the Check button")
        # STEP-05: Verify the page accepted the submitted answer.
        show_success(driver)
        time.sleep(5)


if __name__ == "__main__":
    main()
