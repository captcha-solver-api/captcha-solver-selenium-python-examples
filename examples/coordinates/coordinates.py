"""Solve a coordinate CAPTCHA and click the returned image positions.

What it does:
    Captures a click CAPTCHA from COORDINATES_TARGET_URL, solves CoordinatesTask without a proxy, scales the
    returned source-image points to the rendered element, clicks them, and checks acceptance.

To use this example on another page, change its type-specific target URL and inspect the
site key or challenge parameters, solution fields or callbacks, submission controls, and exact success
signal before applying the result.

How it works:
    STEP-01 - starts browser/client.
    STEP-02 - captures pixels/dimensions.
    STEP-03 - solves the task.
    STEP-04 - scales and clicks its points.
    STEP-05 - submits and checks the page result.
"""

import base64
import os
import struct
from pathlib import Path

from captcha_solver_api import CaptchaClient
from captcha_solver_api.tasks import CoordinatesTask
from dotenv import load_dotenv
from selenium.webdriver import ActionChains
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


URL = required_env("COORDINATES_TARGET_URL")
IMAGE_SELECTOR = "img[alt='clickcaptcha example']"
SUBMIT_LOCATOR = "//button[@type='submit']"

CANVAS_SCRIPT = """
const image = document.querySelector(arguments[0]);
const canvas = document.createElement('canvas');
canvas.width = image.naturalWidth;
canvas.height = image.naturalHeight;
canvas.getContext('2d').drawImage(image, 0, 0);
return canvas.toDataURL('image/png').split(',', 2)[1];
"""


def png_size(png_base64: str):
    image = base64.b64decode(png_base64)
    return struct.unpack(">II", image[16:24])


def main() -> None:
    # STEP-01: Start the browser and SDK client.
    print("\n[STEP-01] Start the browser and SDK client.", flush=True)
    with Driver(browser="chrome", headless=False) as driver, create_client() as client:
        # STEP-02: Capture the source pixels and dimensions of the rendered click CAPTCHA.
        print(
            "\n[STEP-02] Capture the source pixels and dimensions of the rendered click CAPTCHA.",
            flush=True,
        )
        driver.get(URL)
        captcha = wait_for_css(driver, IMAGE_SELECTOR)
        image = driver.execute_script(CANVAS_SCRIPT, IMAGE_SELECTOR)
        image_width, image_height = png_size(image)
        # STEP-03: Create the coordinate task and wait for image-space click points.
        print(
            "\n[STEP-03] Create the coordinate task and wait for image-space click points.",
            flush=True,
        )
        task = CoordinatesTask(body=image)
        solution = client.solve(task)
        print("Ordered click coordinates:", solution["coordinates"])

        # STEP-04: Scale source-image points to the displayed element before clicking.

        print(
            "\n[STEP-04] Scale source-image points to the displayed element before clicking.",
            flush=True,
        )
        scale_x = captcha.size["width"] / image_width
        scale_y = captcha.size["height"] / image_height
        print(
            "Image size:",
            (image_width, image_height),
            "displayed size:",
            (captcha.size["width"], captcha.size["height"]),
            "coordinates:",
            solution["coordinates"],
        )
        print("The received response is converted into a list of coordinates")
        for point in solution["coordinates"]:
            ActionChains(driver).move_to_element_with_offset(
                captcha,
                point["x"] * scale_x - captcha.size["width"] / 2,
                point["y"] * scale_y - captcha.size["height"] / 2,
            ).click().perform()
        print("The coordinates are marked on the image")

        submit = wait_for_xpath(driver, SUBMIT_LOCATOR)
        driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", submit)
        driver.execute_script("arguments[0].click();", submit)
        print("Pressed the Check button")
        # STEP-05: Submit the clicks and require the page's success message.
        print("\n[STEP-05] Submit the clicks and require the page's success message.", flush=True)
        show_success(driver)


if __name__ == "__main__":
    main()
