"""Intercept and solve Turnstile on a Cloudflare Challenge page."""

import time

from captcha_solver_api.tasks import TurnstileTaskProxyless
from common import create_client, show_success
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.support.ui import WebDriverWait
from seleniumbase import Driver

URL = "https://2captcha.com/demo/cloudflare-turnstile-challenge"

INTERCEPT_SCRIPT = """
window.__turnstileParams = null;
window.__turnstileCallback = null;
const timer = setInterval(() => {
  if (!window.turnstile) return;
  clearInterval(timer);
  window.turnstile.render = (_container, options) => {
    window.__turnstileParams = {
      websiteKey: options.sitekey,
      websiteURL: window.location.href,
      action: options.action,
      data: options.cData,
      pagedata: options.chlPageData,
      userAgent: navigator.userAgent,
    };
    window.__turnstileCallback = options.callback;
    return 'intercepted';
  };
}, 10);
"""


def main() -> None:
    with Driver(browser="chrome", headless=False) as driver, create_client() as client:
        driver.execute_cdp_cmd(
            "Page.addScriptToEvaluateOnNewDocument",
            {"source": INTERCEPT_SCRIPT},
        )
        driver.get(URL)
        try:
            WebDriverWait(driver, 30).until(
                lambda current: current.execute_script("return !!window.__turnstileParams")
            )
        except TimeoutException as exc:
            page_text = driver.execute_script("return document.body.innerText.slice(0, 500)")
            raise RuntimeError(
                "Turnstile parameters were not captured. The demo may have blocked "
                f"the browser before rendering the challenge. Page text: {page_text!r}"
            ) from exc
        params = driver.execute_script("return window.__turnstileParams")
        solution = client.solve(TurnstileTaskProxyless(**params))

        returned_user_agent = solution.get("userAgent")
        if returned_user_agent:
            driver.execute_cdp_cmd(
                "Network.setUserAgentOverride",
                {"userAgent": returned_user_agent},
            )

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
