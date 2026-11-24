"""Discover a reCAPTCHA v2 callback automatically and invoke it.

What it does:
    Inspects reCAPTCHA's runtime client configuration to find a site key and callback path,
    solves ``RecaptchaV2TaskProxyless`` without a proxy, invokes the discovered callback with
    the token, and verifies the page's success message through ``CaptchaClient.solve()``.

To use this example on another page, change the target URL and verify the site key and any
challenge-specific parameters required by that page. Token fields, callbacks, submission, and
success indicators are site-specific, so inspect the page before applying the token.

How it works:
    STEP-01 - Start the browser and SDK client.
    STEP-02 - Open the page and inspect reCAPTCHA's runtime configuration.
    STEP-03 - Create and solve the task with the discovered site key.
    STEP-04 - Resolve the discovered callback and deliver the token to it.
    STEP-05 - Require the demo page's explicit success message.
"""

import sys
import time
from pathlib import Path

from captcha_solver_api.tasks import RecaptchaV2TaskProxyless
from selenium.webdriver.support.ui import WebDriverWait
from seleniumbase import Driver

if __package__ in {None, ""}:
    sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from examples.common import create_client, logged_example, required_env, show_success  # noqa: E402

URL = required_env("RECAPTCHA_V2_TARGET_URL", "TARGET_URL")

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


@logged_example
def main() -> None:
    # STEP-01: Start the browser and SDK client.
    with Driver(browser="chrome", headless=False) as driver, create_client() as client:
        # STEP-02: Open the page and inspect reCAPTCHA's runtime configuration.
        driver.get(URL)
        params = WebDriverWait(driver, 30).until(
            lambda current: current.execute_script(FIND_CLIENT)
        )
        print("Got the callback function name and site key")
        # STEP-03: Create and solve the task with the discovered site key.
        solution = client.solve(
            RecaptchaV2TaskProxyless(websiteURL=URL, websiteKey=params["sitekey"])
        )
        # STEP-04: Resolve the discovered callback and deliver the token to it.
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
        show_success(driver)
        time.sleep(5)


if __name__ == "__main__":
    main()
