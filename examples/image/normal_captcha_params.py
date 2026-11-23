"""Solve an image CAPTCHA with additional recognition hints.

What it does:
    Screenshots the CAPTCHA on IMAGE_CAPTCHA_TARGET_URL, creates ImageToTextTask with character and length
    hints, enters the recognized answer, submits the form, and checks acceptance.

To use this example on another page, change its type-specific target URL and inspect the
site key or challenge parameters, solution fields or callbacks, submission controls, and exact success
signal before applying the result.

How it works:
    STEP-01 - starts browser/client.
    STEP-02 - captures the image.
    STEP-03 - adds hints and solves it.
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
    return CaptchaClient(required_env("CAPTCHA_API_KEY"), debug=True)


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
    print("\n[STEP-01] Start the browser and SDK client.", flush=True)
    with Driver(browser="chrome", headless=False) as driver, create_client() as client:
        # STEP-02: Open the page and capture the CAPTCHA image as Base64.
        print("\n[STEP-02] Open the page and capture the CAPTCHA image as Base64.", flush=True)
        driver.get(URL)
        image = wait_for_xpath(driver, IMAGE_LOCATOR).screenshot_as_base64
        # STEP-03: Add recognition hints when constructing the image task.
        print("\n[STEP-03] Add recognition hints when constructing the image task.", flush=True)
        task = ImageToTextTask(
            body=image,
            numeric=4,
            minLength=4,
            maxLength=10,
        )
        solution = client.solve(task)
        print("Recognized text:", solution["text"])
        # STEP-04: Fill and submit the recognized answer.
        print("\n[STEP-04] Fill and submit the recognized answer.", flush=True)
        wait_for_xpath(driver, ANSWER_LOCATOR).send_keys(solution["text"])
        print("Entered the answer to the captcha")
        wait_for_xpath(driver, SUBMIT_LOCATOR).click()
        print("Pressed the Check button")
        # STEP-05: Verify the page accepted the answer.
        print("\n[STEP-05] Verify the page accepted the answer.", flush=True)
        show_success(driver)


if __name__ == "__main__":
    main()
