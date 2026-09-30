"""Solve a coordinate captcha and click the returned image positions."""

import base64
import struct
import time

from captcha_solver_api.tasks import CoordinatesTask
from common import create_client, show_success, wait_for_css, wait_for_xpath
from selenium.webdriver import ActionChains
from seleniumbase import Driver

URL = "https://2captcha.com/demo/clickcaptcha"
IMAGE_SELECTOR = "img[alt='clickcaptcha example']"
SUBMIT_LOCATOR = "//button[@type='submit']"


def png_size(png_base64: str):
    image = base64.b64decode(png_base64)
    return struct.unpack(">II", image[16:24])


def main() -> None:
    with Driver(browser="chrome", headless=False) as driver, create_client() as client:
        driver.get(URL)
        captcha = wait_for_css(driver, IMAGE_SELECTOR)
        screenshot = captcha.screenshot_as_base64
        image_width, image_height = png_size(screenshot)
        solution = client.solve(CoordinatesTask(body=screenshot))

        scale_x = captcha.size["width"] / image_width
        scale_y = captcha.size["height"] / image_height
        for point in solution["coordinates"]:
            ActionChains(driver).move_to_element_with_offset(
                captcha,
                point["x"] * scale_x,
                point["y"] * scale_y,
            ).click().perform()

        wait_for_xpath(driver, SUBMIT_LOCATOR).click()
        show_success(driver)
        time.sleep(5)


if __name__ == "__main__":
    main()
