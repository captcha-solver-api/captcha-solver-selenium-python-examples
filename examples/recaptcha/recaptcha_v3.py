"""Request and apply a reCAPTCHA v3 token.

What it does:
    Extracts the site key and action used by grecaptcha.execute(), solves
    RecaptchaV3TaskProxyless without a proxy, applies its token, and verifies page acceptance.

To use this example on another page, change its type-specific target URL and inspect the
site key or challenge parameters, solution fields or callbacks, submission controls, and exact success
signal before applying the result.

How it works:
    STEP-01 - starts browser/client.
    STEP-02 - extracts key/action.
    STEP-03 - creates and solves the
    score-based task.
    STEP-04 - applies the token.
    STEP-05 - checks the page result.
"""

import os
from pathlib import Path

from captcha_solver_api import CaptchaClient
from captcha_solver_api.tasks import RecaptchaV3TaskProxyless
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
    return CaptchaClient(required_env("CAPTCHA_API_KEY"))


def wait_for_xpath(driver, locator: str, timeout: int = 30):
    """Wait until a target-specific XPath is visible and enabled."""
    return WebDriverWait(driver, timeout).until(EC.element_to_be_clickable((By.XPATH, locator)))


def show_success(driver) -> None:
    """Require the exact target-specific success text configured by the user."""
    expected_text = required_env("CAPTCHA_SUCCESS_TEXT")
    WebDriverWait(driver, 30).until(
        EC.text_to_be_present_in_element((By.TAG_NAME, "body"), expected_text)
    )
    print(f"Page confirmation: {expected_text}")


URL = required_env("RECAPTCHA_V3_TARGET_URL")
SUBMIT_LOCATOR = "//button[@type='submit']"
MINIMUM_SCORE = 0.3

FIND_PARAMS = r"""
const source = Array.from(document.scripts).map(script => script.textContent || '').join('\n');
const pattern = /grecaptcha\.execute\s*\(\s*['"](?<sitekey>[^'"]+)['"]\s*,\s*\{[^}]*action\s*:\s*['"](?<action>[^'"]+)['"]/i;
const match = source.match(pattern);
return match?.groups ? {sitekey: match.groups.sitekey, action: match.groups.action} : null;
"""


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
        task = RecaptchaV3TaskProxyless(
            websiteURL=URL,
            websiteKey=params["sitekey"],
            minScore=MINIMUM_SCORE,
            pageAction=params["action"],
        )
        solution = client.solve(task)
        print("Solution:", solution)
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


if __name__ == "__main__":
    main()
