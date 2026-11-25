"""Solve GeeTest v3 on a configured demo page with SeleniumBase.

What it does:
    Requests a fresh ``gt`` and ``challenge`` pair before the GeeTest widget can consume it,
    solves ``GeeTestTaskProxyless``, opens the target page, inserts ``challenge``, ``validate``,
    and ``seccode`` into the form, submits it, and checks the page's verification response.

To use this example on another page, change the target URL and inspect how that site obtains its
fresh GeeTest initialization parameters. The initialization endpoint, response fields, solution
fields, submission control, and acceptance indicator are site-specific.

How it works:
    STEP-01 - Start the browser and SDK client without opening the GeeTest widget.
    STEP-02 - Request fresh initialization parameters directly from the page's init endpoint.
    STEP-03 - Create and solve the proxyless GeeTest v3 task.
    STEP-04 - Open the target page, insert all three solution fields, and submit the form.
    STEP-05 - Require an explicit successful verification response from the page.
"""

import json
import sys
import time
from pathlib import Path
from urllib.parse import urlencode, urljoin

from captcha_solver_api.tasks import GeeTestTaskProxyless
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.common.by import By
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
INIT_URL = urljoin(URL, "/api/v1/captcha-demo/gee-test/init-params")


@logged_example
def main() -> None:
    # STEP-01: Start the browser and SDK client without opening the GeeTest widget.
    with Driver(browser="chrome", headless=False) as driver, create_client() as client:
        # STEP-02: Request fresh initialization parameters directly from the page's init endpoint.
        params = None
        driver.set_page_load_timeout(45)
        for attempt in range(1, 4):
            try:
                query = urlencode({"t": time.time_ns()})
                driver.get(f"{INIT_URL}?{query}")
                payload = json.loads(driver.find_element(By.TAG_NAME, "body").text)
                params = payload.get("body", payload)
                if isinstance(params, dict) and params.get("gt") and params.get("challenge"):
                    break
            except (TimeoutException, json.JSONDecodeError):
                if attempt < 3:
                    print(f"GeeTest init request failed; retrying ({attempt + 1}/3)")
                    time.sleep(2)
                    continue
                raise RuntimeError(
                    "The GeeTest v3 init endpoint did not return valid parameters"
                ) from None
            if attempt == 3:
                raise RuntimeError(
                    "The GeeTest v3 init endpoint did not return fresh gt/challenge values"
                )
            print(f"GeeTest init response was incomplete; retrying ({attempt + 1}/3)")
            time.sleep(2)

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
                websiteURL=URL,
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

        # STEP-04: Open the target page, insert all three solution fields, and submit the form.
        try:
            driver.get(URL)
        except TimeoutException:
            print("Target page load timed out; continuing with the initialized content")
        for name in required_fields:
            wait_for_css(driver, f"[name='geetest_{name}']")
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
