"""Solve an image-based Yandex SmartCaptcha from bundled local images.

What it does:
    This example submits a captured SmartCaptcha challenge image and its instruction image
    without a proxy. It uses YandexSmartCaptchaImageTask and CaptchaClient.solve(), which
    returns ordered pixel coordinates.

This offline example intentionally stops after printing the result. A live integration must
capture both images from the same challenge, click the original image at the returned points
in order, account for any scaling, and verify acceptance on that page.

How it works:
    STEP-01 - Read both parts of the same captured challenge from local assets.
    STEP-02 - Create the SDK client with the API key from the environment.
    STEP-03 - Keep the main image and click-order instructions together in one task.
    STEP-04 - solve() creates the task, waits for it, and returns ordered coordinates.
"""

import base64
from pathlib import Path

from captcha_solver_api.tasks import YandexSmartCaptchaImageTask

from examples.common import create_client

REPOSITORY_ROOT = Path(__file__).resolve().parents[2]
ASSETS_DIR = REPOSITORY_ROOT / "assets" / "yandex"
CHALLENGE_IMAGE = ASSETS_DIR / "yandex-smartcaptcha-image.jpg"
INSTRUCTION_IMAGE = ASSETS_DIR / "yandex-smartcaptcha-instructions.png"


def encode_image(path: Path) -> str:
    """Read an image and return the pure Base64 value expected by the SDK."""
    return base64.b64encode(path.read_bytes()).decode("ascii")


def main() -> None:
    # STEP-01: Read both parts of the same captured challenge from local assets.
    print(
        "\n[STEP-01] Read both parts of the same captured challenge from local assets.", flush=True
    )
    challenge = encode_image(CHALLENGE_IMAGE)
    instructions = encode_image(INSTRUCTION_IMAGE)

    # STEP-02: Create the SDK client with the API key from the environment.

    print("\n[STEP-02] Create the SDK client with the API key from the environment.", flush=True)
    with create_client() as client:
        # STEP-03: Keep the main image and click-order instructions together in one task.
        print(
            "\n[STEP-03] Keep the main image and click-order instructions together in one task.",
            flush=True,
        )
        task = YandexSmartCaptchaImageTask(
            image=challenge,
            imgInstructions=instructions,
        )

        # STEP-04: solve() creates the task, waits for it, and returns ordered coordinates.

        print(
            "\n[STEP-04] solve() creates the task, waits for it, and returns ordered coordinates.",
            flush=True,
        )
        solution = client.solve(task)
        print("Ordered click coordinates:", solution["coordinates"])

        # Coordinate application is site-specific. Click these points on the original image
        # in the returned order, then use that page's own success signal to verify acceptance.


if __name__ == "__main__":
    main()
