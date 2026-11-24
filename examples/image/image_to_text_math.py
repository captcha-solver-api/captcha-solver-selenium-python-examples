"""Solve a mathematical CAPTCHA from bundled local images.

What it does:
    Reads a mathematical CAPTCHA and its instruction image from ``assets/image-to-text``,
    Base64-encodes both, and submits an ``ImageToTextTask`` with ``math=True`` and
    ``imgInstructions``. No proxy or browser is used; ``CaptchaClient.solve()`` returns the
    numeric result.

The instruction image must belong to the same challenge as the main image. A live integration
must submit the returned answer to the source page and verify that the page accepts it.

How it works:
    STEP-01 - Read and Base64-encode the CAPTCHA and instruction images.
    STEP-02 - Create the SDK client with the API key from the environment.
    STEP-03 - Create and solve the mathematical image-to-text task.
    STEP-04 - Print the returned numeric result.
"""

import base64
import sys
from pathlib import Path

from captcha_solver_api.tasks import ImageToTextTask

if __package__ in {None, ""}:
    sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from examples.common import create_client, logged_example  # noqa: E402

REPOSITORY_ROOT = Path(__file__).resolve().parents[2]
ASSETS_DIR = REPOSITORY_ROOT / "assets" / "image-to-text"
IMAGE_PATH = ASSETS_DIR / "captcha-math.png"
INSTRUCTION_PATH = ASSETS_DIR / "captcha-math-instructions.png"


def encode_image(path: Path) -> str:
    """Return the image bytes as Base64 without a data-URL prefix."""
    return base64.b64encode(path.read_bytes()).decode("ascii")


@logged_example
def main() -> None:
    # STEP-01: Read and Base64-encode the CAPTCHA and instruction images.
    image = encode_image(IMAGE_PATH)
    instructions = encode_image(INSTRUCTION_PATH)

    # STEP-02: Create the SDK client with the API key from the environment.
    with create_client() as client:
        # STEP-03: Create and solve the mathematical image-to-text task.
        solution = client.solve(
            ImageToTextTask(body=image, math=True, imgInstructions=instructions)
        )

        # STEP-04: Print the returned numeric result.
        print("Math result:", solution["text"])


if __name__ == "__main__":
    main()
