"""Solve reCAPTCHA v2 Enterprise on a configured page.

What it does:
    Opens a reCAPTCHA v2 Enterprise page, extracts its site key, solves a
    ``RecaptchaV2EnterpriseTaskProxyless`` without a proxy, inserts the returned token into
    the response field, exposes it through the Enterprise page API, submits the
    form, and checks the page's acceptance message.

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
SUCCESS_SELECTOR = (
    os.getenv(
        "RECAPTCHA_V2_ENTERPRISE_SUCCESS_SELECTOR",
        "",
    )
    or "p[class*='successMessage'], [role='alert']"
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
        # This React form reads grecaptcha.enterprise.getResponse() during submission, so keep
        # both the native response field and the page API synchronized with the solved token.
        fill_response_field(driver, "g-recaptcha-response", token)
        driver.execute_script(
            """
            const token = arguments[0];
            const field = document.querySelector('[name="g-recaptcha-response"]');
            const nativeSetter = Object.getOwnPropertyDescriptor(
              HTMLTextAreaElement.prototype,
              'value'
            ).set;
            nativeSetter.call(field, token);
            field.dispatchEvent(new Event('input', {bubbles: true}));
            field.dispatchEvent(new Event('change', {bubbles: true}));

            const enterprise = window.grecaptcha?.enterprise;
            if (!enterprise || typeof enterprise.getResponse !== 'function') {
              throw new Error('grecaptcha.enterprise.getResponse is unavailable');
            }
            enterprise.getResponse = () => token;
            """,
            token,
        )
        print("Enterprise token sent")
        submit = wait_for_xpath(driver, SUBMIT_LOCATOR)
        driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", submit)
        driver.execute_script("arguments[0].click();", submit)
        print("Submitted the Enterprise form")

        # STEP-05: Require the page's explicit success signal.
        result = wait_for_css(driver, SUCCESS_SELECTOR)
        message = result.text.strip()
        if not message:
            raise RuntimeError("The Enterprise page returned an empty result message")
        result_class = (result.get_attribute("class") or "").lower()
        result_role = (result.get_attribute("role") or "").lower()
        if result_role == "alert" or "error" in result_class:
            raise RuntimeError(f"The Enterprise page rejected the token: {message}")
        print(f"Page confirmation: {message}")
        time.sleep(5)


if __name__ == "__main__":
    main()
