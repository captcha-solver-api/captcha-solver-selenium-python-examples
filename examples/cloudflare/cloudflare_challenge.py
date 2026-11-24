"""Intercept and solve Turnstile on a Cloudflare Challenge page.

What it does:
    Opens a user-configured Cloudflare Challenge page, captures the parameters passed to
    ``turnstile.render()``, solves them without a proxy, and returns the token through the
    page's original callback. The example uses ``TurnstileTaskProxyless`` and
    ``CaptchaClient.solve()``.

To use this example on another page, change the target URL and verify the captured site key,
action, challenge data, User-Agent, and callback. Token delivery, submission, and success
indicators are site-specific, so inspect the page before applying the token.

How it works:
    STEP-01 - Start Chrome with the same User-Agent sent in the solver task.
    STEP-02 - Install the interceptor before reloading the challenge page.
    STEP-03 - Build the task from captured render options and solve it.
    STEP-04 - Deliver the token to the callback captured from this page.
    STEP-05 - Verify the page's explicit success signal after callback delivery.
"""

import os
import sys
import time
from pathlib import Path

from captcha_solver_api.tasks import TurnstileTaskProxyless
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.support.ui import WebDriverWait
from seleniumbase import Driver

if __package__ in {None, ""}:
    sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from examples.common import create_client, logged_example, required_env, show_success  # noqa: E402

URL = required_env("TARGET_URL")
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


@logged_example
def main() -> None:
    # STEP-01: Start Chrome with the same User-Agent sent in the solver task.
    with (
        Driver(browser="chrome", headless=False, agent=BROWSER_USER_AGENT) as driver,
        create_client() as client,
    ):
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
        solution = client.solve(TurnstileTaskProxyless(**params))

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
        # STEP-05: Verify the page's explicit success signal after callback delivery.
        show_success(driver)
        time.sleep(10)


if __name__ == "__main__":
    main()
