"""Solve Tencent CAPTCHA on a user-configured page."""

import os
import time

from captcha_solver_api.tasks import TencentTaskProxyless
from common import create_client, logged_example, required_env, wait_for_css
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from seleniumbase import Driver

TENCENT_INTERCEPT_SCRIPT = r"""
(() => {
  const records = new Map();
  const wrappers = new WeakMap();
  let constructor;
  let sequence = 0;

  const wrap = (Original, scriptUrl) => {
    if (typeof Original !== 'function') return Original;
    if (wrappers.has(Original)) return wrappers.get(Original);
    const Wrapped = new Proxy(Original, {
      construct(Target, args, newTarget) {
        const offset = typeof args[1] === 'function' ? 0 : 1;
        const appId = args[offset];
        const callback = args[offset + 1];
        if (!appId || typeof callback !== 'function') {
          return Reflect.construct(Target, args, newTarget);
        }
        const id = `tencent-${++sequence}`;
        const params = {
          id,
          websiteURL: location.href,
          appId: String(appId),
          captchaScript: scriptUrl || [...document.scripts]
            .map(script => script.src)
            .find(src => /\/TCaptcha-global\.js(?:\?|$)/i.test(src))
        };
        const nativeArgs = [...args];
        nativeArgs[offset + 1] = () => {};
        const instance = Reflect.construct(Target, nativeArgs, newTarget);
        instance.show = () => {};
        records.set(id, {params, callback, submitted: false});
        return instance;
      }
    });
    wrappers.set(Original, Wrapped);
    wrappers.set(Wrapped, Wrapped);
    return Wrapped;
  };

  Object.defineProperty(window, '__captchaSolverTencent', {value: {
    pending: () => [...records.values()]
      .filter(record => !record.submitted)
      .map(record => record.params),
    submit(id, solution) {
      const record = records.get(id);
      if (!record || record.submitted) throw new Error('Tencent CAPTCHA callback is missing.');
      record.submitted = true;
      record.callback(solution);
    }
  }});

  const existing = window.TencentCaptcha;
  Object.defineProperty(window, 'TencentCaptcha', {
    configurable: true,
    enumerable: true,
    get: () => constructor,
    set: value => { constructor = wrap(value, document.currentScript?.src); }
  });
  if (existing) window.TencentCaptcha = existing;
})();
"""


@logged_example
def main() -> None:
    target_url = required_env("TARGET_URL")
    success_selector = required_env("TENCENT_SUCCESS_SELECTOR")

    with Driver(browser="chrome", headless=False) as driver, create_client() as client:
        driver.execute_cdp_cmd(
            "Page.addScriptToEvaluateOnNewDocument", {"source": TENCENT_INTERCEPT_SCRIPT}
        )
        driver.get(target_url)

        trigger_selector = os.getenv("TENCENT_TRIGGER_SELECTOR")
        if trigger_selector:
            WebDriverWait(driver, 30).until(
                EC.element_to_be_clickable((By.CSS_SELECTOR, trigger_selector))
            ).click()

        params = WebDriverWait(driver, 30).until(
            lambda browser: browser.execute_script(
                "return window.__captchaSolverTencent?.pending()[0] || null"
            )
        )
        record_id = params.pop("id")
        solution = client.solve(TencentTaskProxyless(**params))
        driver.execute_script(
            "window.__captchaSolverTencent.submit(arguments[0], arguments[1])",
            record_id,
            solution,
        )
        message = wait_for_css(driver, success_selector)
        WebDriverWait(driver, 30).until(EC.visibility_of(message))
        print(message.text)
        time.sleep(5)


if __name__ == "__main__":
    main()
