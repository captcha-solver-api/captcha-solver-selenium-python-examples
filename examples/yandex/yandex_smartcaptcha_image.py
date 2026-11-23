"""Solve an image-based Yandex SmartCaptcha from bundled local images.

What it does:
    This example submits a captured SmartCaptcha challenge image and its instruction image
    without a proxy. It uses YandexSmartCaptchaImageTask and CaptchaClient.solve(), which
    returns ordered pixel coordinates.

How it works:
    STEP-01 - Locate and Base64-encode the bundled challenge assets.
    STEP-02 - Configure CaptchaClient with CAPTCHA_API_KEY.
    STEP-03 - Create YandexSmartCaptchaImageTask with both images.
    STEP-04 - Send the task with client.solve() and print the ordered click coordinates.

The example intentionally stops after printing the result: applying coordinates and checking
acceptance require the browser page from which the two images were captured.
"""

import base64
import os
from pathlib import Path

from captcha_solver_api import CaptchaClient
from captcha_solver_api.tasks import YandexSmartCaptchaImageTask
from dotenv import load_dotenv

REPOSITORY_ROOT = Path(__file__).resolve().parents[2]
ASSETS_DIR = REPOSITORY_ROOT / "assets" / "yandex"
CHALLENGE_IMAGE = ASSETS_DIR / "yandex-smartcaptcha-image.jpg"
INSTRUCTION_IMAGE = ASSETS_DIR / "yandex-smartcaptcha-instructions.png"

# Load local development settings without overriding variables already set by the shell.
load_dotenv(REPOSITORY_ROOT / ".env")


def encode_image(path: Path) -> str:
    """Read an image and return the pure Base64 value expected by the SDK."""
    return base64.b64encode(path.read_bytes()).decode("ascii")


def main() -> None:
    # STEP-01: Read both parts of the same captured challenge from local assets.
    challenge = encode_image(CHALLENGE_IMAGE)
    instructions = encode_image(INSTRUCTION_IMAGE)

    # STEP-02: Create the SDK client with the API key from the environment.
    api_key = os.getenv("CAPTCHA_API_KEY")
    if not api_key:
        raise RuntimeError("Set CAPTCHA_API_KEY in the environment or .env file")

    with CaptchaClient(api_key) as client:
        # STEP-03: Keep the main image and click-order instructions together in one task.
        task = YandexSmartCaptchaImageTask(
            image=challenge,
            imgInstructions=instructions,
        )

        # STEP-04: solve() creates the task, waits for it, and returns ordered coordinates.
        solution = client.solve(task)
        print("Ordered click coordinates:", solution["coordinates"])

        # Coordinate application is site-specific. Click these points on the original image
        # in the returned order, then use that page's own success signal to verify acceptance.


if __name__ == "__main__":
    main()
