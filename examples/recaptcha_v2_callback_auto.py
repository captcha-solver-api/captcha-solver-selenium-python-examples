"""Discover a reCAPTCHA v2 callback automatically and invoke it."""

import time

from captcha_solver_api.tasks import RecaptchaV2TaskProxyless
from common import create_client, logged_example, required_env, show_success
from selenium.webdriver.support.ui import WebDriverWait
from seleniumbase import Driver

URL = required_env("TARGET_URL")

FIND_CLIENT = """
const clients = window.___grecaptcha_cfg?.clients || {};
for (const [clientId, client] of Object.entries(clients)) {
  for (const [topKey, topValue] of Object.entries(client)) {
    if (!topValue || typeof topValue !== 'object') continue;
    for (const [subKey, subValue] of Object.entries(topValue)) {
      if (!subValue || typeof subValue !== 'object' || !subValue.sitekey) continue;
      if (typeof subValue.callback === 'string') {
        return {
          sitekey: subValue.sitekey,
          callbackName: subValue.callback,
        };
      }
      if (typeof subValue.callback === 'function') {
        return {
          sitekey: subValue.sitekey,
          callbackPath:
            `___grecaptcha_cfg.clients['${clientId}']['${topKey}']['${subKey}']['callback']`,
        };
      }
    }
  }
}
return null;
"""


@logged_example
def main() -> None:
    with Driver(browser="chrome", headless=False) as driver, create_client() as client:
        driver.get(URL)
        params = WebDriverWait(driver, 30).until(
            lambda current: current.execute_script(FIND_CLIENT)
        )
        print("Got the callback function name and site key")
        solution = client.solve(
            RecaptchaV2TaskProxyless(websiteURL=URL, websiteKey=params["sitekey"])
        )
        driver.execute_script(
            """
            const callback = arguments[0]
              ? window[arguments[0]]
              : eval(arguments[1]);
            callback(arguments[2]);
            """,
            params.get("callbackName"),
            params.get("callbackPath"),
            solution["gRecaptchaResponse"],
        )
        print("The token is sent to the callback function")
        show_success(driver)
        time.sleep(5)


if __name__ == "__main__":
    main()
