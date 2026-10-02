"""Solve a coordinate captcha and click the returned image positions."""

import base64
import struct
import time

from captcha_solver_api.tasks import CoordinatesTask
from common import (
    create_client,
    logged_example,
    required_env,
    show_success,
    wait_for_css,
    wait_for_xpath,
)
from selenium.webdriver import ActionChains
from seleniumbase import Driver

URL = required_env("TARGET_URL")
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


@logged_example
def main() -> None:
    with Driver(browser="chrome", headless=False) as driver, create_client() as client:
        driver.get(URL)
        captcha = wait_for_css(driver, IMAGE_SELECTOR)
        image = driver.execute_script(CANVAS_SCRIPT, IMAGE_SELECTOR)
        image_width, image_height = png_size(image)
        solution = client.solve(CoordinatesTask(body=image))

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
        show_success(driver)
        time.sleep(5)


if __name__ == "__main__":
    main()
