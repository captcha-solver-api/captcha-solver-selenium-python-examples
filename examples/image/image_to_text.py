"""Solve a text CAPTCHA from a bundled local image.

What it does:
    Reads ``assets/image-to-text/text-captcha.png``, Base64-encodes it, submits an
    ``ImageToTextTask`` without a proxy, and prints the text returned by
    ``CaptchaClient.solve()``.

This offline example has no browser application or page acceptance step. A live integration
must enter the returned text into the form that supplied the original image and verify the
site's response.

How it works:
    STEP-01 - Read and Base64-encode the bundled text CAPTCHA image.
    STEP-02 - Create the SDK client with the API key from the environment.
    STEP-03 - Create and solve the image-to-text task.
    STEP-04 - Print the recognized text.
"""

import base64
import sys
from pathlib import Path

from captcha_solver_api.tasks import ImageToTextTask

if __package__ in {None, ""}:
    sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from examples.common import create_client, logged_example  # noqa: E402

REPOSITORY_ROOT = Path(__file__).resolve().parents[2]
IMAGE_PATH = REPOSITORY_ROOT / "assets" / "image-to-text" / "text-captcha.png"


@logged_example
def main() -> None:
    # STEP-01: Read and Base64-encode the bundled text CAPTCHA image.
    image = base64.b64encode(IMAGE_PATH.read_bytes()).decode("ascii")

    # STEP-02: Create the SDK client with the API key from the environment.
    with create_client() as client:
        # STEP-03: Create and solve the image-to-text task.
        solution = client.solve(ImageToTextTask(body=image))

        # STEP-04: Print the recognized text.
        print("Recognized text:", solution["text"])


if __name__ == "__main__":
    main()
