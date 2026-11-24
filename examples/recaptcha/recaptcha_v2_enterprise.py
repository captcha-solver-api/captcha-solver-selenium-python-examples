"""Solve reCAPTCHA v2 Enterprise on a configured page.

What it does:
    Opens a reCAPTCHA v2 Enterprise page, extracts its site key, solves a
    ``RecaptchaV2EnterpriseTaskProxyless`` without a proxy, inserts the returned token into
    the response field, submits the form, and checks page acceptance with
    ``CaptchaClient.solve()``.

To use this example on another page, change the target URL and inspect the Enterprise site key,
``enterprisePayload``, invisibility mode, token field, submission control, and success
indicator. These integration details are site-specific.

How it works:
    STEP-01 - Start the browser and SDK client.
    STEP-02 - Open the Enterprise page and extract its site key.
    STEP-03 - Create and solve the proxyless Enterprise task.
    STEP-04 - Insert the returned token and submit the form.
    STEP-05 - Require the page's explicit success signal.
"""

import os
import sys
import time
from pathlib import Path

from captcha_solver_api.tasks import RecaptchaV2EnterpriseTaskProxyless
from seleniumbase import Driver

if __package__ in {None, ""}:
    sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from examples.common import (  # noqa: E402
    create_client,
    fill_response_field,
    logged_example,
    required_env,
    wait_for_css,
    wait_for_xpath,
)

URL = required_env(
    "RECAPTCHA_V2_ENTERPRISE_TARGET_URL",
    "RECAPTCHA_ENTERPRISE_TARGET_URL",
)
SITEKEY_SELECTOR = "[data-sitekey]"
SUBMIT_LOCATOR = "//*[@type='submit']"
SUCCESS_SELECTOR = os.getenv(
    "RECAPTCHA_V2_ENTERPRISE_SUCCESS_SELECTOR",
    ".recaptcha-success, p.successMessage",
)


@logged_example
def main() -> None:
    # STEP-01: Start the browser and SDK client.
    with Driver(browser="chrome", headless=False) as driver, create_client() as client:
        # STEP-02: Open the Enterprise page and extract its site key.
        driver.get(URL)
        widget = wait_for_css(driver, SITEKEY_SELECTOR)
        sitekey = widget.get_attribute("data-sitekey")
        if not sitekey:
            raise RuntimeError("No reCAPTCHA v2 Enterprise sitekey found")
        print(f"Enterprise sitekey received: {sitekey}")

        # STEP-03: Create and solve the proxyless Enterprise task.
        solution = client.solve(
            RecaptchaV2EnterpriseTaskProxyless(
                websiteURL=driver.current_url,
                websiteKey=sitekey,
                isInvisible=False,
                userAgent=driver.execute_script("return navigator.userAgent"),
            )
        )
        token = solution.get("gRecaptchaResponse")
        if not isinstance(token, str) or not token:
            raise RuntimeError("Solver returned an empty Enterprise token")

        # STEP-04: Insert the returned token and submit the form.
        # Token injection and submission are site-specific; adapt this step to the target page.
        fill_response_field(driver, "g-recaptcha-response", token)
        print("Enterprise token sent")
        submit = wait_for_xpath(driver, SUBMIT_LOCATOR)
        driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", submit)
        driver.execute_script("arguments[0].click();", submit)
        print("Submitted the Enterprise form")

        # STEP-05: Require the page's explicit success signal.
        print(wait_for_css(driver, SUCCESS_SELECTOR).text)
        time.sleep(5)


if __name__ == "__main__":
    main()
