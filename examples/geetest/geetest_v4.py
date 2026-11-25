"""Solve GeeTest v4 on a configured page with SeleniumBase.

What it does:
    Intercepts ``initGeetest4`` to capture the page's ``captchaId`` and widget instance, solves
    ``GeeTestTaskProxyless`` with version 4, exposes the complete solution through the widget's
    ``getValidate()``, submits the form, and checks the page's verification response.

To use this example on another page, change the target URL and inspect its ``initGeetest4`` call,
widget callback, submission behavior, and acceptance indicator. All v4 solution fields must be
delivered together; these integration details are site-specific.

How it works:
    STEP-01 - Install the initGeetest4 interceptor and start the browser/client.
    STEP-02 - Open the page and capture its captcha ID and widget instance.
    STEP-03 - Create and solve the proxyless GeeTest v4 task.
    STEP-04 - Return the complete solution from getValidate() and submit the form.
    STEP-05 - Require an explicit successful verification response from the page.
"""

import sys
import time
from pathlib import Path

from captcha_solver_api.tasks import GeeTestTaskProxyless
from selenium.webdriver.support.ui import WebDriverWait
from seleniumbase import Driver

if __package__ in {None, ""}:
    sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from examples.common import (  # noqa: E402
    create_client,
    logged_example,
    required_env,
    wait_for_css,
    wait_for_xpath,
)

URL = required_env("GEETEST_V4_TARGET_URL")
SUBMIT_LOCATOR = "//button[@type='submit' and @data-action='demo_action']"
RESULT_SELECTOR = "p[class*='successMessage'], [role='alert']"

GEETEST_V4_INTERCEPT_SCRIPT = r"""
(() => {
  let original;
  const state = {params: null, instance: null};

  const wrap = value => {
    if (typeof value !== 'function' || value.__captchaSolverWrapped) return value;
    const wrapped = function(params, callback) {
      state.params = {...params};
      return value.call(this, params, instance => {
        state.instance = instance;
        return callback(instance);
      });
    };
    Object.defineProperty(wrapped, '__captchaSolverWrapped', {value: true});
    return wrapped;
  };

  Object.defineProperty(window, '__captchaSolverGeeTest4', {
    value: {
      params: () => state.params,
      ready: () => Boolean(state.instance),
      apply(solution) {
        if (!state.instance) throw new Error('GeeTest v4 widget instance is unavailable');
        state.instance.getValidate = () => ({...solution});
        return state.instance.getValidate();
      }
    }
  });

  Object.defineProperty(window, 'initGeetest4', {
    configurable: true,
    enumerable: true,
    get: () => original,
    set: value => { original = wrap(value); }
  });
})();
"""


@logged_example
def main() -> None:
    # STEP-01: Install the initGeetest4 interceptor and start the browser/client.
    with Driver(browser="chrome", headless=False) as driver, create_client() as client:
        driver.execute_cdp_cmd(
            "Page.addScriptToEvaluateOnNewDocument",
            {"source": GEETEST_V4_INTERCEPT_SCRIPT},
        )

        # STEP-02: Open the page and capture its captcha ID and widget instance.
        driver.get(URL)
        params = WebDriverWait(driver, 30).until(
            lambda browser: browser.execute_script(
                "return window.__captchaSolverGeeTest4?.params() || null"
            )
        )
        WebDriverWait(driver, 30).until(
            lambda browser: browser.execute_script(
                "return window.__captchaSolverGeeTest4?.ready() || false"
            )
        )
        captcha_id = params.get("captchaId") if isinstance(params, dict) else None
        if not isinstance(captcha_id, str) or not captcha_id:
            raise RuntimeError("No GeeTest v4 captchaId was captured from initGeetest4")
        print("GeeTest v4 captcha ID received")

        # STEP-03: Create and solve the proxyless GeeTest v4 task.
        solution = client.solve(
            GeeTestTaskProxyless(
                websiteURL=driver.current_url,
                version=4,
                initParameters={"captcha_id": captcha_id},
                userAgent=driver.execute_script("return navigator.userAgent"),
            )
        )
        required_fields = (
            "captcha_id",
            "lot_number",
            "pass_token",
            "gen_time",
            "captcha_output",
        )
        if any(
            not isinstance(solution.get(name), str) or not solution[name]
            for name in required_fields
        ):
            raise RuntimeError("Solver returned an incomplete GeeTest v4 solution")

        # STEP-04: Return the complete solution from getValidate() and submit the form.
        applied = driver.execute_script(
            "return window.__captchaSolverGeeTest4.apply(arguments[0])",
            {name: solution[name] for name in required_fields},
        )
        if (
            not isinstance(applied, dict)
            or applied.get("captcha_output") != solution["captcha_output"]
        ):
            raise RuntimeError("The GeeTest v4 solution was not applied to the widget")
        submit = wait_for_xpath(driver, SUBMIT_LOCATOR)
        driver.execute_script("arguments[0].click();", submit)
        print("GeeTest v4 solution submitted")

        # STEP-05: Require an explicit successful verification response from the page.
        result = wait_for_css(driver, RESULT_SELECTOR)
        message = result.text.strip()
        result_role = (result.get_attribute("role") or "").lower()
        if result_role == "alert":
            raise RuntimeError(f"The page rejected the GeeTest v4 solution: {message}")
        details = result.find_element("xpath", "..").text.strip()
        if '"result": "success"' not in details:
            raise RuntimeError("The page did not confirm GeeTest v4 verification success")
        print(f"Page confirmation:\n{details}")
        time.sleep(5)


if __name__ == "__main__":
    main()
