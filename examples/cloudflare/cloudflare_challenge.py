"""Intercept and solve Turnstile on a Cloudflare Challenge page.

What it does:
    Intercepts Turnstile render parameters on CLOUDFLARE_CHALLENGE_TARGET_URL, solves TurnstileTaskProxyless with the
    browser User-Agent, delivers the token to the captured callback, and checks page acceptance.

To use this example on another page, change its type-specific target URL and inspect the
site key or challenge parameters, solution fields or callbacks, submission controls, and exact success
signal before applying the result.

How it works:
    STEP-01 - starts browser/client.
    STEP-02 - installs the interceptor.
    STEP-03 - solves from captured
    parameters.
    STEP-04 - invokes the callback.
    STEP-05 - checks the explicit success signal.
"""

import os
from pathlib import Path

from captcha_solver_api import CaptchaClient
from captcha_solver_api.tasks import TurnstileTaskProxyless
from dotenv import load_dotenv
from selenium.common.exceptions import TimeoutException
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


URL = required_env("CLOUDFLARE_CHALLENGE_TARGET_URL")
BROWSER_USER_AGENT = os.getenv("BROWSER_USER_AGENT") or (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36"
)

INTERCEPT_SCRIPT = """
window.__turnstileParams = null;
window.__turnstileCallback = null;
const timer = setInterval(() => {
  if (!window.turnstile) return;
  clearInterval(timer);
  const originalRender = window.turnstile.render;
  window.turnstile.render = (container, options) => {
    window.__turnstileParams = {
      websiteKey: options.sitekey,
      websiteURL: window.location.href,
      action: options.action,
      data: options.cData,
      pagedata: options.chlPageData,
      userAgent: navigator.userAgent,
    };
    window.__turnstileCallback = options.callback;
    return originalRender ? originalRender(container, options) : undefined;
  };
}, 10);
"""


def capture_params(driver):
    try:
        state = WebDriverWait(driver, 30).until(
            lambda current: current.execute_script(
                """
                if (window.__turnstileParams) {
                  return {params: window.__turnstileParams};
                }
                const success = document.querySelector('p.successMessage');
                if (success && success.offsetParent !== null) {
                  return {success: success.innerText};
                }
                return null;
                """
            )
        )
    except TimeoutException as exc:
        page_text = driver.execute_script("return document.body.innerText.slice(0, 500)")
        raise RuntimeError(
            "Turnstile parameters were not captured. The demo may have blocked "
            f"the browser before rendering the challenge. Page text: {page_text!r}"
        ) from exc
    if state.get("success"):
        print(state["success"])
        return None
    return state["params"]


def main() -> None:
    # STEP-01: Start Chrome with the same User-Agent sent in the solver task.
    with (
        Driver(browser="chrome", headless=False, agent=BROWSER_USER_AGENT) as driver,
        create_client() as client,
    ):
        initial_clearance = next(
            (
                cookie["value"]
                for cookie in driver.get_cookies()
                if cookie["name"] == "cf_clearance"
            ),
            None,
        )
        # STEP-02: Install the interceptor before reloading the challenge page.
        driver.get(URL)
        driver.execute_cdp_cmd(
            "Page.addScriptToEvaluateOnNewDocument",
            {"source": INTERCEPT_SCRIPT},
        )
        driver.refresh()
        params = capture_params(driver)
        if params is None:
            return
        print("Parameters received")
        # STEP-03: Build the task from captured render options and solve it.
        task = TurnstileTaskProxyless(**params)
        solution = client.solve(task)
        print("Solution:", solution)

        # STEP-04: Deliver the token to the callback captured from this page.
        # Token injection and submission are site-specific; adapt this step to the target page.
        driver.execute_script(
            """
            if (typeof window.__turnstileCallback !== 'function') {
              throw new Error('Turnstile callback was not captured');
            }
            window.__turnstileCallback(arguments[0]);
            """,
            solution["token"],
        )
        print("The token is sent to the callback function")
        # STEP-05: Require a new clearance cookie and a page that is no longer the challenge.
        clearance = WebDriverWait(driver, 30).until(
            lambda current: next(
                (
                    cookie["value"]
                    for cookie in current.get_cookies()
                    if cookie["name"] == "cf_clearance" and cookie["value"] != initial_clearance
                ),
                None,
            )
        )
        if "challenge" in driver.current_url.lower():
            raise RuntimeError("A new clearance cookie was set, but the challenge page remained")
        print(f"Cloudflare accepted the solution; new clearance cookie: {clearance[:8]}...")


if __name__ == "__main__":
    main()
