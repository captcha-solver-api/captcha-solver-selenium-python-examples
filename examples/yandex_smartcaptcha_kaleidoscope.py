"""Solve a Yandex SmartCaptcha Kaleidoscope puzzle from a bundled image.

What it does:
    This example submits a captured Kaleidoscope image and its challenge-specific step sequence
    without a proxy. It uses YandexSmartCaptchaKaleidoscopeTask and CaptchaClient.solve(), which
    returns the number of slider-arrow clicks.

How it works:
    STEP-01 - Read and Base64-encode the bundled Kaleidoscope image.
    STEP-02 - Configure CaptchaClient with CAPTCHA_API_KEY.
    STEP-03 - Create YandexSmartCaptchaKaleidoscopeTask with the image and captured steps.
    STEP-04 - Send the task with client.solve() and print the required click count.

The step sequence belongs to this captured image. A live integration must capture a fresh image
and its matching sequence, apply the clicks, and verify acceptance on the target page.
"""

import base64
import os
from pathlib import Path

from captcha_solver_api import CaptchaClient
from captcha_solver_api.tasks import YandexSmartCaptchaKaleidoscopeTask
from dotenv import load_dotenv

IMAGE_PATH = (
    Path(__file__).resolve().parent.parent / "assets" / "yandex-smartcaptcha-kaleidoscope.jpg"
)
PUZZLE_STEPS = [
    7,
    15,
    14,
    0,
    11,
    6,
    6,
    0,
    11,
    15,
    6,
    10,
    1,
    14,
    3,
    12,
    9,
    0,
    15,
    1,
    5,
    1,
    8,
    11,
    12,
    11,
    0,
    12,
    1,
    10,
    1,
    4,
    14,
    6,
    10,
    6,
    10,
    8,
    3,
    0,
    5,
    9,
    7,
    8,
    0,
    3,
    8,
    0,
    9,
    12,
    12,
    11,
    3,
    0,
    8,
    10,
]

# Load local development settings without overriding variables already set by the shell.
load_dotenv(IMAGE_PATH.parent.parent / ".env")


def main() -> None:
    # STEP-01: The SDK expects image bytes as Base64 without a data-URL prefix.
    image = base64.b64encode(IMAGE_PATH.read_bytes()).decode("ascii")

    # STEP-02: Create the SDK client with the API key from the environment.
    api_key = os.getenv("CAPTCHA_API_KEY")
    if not api_key:
        raise RuntimeError("Set CAPTCHA_API_KEY in the environment or .env file")

    with CaptchaClient(api_key) as client:
        # STEP-03: The ordered steps must come from the same challenge as the image.
        task = YandexSmartCaptchaKaleidoscopeTask(image=image, task=PUZZLE_STEPS)

        # STEP-04: solve() returns a plain click-count string for this task type.
        clicks = client.solve(task)
        print("Slider-arrow clicks:", clicks)

        # Applying the clicks and checking acceptance are site-specific browser actions.


if __name__ == "__main__":
    main()
