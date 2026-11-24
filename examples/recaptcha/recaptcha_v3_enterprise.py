"""Solve reCAPTCHA v3 Enterprise on a configured page.

What it does:
    Extracts the site key and action used by ``grecaptcha.enterprise.execute()``, solves a
    ``RecaptchaV3TaskProxyless`` with ``isEnterprise=True`` and no proxy, delivers the
    token to the configured page callback, and verifies acceptance with
    ``CaptchaClient.solve()``.

To use this example on another page, change the target URL and inspect the Enterprise site key,
action, minimum score, callback, submission behavior, and success indicator. Token delivery and
acceptance checks are site-specific.

How it works:
    STEP-01 - Start the browser and SDK client.
    STEP-02 - Open the page and extract the Enterprise site key and action.
    STEP-03 - Create and solve the score-based Enterprise task.
    STEP-04 - Deliver the returned token to the configured callback.
    STEP-05 - Require the page's explicit success signal.
"""

import os
import sys
import time
from pathlib import Path

from captcha_solver_api.tasks import RecaptchaV3TaskProxyless
from selenium.webdriver.support.ui import WebDriverWait
from seleniumbase import Driver

if __package__ in {None, ""}:
    sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from examples.common import create_client, logged_example, required_env, wait_for_css  # noqa: E402

URL = required_env("RECAPTCHA_V3_ENTERPRISE_TARGET_URL")
CALLBACK_NAME = os.getenv("RECAPTCHA_V3_ENTERPRISE_CALLBACK_NAME", "verifyRecaptcha")
SUCCESS_SELECTOR = os.getenv(
    "RECAPTCHA_V3_ENTERPRISE_SUCCESS_SELECTOR",
    ".recaptcha-success, p.successMessage",
)
MINIMUM_SCORE = 0.3

FIND_PARAMS = r"""
const source = Array.from(document.scripts).map(script => script.textContent || '').join('\n');
const pattern = /grecaptcha\.enterprise\.execute\s*\(\s*['"]([^'"]+)['"]\s*,\s*\{[^}]*action\s*:\s*['"]([^'"]+)['"]/i;
const match = source.match(pattern);
return match ? {sitekey: match[1], action: match[2]} : null;
"""


@logged_example
def main() -> None:
    # STEP-01: Start the browser and SDK client.
    with Driver(browser="chrome", headless=False) as driver, create_client() as client:
        # STEP-02: Open the page and extract the Enterprise site key and action.
        driver.get(URL)
        params = WebDriverWait(driver, 30).until(
            lambda current: current.execute_script(FIND_PARAMS)
        )
        print(
            "Enterprise parameters received:",
            {"sitekey": params["sitekey"], "action": params["action"]},
        )

        # STEP-03: Create and solve the score-based Enterprise task.
        solution = client.solve(
            RecaptchaV3TaskProxyless(
                websiteURL=driver.current_url,
                websiteKey=params["sitekey"],
                minScore=MINIMUM_SCORE,
                pageAction=params["action"],
                isEnterprise=True,
            )
        )
        token = solution.get("gRecaptchaResponse")
        if not isinstance(token, str) or not token:
            raise RuntimeError("Solver returned an empty Enterprise token")

        # STEP-04: Deliver the returned token to the configured callback.
        # Token injection and submission are site-specific; adapt this step to the target page.
        driver.execute_script(
            """
            const callbackName = arguments[0];
            const callback = callbackName
              .split('.')
              .reduce((value, key) => value?.[key], window);
            if (typeof callback !== 'function') {
              throw new Error(`Callback ${callbackName} was not found`);
            }
            callback(arguments[1]);
            """,
            CALLBACK_NAME,
            token,
        )
        print(f"Enterprise token sent to callback {CALLBACK_NAME}")

        # STEP-05: Require the page's explicit success signal.
        print(wait_for_css(driver, SUCCESS_SELECTOR).text)
        time.sleep(5)


if __name__ == "__main__":
    main()
