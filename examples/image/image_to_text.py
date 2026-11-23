"""Screenshot an image CAPTCHA, solve it, and fill its answer field.

What it does:
    Captures the CAPTCHA element on IMAGE_CAPTCHA_TARGET_URL, solves ImageToTextTask without a proxy, enters
    the recognized text, submits the form, and checks that the page accepted it.

To use this example on another page, change its type-specific target URL and inspect the
site key or challenge parameters, solution fields or callbacks, submission controls, and exact success
signal before applying the result.

How it works:
    STEP-01 - starts browser/client.
    STEP-02 - captures Base64 pixels.
    STEP-03 - solves the image task.
    STEP-04 - enters/submits the text.
    STEP-05 - checks the page result.
"""

import os
from pathlib import Path

from captcha_solver_api import CaptchaClient
from captcha_solver_api.tasks import ImageToTextTask
from dotenv import load_dotenv
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from seleniumbase import Driver

REPOSITORY_ROOT = Path(__file__).resolve().parents[2]
load_dotenv(REPOSITORY_ROOT / ".env")


def required_env(name: str) -> str:
    """Return a required environment value or explain how to configure it."""
    value = os.getenv(name)
    if not value:
        raise RuntimeError(f"Set {name} in the environment or .env file")
    return value


def create_client() -> CaptchaClient:
    """Create the SDK client with CAPTCHA_API_KEY."""
    return CaptchaClient(required_env("CAPTCHA_API_KEY"))


def wait_for_xpath(driver, locator: str, timeout: int = 30):
    """Wait until a target-specific XPath is visible and enabled."""
    return WebDriverWait(driver, timeout).until(EC.element_to_be_clickable((By.XPATH, locator)))


def show_success(driver) -> None:
    """Require the exact target-specific success text configured by the user."""
    expected_text = required_env("CAPTCHA_SUCCESS_TEXT")
    WebDriverWait(driver, 30).until(
        EC.text_to_be_present_in_element((By.TAG_NAME, "body"), expected_text)
    )
    print(f"Page confirmation: {expected_text}")


URL = required_env("IMAGE_CAPTCHA_TARGET_URL")
IMAGE_LOCATOR = "//img[contains(@class,'captchaImage')]"
ANSWER_LOCATOR = "//input[@id='simple-captcha-field']"
SUBMIT_LOCATOR = "//button[@type='submit']"


def main() -> None:
    # STEP-01: Start the browser and SDK client.
    with Driver(browser="chrome", headless=False) as driver, create_client() as client:
        # STEP-02: Open the page and capture only the CAPTCHA image as Base64.
        driver.get(URL)
        captcha = wait_for_xpath(driver, IMAGE_LOCATOR)
        # STEP-03: Create the image task and wait for recognized text.
        task = ImageToTextTask(body=captcha.screenshot_as_base64)
        solution = client.solve(task)
        print("Recognized text:", solution["text"])
        # STEP-04: Enter the returned text and submit this demo's form.
        wait_for_xpath(driver, ANSWER_LOCATOR).send_keys(solution["text"])
        print("Entered the answer to the captcha")
        wait_for_xpath(driver, SUBMIT_LOCATOR).click()
        print("Pressed the Check button")
        # STEP-05: Verify the page accepted the answer.
        show_success(driver)


if __name__ == "__main__":
    main()
