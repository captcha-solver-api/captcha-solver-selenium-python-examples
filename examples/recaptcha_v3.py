"""Request and apply a reCAPTCHA v3 token."""

import time

from captcha_solver_api.tasks import RecaptchaV3TaskProxyless
from common import create_client, logged_example, required_env, show_success, wait_for_xpath
from selenium.webdriver.support.ui import WebDriverWait
from seleniumbase import Driver

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
    with Driver(browser="chrome", headless=False) as driver, create_client() as client:
        driver.get(URL)
        params = WebDriverWait(driver, 30).until(
            lambda current: current.execute_script(FIND_PARAMS)
        )
        print("Parameters sitekey and action received")
        solution = client.solve(
            RecaptchaV3TaskProxyless(
                websiteURL=URL,
                websiteKey=params["sitekey"],
                minScore=0.3,
                pageAction=params["action"],
            )
        )
        driver.execute_script(
            "window.verifyRecaptcha(arguments[0]);",
            solution["gRecaptchaResponse"],
        )
        print("The token is sent")
        wait_for_xpath(driver, SUBMIT_LOCATOR).click()
        print("Pressed the Check button")
        show_success(driver)
        time.sleep(5)


if __name__ == "__main__":
    main()
