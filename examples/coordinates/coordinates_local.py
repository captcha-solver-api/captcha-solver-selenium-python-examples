"""Recognize click coordinates in a bundled CAPTCHA image without a browser.

What it does:
    Reads assets/coordinates/coordinates-captcha.png, Base64-encodes it, solves CoordinatesTask
    without a proxy, and prints the ordered pixel coordinates.

How it works:
    STEP-01 - Locate and encode the bundled image.
    STEP-02 - Configure CaptchaClient with CAPTCHA_API_KEY.
    STEP-03 - Create CoordinatesTask and solve it.
    STEP-04 - Print the returned points in source-image coordinates.

Applying the points requires the original page. Scale them if the displayed image dimensions
differ from the source asset, as demonstrated by coordinates.py.
"""

import base64
import os
from pathlib import Path

from captcha_solver_api import CaptchaClient
from captcha_solver_api.tasks import CoordinatesTask
from dotenv import load_dotenv

REPOSITORY_ROOT = Path(__file__).resolve().parents[2]
IMAGE_PATH = REPOSITORY_ROOT / "assets" / "coordinates" / "coordinates-captcha.png"

load_dotenv(REPOSITORY_ROOT / ".env")


def main() -> None:
    # STEP-01: Preserve the source pixels because returned points use this coordinate system.
    print(
        "\n[STEP-01] Preserve the source pixels because returned points use this coordinate system.",
        flush=True,
    )
    image = base64.b64encode(IMAGE_PATH.read_bytes()).decode("ascii")

    # STEP-02: Read the API key explicitly so this file remains self-contained.

    print(
        "\n[STEP-02] Read the API key explicitly so this file remains self-contained.", flush=True
    )
    api_key = os.getenv("CAPTCHA_API_KEY")
    if not api_key:
        raise RuntimeError("Set CAPTCHA_API_KEY in the environment or .env file")

    with CaptchaClient(api_key, debug=True) as client:
        # STEP-03: Ask for ordered click points on the bundled challenge image.
        print(
            "\n[STEP-03] Ask for ordered click points on the bundled challenge image.", flush=True
        )
        task = CoordinatesTask(body=image)
        solution = client.solve(task)

        # STEP-04: Coordinates are relative to the original asset, not a resized DOM element.

        print(
            "\n[STEP-04] Coordinates are relative to the original asset, not a resized DOM element.",
            flush=True,
        )
        print("Ordered click coordinates:", solution["coordinates"])


if __name__ == "__main__":
    main()
