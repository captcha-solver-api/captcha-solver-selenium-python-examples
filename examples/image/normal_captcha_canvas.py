"""Extract an image CAPTCHA through canvas and submit its solution.

What it does:
    Copies rendered CAPTCHA pixels from IMAGE_CAPTCHA_TARGET_URL into a canvas, solves ImageToTextTask without
    a proxy, fills the recognized text, submits the form, and checks acceptance.

To use this example on another page, change its type-specific target URL and inspect the
site key or challenge parameters, solution fields or callbacks, submission controls, and exact success
signal before applying the result.

How it works:
    STEP-01 - starts browser/client.
    STEP-02 - extracts Base64 pixels.
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


def wait_for_css(driver, selector: str, timeout: int = 30):
    """Wait until a target-specific CSS selector exists."""
    return WebDriverWait(driver, timeout).until(
        EC.presence_of_element_located((By.CSS_SELECTOR, selector))
    )


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
        print("Recognized text:", solution["text"])
        # STEP-04: Fill and submit the answer using this demo's controls.
        wait_for_xpath(driver, ANSWER_LOCATOR).send_keys(solution["text"])
        print("Entered the answer to the captcha")
        wait_for_xpath(driver, SUBMIT_LOCATOR).click()
        print("Pressed the Check button")
        # STEP-05: Verify the page accepted the submitted answer.
        show_success(driver)


if __name__ == "__main__":
    main()
