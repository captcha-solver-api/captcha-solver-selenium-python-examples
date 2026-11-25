"""Solve a coordinate CAPTCHA from a bundled local image.

What it does:
    Reads ``assets/coordinates/coordinates-captcha.png``, Base64-encodes it, submits a
    ``CoordinatesTask`` without a proxy, and prints the pixel coordinates returned by
    ``CaptchaClient.solve()``.

This offline example intentionally stops after printing the result. In a live integration,
click the original CAPTCHA image at the returned points, accounting for any display scaling,
and verify acceptance on the page that supplied the image.

How it works:
    STEP-01 - Read and Base64-encode the bundled coordinate CAPTCHA image.
    STEP-02 - Create the SDK client with the API key from the environment.
    STEP-03 - Create and solve the coordinate task.
    STEP-04 - Print the returned image-space coordinates.
"""

import base64
import sys
from pathlib import Path

from captcha_solver_api.tasks import CoordinatesTask

if __package__ in {None, ""}:
    sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from examples.common import create_client, logged_example  # noqa: E402

REPOSITORY_ROOT = Path(__file__).resolve().parents[2]
IMAGE_PATH = REPOSITORY_ROOT / "assets" / "coordinates" / "coordinates-captcha.png"


@logged_example
def main() -> None:
    # STEP-01: Read and Base64-encode the bundled coordinate CAPTCHA image.
    image = base64.b64encode(IMAGE_PATH.read_bytes()).decode("ascii")

    # STEP-02: Create the SDK client with the API key from the environment.
    with create_client() as client:
        # STEP-03: Create and solve the coordinate task.
        solution = client.solve(CoordinatesTask(body=image))

        # STEP-04: Print the returned image-space coordinates.
        print("Coordinates:", solution["coordinates"])
        print("Apply these x/y points to the original image in the returned order.")


if __name__ == "__main__":
    main()
