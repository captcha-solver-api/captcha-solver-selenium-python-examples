"""Solve a Yandex SmartCaptcha Kaleidoscope puzzle from a bundled image.

What it does:
    This example submits a captured Kaleidoscope image and its challenge-specific step sequence
    without a proxy. It uses YandexSmartCaptchaKaleidoscopeTask and CaptchaClient.solve(), which
    returns the number of slider-arrow clicks.

The step sequence belongs to this captured image. A live integration must capture a fresh
image and its matching sequence, apply the returned clicks to the original challenge, and
verify acceptance on that page.

How it works:
    STEP-01 - The SDK expects image bytes as Base64 without a data-URL prefix.
    STEP-02 - Create the SDK client with the API key from the environment.
    STEP-03 - The ordered steps must come from the same challenge as the image.
    STEP-04 - solve() returns a plain click-count string for this task type.
"""

import base64
from pathlib import Path

from captcha_solver_api.tasks import YandexSmartCaptchaKaleidoscopeTask

from examples.common import create_client

REPOSITORY_ROOT = Path(__file__).resolve().parents[2]
IMAGE_PATH = REPOSITORY_ROOT / "assets" / "yandex" / "yandex-smartcaptcha-kaleidoscope.jpg"
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


def main() -> None:
    # STEP-01: The SDK expects image bytes as Base64 without a data-URL prefix.
    print(
        "\n[STEP-01] The SDK expects image bytes as Base64 without a data-URL prefix.", flush=True
    )
    image = base64.b64encode(IMAGE_PATH.read_bytes()).decode("ascii")

    # STEP-02: Create the SDK client with the API key from the environment.

    print("\n[STEP-02] Create the SDK client with the API key from the environment.", flush=True)
    with create_client() as client:
        # STEP-03: The ordered steps must come from the same challenge as the image.
        print(
            "\n[STEP-03] The ordered steps must come from the same challenge as the image.",
            flush=True,
        )
        task = YandexSmartCaptchaKaleidoscopeTask(image=image, task=PUZZLE_STEPS)

        # STEP-04: solve() returns a plain click-count string for this task type.

        print(
            "\n[STEP-04] solve() returns a plain click-count string for this task type.", flush=True
        )
        clicks = client.solve(task)
        print("Slider-arrow clicks:", clicks)

        # Applying the clicks and checking acceptance are site-specific browser actions.


if __name__ == "__main__":
    main()
