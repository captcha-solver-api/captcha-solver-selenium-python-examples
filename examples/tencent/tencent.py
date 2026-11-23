"""Solve Tencent CAPTCHA on a user-configured page.

What it does:
    Installs an interceptor before TARGET_URL loads, captures Tencent constructor parameters,
    solves TencentTaskProxyless, delivers ticket/randstr to the original callback, and checks the
    target-specific success element.

How it works:
    STEP-01 loads configuration. STEP-02 installs interception. STEP-03 captures parameters.
    STEP-04 solves the task. STEP-05 invokes the callback. STEP-06 checks the page signal.
"""

import os
import time

from captcha_solver_api.tasks import TencentTaskProxyless
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from seleniumbase import Driver

from examples.common import create_client, logged_example, required_env, wait_for_css

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
    # STEP-01: Read target-specific configuration and start the browser/client.
    target_url = required_env("TARGET_URL")
    success_selector = required_env("TENCENT_SUCCESS_SELECTOR")

    with Driver(browser="chrome", headless=False) as driver, create_client() as client:
        # STEP-02: Install the constructor interceptor before opening the page.
        driver.execute_cdp_cmd(
            "Page.addScriptToEvaluateOnNewDocument", {"source": TENCENT_INTERCEPT_SCRIPT}
        )
        driver.get(target_url)

        trigger_selector = os.getenv("TENCENT_TRIGGER_SELECTOR")
        if trigger_selector:
            WebDriverWait(driver, 30).until(
                EC.element_to_be_clickable((By.CSS_SELECTOR, trigger_selector))
            ).click()

        # STEP-03: Capture the app ID and other parameters passed by the page.
        params = WebDriverWait(driver, 30).until(
            lambda browser: browser.execute_script(
                "return window.__captchaSolverTencent?.pending()[0] || null"
            )
        )
        record_id = params.pop("id")
        # STEP-04: Create the proxyless task and wait for ticket/randstr.
        task = TencentTaskProxyless(**params)
        solution = client.solve(task)
        # STEP-05: Deliver the result to the original page callback.
        # Token injection and submission are site-specific; adapt this step to the target page.
        driver.execute_script(
            "window.__captchaSolverTencent.submit(arguments[0], arguments[1])",
            record_id,
            solution,
        )
        # STEP-06: Require the target's configured success element after delivery.
        message = wait_for_css(driver, success_selector)
        WebDriverWait(driver, 30).until(EC.visibility_of(message))
        print(message.text)
        time.sleep(5)


if __name__ == "__main__":
    main()
