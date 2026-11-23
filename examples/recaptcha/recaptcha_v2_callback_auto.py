"""Discover a reCAPTCHA v2 callback automatically and invoke it.

What it does:
    Inspects reCAPTCHA runtime state on RECAPTCHA_V2_TARGET_URL, discovers its site key and callback, solves
    RecaptchaV2TaskProxyless, calls the discovered function, and verifies the page result.

To use this example on another page, change its type-specific target URL and inspect the
site key or challenge parameters, solution fields or callbacks, submission controls, and exact success
signal before applying the result.

How it works:
    STEP-01 - starts browser/client.
    STEP-02 - inspects runtime configuration.
    STEP-03 - solves the
    task.
    STEP-04 - invokes the discovered callback.
    STEP-05 - checks its success signal.
"""

import os
from pathlib import Path

from captcha_solver_api import CaptchaClient
from captcha_solver_api.tasks import RecaptchaV2TaskProxyless
from dotenv import load_dotenv
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from seleniumbase import Driver

REPOSITORY_ROOT = Path(__file__).resolve().parents[2]
load_dotenv(REPOSITORY_ROOT / ".env")


def required_env(name: str) -> str:
    """Return a required environment value or explain how to configure it."""
    value = os.getenv(name)
    if not value:
        raise RuntimeError(f"Set {name} in the environment or .env file")
    return value


def create_client() -> CaptchaClient:
    """Create the SDK client with CAPTCHA_API_KEY."""
    return CaptchaClient(required_env("CAPTCHA_API_KEY"), debug=True)


def show_success(driver) -> None:
    """Require the exact target-specific success text configured by the user."""
    expected_text = required_env("CAPTCHA_SUCCESS_TEXT")
    WebDriverWait(driver, 30).until(
        EC.text_to_be_present_in_element((By.TAG_NAME, "body"), expected_text)
    )
    print(f"Page confirmation: {expected_text}")


URL = required_env("RECAPTCHA_V2_TARGET_URL")

FIND_CLIENT = """
const clients = window.___grecaptcha_cfg?.clients || {};
for (const [clientId, client] of Object.entries(clients)) {
  for (const [topKey, topValue] of Object.entries(client)) {
    if (!topValue || typeof topValue !== 'object') continue;
    for (const [subKey, subValue] of Object.entries(topValue)) {
      if (!subValue || typeof subValue !== 'object' || !subValue.sitekey) continue;
      if (typeof subValue.callback === 'string') {
        return {
          sitekey: subValue.sitekey,
          callbackName: subValue.callback,
        };
      }
      if (typeof subValue.callback === 'function') {
        return {
          sitekey: subValue.sitekey,
          callbackPath:
            `___grecaptcha_cfg.clients['${clientId}']['${topKey}']['${subKey}']['callback']`,
        };
      }
    }
  }
}
return null;
"""


def main() -> None:
    # STEP-01: Start the browser and SDK client.
    print("\n[STEP-01] Start the browser and SDK client.", flush=True)
    with Driver(browser="chrome", headless=False) as driver, create_client() as client:
        # STEP-02: Open the page and inspect reCAPTCHA's runtime configuration.
        print(
            "\n[STEP-02] Open the page and inspect reCAPTCHA's runtime configuration.", flush=True
        )
        driver.get(URL)
        params = WebDriverWait(driver, 30).until(
            lambda current: current.execute_script(FIND_CLIENT)
        )
        print("Got the callback function name and site key")
        # STEP-03: Create and solve the task with the discovered site key.
        print("\n[STEP-03] Create and solve the task with the discovered site key.", flush=True)
        task = RecaptchaV2TaskProxyless(websiteURL=URL, websiteKey=params["sitekey"])
        solution = client.solve(task)
        print("Solution received; fields:", ", ".join(solution), flush=True)
        # STEP-04: Resolve the discovered callback and deliver the token to it.
        print(
            "\n[STEP-04] Resolve the discovered callback and deliver the token to it.", flush=True
        )
        # Token injection and submission are site-specific; adapt this step to the target page.
        driver.execute_script(
            """
            const callback = arguments[0]
              ? window[arguments[0]]
              : eval(arguments[1]);
            callback(arguments[2]);
            """,
            params.get("callbackName"),
            params.get("callbackPath"),
            solution["gRecaptchaResponse"],
        )
        print("The token is sent to the callback function")
        # STEP-05: Require the demo page's explicit success message.
        print("\n[STEP-05] Require the demo page's explicit success message.", flush=True)
        show_success(driver)


if __name__ == "__main__":
    main()
