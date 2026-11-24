"""Request and apply a reCAPTCHA v3 token.

What it does:
    Finds the site key and action used by ``grecaptcha.execute()``, solves a score-based
    ``RecaptchaV3TaskProxyless`` without a proxy, passes the token into the page integration,
    submits the form, and checks acceptance through ``CaptchaClient.solve()``.

How it works:
    STEP-01 - Start Chrome and create the SDK client.
    STEP-02 - Extract the site key and action from page scripts.
    STEP-03 - Create and solve the score-based task.
    STEP-04 - Apply the token through the page integration.
    STEP-05 - Require the page's success message.

Script patterns, callbacks, submission, and success indicators are site-specific. Inspect the
target's v3 execution path before adapting the example.
"""

import time

from captcha_solver_api.tasks import RecaptchaV3TaskProxyless
from selenium.webdriver.support.ui import WebDriverWait
from seleniumbase import Driver

from examples.common import (
    create_client,
    logged_example,
    required_env,
    show_success,
    wait_for_xpath,
)

URL = required_env("TARGET_URL")
SUBMIT_LOCATOR = "//button[@type='submit']"

FIND_PARAMS = r"""
const source = Array.from(document.scripts).map(script => script.textContent || '').join('\n');
const pattern = /grecaptcha\.execute\s*\(\s*['"]([^'"]+)['"]\s*,\s*\{[^}]*action\s*:\s*['"]([^'"]+)['"]/i;
const match = source.match(pattern);
return match ? {sitekey: match[1], action: match[2]} : null;
"""


@logged_example
def main() -> None:
    # STEP-01: Start the browser and SDK client.
    with Driver(browser="chrome", headless=False) as driver, create_client() as client:
        # STEP-02: Open the page and extract the key/action used by grecaptcha.execute().
        driver.get(URL)
        params = WebDriverWait(driver, 30).until(
            lambda current: current.execute_script(FIND_PARAMS)
        )
        print("Parameters sitekey and action received")
        # STEP-03: Create the score-based task and wait for its token.
        solution = client.solve(
            RecaptchaV3TaskProxyless(
                websiteURL=URL,
                websiteKey=params["sitekey"],
                minScore=0.3,
                pageAction=params["action"],
            )
        )
        # STEP-04: Apply the token using this target page's integration.
        # Token injection and submission are site-specific; adapt this step to the target page.
        driver.execute_script(
            "window.verifyRecaptcha(arguments[0]);",
            solution["gRecaptchaResponse"],
        )
        print("The token is sent")
        wait_for_xpath(driver, SUBMIT_LOCATOR).click()
        print("Pressed the Check button")
        # STEP-05: Verify page acceptance independently of SDK completion.
        show_success(driver)
        time.sleep(5)


if __name__ == "__main__":
    main()
