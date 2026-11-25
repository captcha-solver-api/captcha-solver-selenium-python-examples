"""Solve a digits-only CAPTCHA from a bundled local image.

What it does:
    Reads ``assets/image-to-text/captcha-digits.png``, Base64-encodes it, and submits an
    ``ImageToTextTask`` with digit and length hints. No proxy or browser is used;
    ``CaptchaClient.solve()`` returns the recognized digits.

The hints belong to this sample image. When adapting the example, update them to match the
actual character set and answer length expected by the source CAPTCHA.

How it works:
    STEP-01 - Read and Base64-encode the bundled digits CAPTCHA image.
    STEP-02 - Create the SDK client with the API key from the environment.
    STEP-03 - Create and solve the task with digits-only recognition hints.
    STEP-04 - Print the recognized digits.
"""

import base64
import sys
from pathlib import Path

from captcha_solver_api.tasks import ImageToTextTask

if __package__ in {None, ""}:
    sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from examples.common import create_client, logged_example  # noqa: E402

REPOSITORY_ROOT = Path(__file__).resolve().parents[2]
IMAGE_PATH = REPOSITORY_ROOT / "assets" / "image-to-text" / "captcha-digits.png"


@logged_example
def main() -> None:
    # STEP-01: Read and Base64-encode the bundled digits CAPTCHA image.
    image = base64.b64encode(IMAGE_PATH.read_bytes()).decode("ascii")

    # STEP-02: Create the SDK client with the API key from the environment.
    with create_client() as client:
        # STEP-03: Create and solve the task with digits-only recognition hints.
        solution = client.solve(ImageToTextTask(body=image, numeric=1, minLength=5, maxLength=5))

        # STEP-04: Print the recognized digits.
        print("Recognized digits:", solution["text"])


if __name__ == "__main__":
    main()
