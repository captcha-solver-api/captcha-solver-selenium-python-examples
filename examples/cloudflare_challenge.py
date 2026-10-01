"""Intercept and solve Turnstile on a Cloudflare Challenge page."""

import os
import time

from captcha_solver_api.tasks import TurnstileTaskProxyless
from common import create_client, required_env, show_success
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.support.ui import WebDriverWait
from seleniumbase import Driver

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


def main() -> None:
    with (
        Driver(browser="chrome", headless=False, agent=BROWSER_USER_AGENT) as driver,
        create_client() as client,
    ):
        driver.get(URL)
        driver.execute_cdp_cmd(
            "Page.addScriptToEvaluateOnNewDocument",
            {"source": INTERCEPT_SCRIPT},
        )
        driver.refresh()
        params = capture_params(driver)
        if params is None:
            return
        solution = client.solve(TurnstileTaskProxyless(**params))

        driver.execute_script(
            """
            if (typeof window.__turnstileCallback !== 'function') {
              throw new Error('Turnstile callback was not captured');
            }
            window.__turnstileCallback(arguments[0]);
            """,
            solution["token"],
        )
        show_success(driver)
        time.sleep(10)


if __name__ == "__main__":
    main()
