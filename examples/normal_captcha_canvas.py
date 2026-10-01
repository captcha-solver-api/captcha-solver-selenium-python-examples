"""Extract the demo image captcha through canvas and submit its solution."""

import time

from captcha_solver_api.tasks import ImageToTextTask
from common import create_client, required_env, show_success, wait_for_css, wait_for_xpath
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


def main() -> None:
    with Driver(browser="chrome", headless=False) as driver, create_client() as client:
        driver.get(URL)
        wait_for_css(driver, IMAGE_SELECTOR)
        image = driver.execute_script(CANVAS_SCRIPT, IMAGE_SELECTOR)
        solution = client.solve(ImageToTextTask(body=image))
        wait_for_xpath(driver, ANSWER_LOCATOR).send_keys(solution["text"])
        wait_for_xpath(driver, SUBMIT_LOCATOR).click()
        show_success(driver)
        time.sleep(5)


if __name__ == "__main__":
    main()
