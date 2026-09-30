"""Solve a coordinate captcha and click the returned image positions."""

import base64
import os
import struct
import time

from captcha_solver_api.tasks import CoordinatesTask
from common import click_optional, create_client, required_env, wait_for_css
from selenium.webdriver import ActionChains
from seleniumbase import Driver


def png_size(png_base64: str):
    image = base64.b64decode(png_base64)
    return struct.unpack(">II", image[16:24])


def main() -> None:
    target_url = required_env("TARGET_URL")
    captcha_selector = os.getenv("CAPTCHA_SELECTOR", "img.captcha")
    instruction = required_env("CAPTCHA_INSTRUCTION")

    with Driver(browser="chrome", headless=False) as driver, create_client() as client:
        driver.get(target_url)
        captcha = wait_for_css(driver, captcha_selector)
        screenshot = captcha.screenshot_as_base64
        image_width, image_height = png_size(screenshot)
        solution = client.solve(CoordinatesTask(body=screenshot, comment=instruction))

        scale_x = captcha.size["width"] / image_width
        scale_y = captcha.size["height"] / image_height
        for point in solution["coordinates"]:
            ActionChains(driver).move_to_element_with_offset(
                captcha,
                point["x"] * scale_x,
                point["y"] * scale_y,
            ).click().perform()

        click_optional(driver, os.getenv("SUBMIT_SELECTOR"))
        time.sleep(5)


if __name__ == "__main__":
    main()
