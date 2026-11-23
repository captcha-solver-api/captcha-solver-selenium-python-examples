"""Recognize text from a bundled CAPTCHA image without opening a browser.

What it does:
    Reads assets/image-to-text/text-captcha.png, Base64-encodes it, solves ImageToTextTask
    without a proxy, and prints the recognized text.

How it works:
    STEP-01 - Locate and encode the bundled image.
    STEP-02 - Configure CaptchaClient with CAPTCHA_API_KEY.
    STEP-03 - Create ImageToTextTask and solve it.
    STEP-04 - Print the returned text.

The other files in assets/image-to-text demonstrate numeric and mathematical CAPTCHA variants.
Use their matching task hints when adapting this example.
"""

import base64
import os
from pathlib import Path

from captcha_solver_api import CaptchaClient
from captcha_solver_api.tasks import ImageToTextTask
from dotenv import load_dotenv

REPOSITORY_ROOT = Path(__file__).resolve().parents[2]
IMAGE_PATH = REPOSITORY_ROOT / "assets" / "image-to-text" / "text-captcha.png"

load_dotenv(REPOSITORY_ROOT / ".env")


def main() -> None:
    # STEP-01: The SDK expects Base64 image data without a data-URL prefix.
    image = base64.b64encode(IMAGE_PATH.read_bytes()).decode("ascii")

    # STEP-02: Read the API key explicitly so this file remains self-contained.
    api_key = os.getenv("CAPTCHA_API_KEY")
    if not api_key:
        raise RuntimeError("Set CAPTCHA_API_KEY in the environment or .env file")

    with CaptchaClient(api_key) as client:
        # STEP-03: Create the image recognition task and wait for its solution.
        task = ImageToTextTask(body=image)
        solution = client.solve(task)

        # STEP-04: ImageToTextTask returns the recognized answer in the text field.
        print("Recognized text:", solution["text"])


if __name__ == "__main__":
    main()
