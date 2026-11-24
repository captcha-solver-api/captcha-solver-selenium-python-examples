"""Screenshot an image CAPTCHA, solve it, and fill its answer field.

What it does:
    Captures only the CAPTCHA element as Base64, sends it in an ``ImageToTextTask`` without a
    proxy, enters the recognized text into the form, and checks that the page accepts it. It
    uses ``CaptchaClient.solve()`` to submit the task and wait for the result.

To use this example on another page, change the target URL and update the CAPTCHA image,
answer field, submit control, and success indicator. These selectors and the answer format are
site-specific.

How it works:
    STEP-01 - Start the browser and SDK client.
    STEP-02 - Open the page and capture only the CAPTCHA image as Base64.
    STEP-03 - Create the image task and wait for recognized text.
    STEP-04 - Enter the returned text and submit this demo's form.
    STEP-05 - Verify the page accepted the answer.
"""

import sys
import time
from pathlib import Path

from captcha_solver_api.tasks import ImageToTextTask
from seleniumbase import Driver

if __package__ in {None, ""}:
    sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from examples.common import (  # noqa: E402
    create_client,
    logged_example,
    required_env,
    show_success,
    wait_for_xpath,
)

URL = required_env("IMAGE_TARGET_URL", "TARGET_URL")
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
        solution = client.solve(ImageToTextTask(body=captcha.screenshot_as_base64))
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
