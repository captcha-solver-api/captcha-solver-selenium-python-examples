"""Solve GeeTest v3 on a configured demo page with SeleniumBase.

What it does:
    Opens a GeeTest v3 page, intercepts the fresh ``gt`` and ``challenge`` pair passed to
    ``initGeetest``, solves ``GeeTestTaskProxyless``, inserts ``challenge``, ``validate``, and
    ``seccode`` into the form, submits it, and checks the page's verification response.

To use this example on another page, change the target URL and inspect how that site obtains its
fresh GeeTest initialization parameters. The initialization endpoint, response fields, solution
fields, submission control, and acceptance indicator are site-specific.

How it works:
    STEP-01 - Install the initGeetest interceptor and start the browser/client.
    STEP-02 - Open the page and capture its fresh GeeTest v3 initialization parameters.
    STEP-03 - Create and solve the proxyless GeeTest v3 task.
    STEP-04 - Insert all three solution fields and submit the form.
    STEP-05 - Require an explicit successful verification response from the page.
"""

import sys
import time
from pathlib import Path

from captcha_solver_api.tasks import GeeTestTaskProxyless
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.support.ui import WebDriverWait
from seleniumbase import Driver

if __package__ in {None, ""}:
    sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from examples.common import (  # noqa: E402
    create_client,
    fill_response_field,
    logged_example,
    required_env,
    wait_for_css,
    wait_for_xpath,
)

URL = required_env("GEETEST_V3_TARGET_URL")
SUBMIT_LOCATOR = "//form[@id='geetest-demo-form']//button[@type='submit']"
RESULT_SELECTOR = "p[class*='successMessage'], [role='alert']"

GEETEST_V3_INTERCEPT_SCRIPT = r"""
(() => {
  let original;
  let params;

  const wrap = value => {
    if (typeof value !== 'function' || value.__captchaSolverWrapped) return value;
    const wrapped = function(config, callback) {
      params = {...config};
      return value.call(this, config, callback);
    };
    Object.defineProperty(wrapped, '__captchaSolverWrapped', {value: true});
    return wrapped;
  };

  Object.defineProperty(window, '__captchaSolverGeeTest3', {
    value: {params: () => params}
  });

  Object.defineProperty(window, 'initGeetest', {
    configurable: true,
    enumerable: true,
    get: () => original,
    set: value => { original = wrap(value); }
  });
})();
"""


@logged_example
def main() -> None:
    # STEP-01: Install the initGeetest interceptor and start the browser/client.
    with Driver(browser="chrome", headless=False) as driver, create_client() as client:
        driver.execute_cdp_cmd(
            "Page.addScriptToEvaluateOnNewDocument",
            {"source": GEETEST_V3_INTERCEPT_SCRIPT},
        )

        # STEP-02: Open the page and capture its fresh GeeTest v3 initialization parameters.
        params = None
        driver.set_page_load_timeout(45)
        for attempt in range(1, 4):
            try:
                driver.get(URL)
            except TimeoutException:
                print(f"Page load attempt {attempt} timed out; checking initialized content")
            try:
                params = WebDriverWait(driver, 30).until(
                    lambda browser: browser.execute_script(
                        "return window.__captchaSolverGeeTest3?.params() || null"
                    )
                )
                break
            except TimeoutException:
                if attempt == 3:
                    raise RuntimeError(
                        "The GeeTest v3 page did not initialize after three attempts"
                    ) from None
                print(f"GeeTest v3 did not initialize; reopening the page ({attempt + 1}/3)")

        if not isinstance(params, dict):
            raise RuntimeError("The page returned invalid GeeTest v3 initialization parameters")
        gt = params.get("gt")
        challenge = params.get("challenge")
        if not isinstance(gt, str) or not gt or not isinstance(challenge, str) or not challenge:
            raise RuntimeError("The page did not return fresh GeeTest v3 gt/challenge values")
        print("Fresh GeeTest v3 parameters received")

        # STEP-03: Create and solve the proxyless GeeTest v3 task.
        solution = client.solve(
            GeeTestTaskProxyless(
                websiteURL=driver.current_url,
                version=3,
                gt=gt,
                challenge=challenge,
                userAgent=driver.execute_script("return navigator.userAgent"),
            )
        )
        required_fields = ("challenge", "validate", "seccode")
        if any(
            not isinstance(solution.get(name), str) or not solution[name]
            for name in required_fields
        ):
            raise RuntimeError("Solver returned an incomplete GeeTest v3 solution")

        # STEP-04: Insert all three solution fields and submit the form.
        for name in required_fields:
            fill_response_field(driver, f"geetest_{name}", solution[name])
        submit = wait_for_xpath(driver, SUBMIT_LOCATOR)
        driver.execute_script("arguments[0].click();", submit)
        print("GeeTest v3 solution submitted")

        # STEP-05: Require an explicit successful verification response from the page.
        result = wait_for_css(driver, RESULT_SELECTOR)
        message = result.text.strip()
        result_role = (result.get_attribute("role") or "").lower()
        if result_role == "alert":
            raise RuntimeError(f"The page rejected the GeeTest v3 solution: {message}")
        details = result.find_element("xpath", "following-sibling::pre[1]").text.strip()
        if '"success": true' not in details:
            raise RuntimeError("The page did not confirm GeeTest v3 verification success")
        print(f"Page confirmation: {message}\n{details}")
        time.sleep(5)


if __name__ == "__main__":
    main()
