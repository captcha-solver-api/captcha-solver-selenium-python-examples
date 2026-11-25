"""Browser regression tests that use local HTML and never call the solver API."""

from urllib.parse import quote

import pytest
from selenium import webdriver
from selenium.common.exceptions import JavascriptException
from selenium.webdriver.chrome.options import Options

from examples.common import fill_response_field


@pytest.fixture
def browser():
    options = Options()
    options.add_argument("--headless=new")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    driver = webdriver.Chrome(options=options)
    try:
        yield driver
    finally:
        driver.quit()


def test_fill_response_field_updates_local_page_and_dispatches_events(browser):
    html = """
    <textarea name="captcha-response"></textarea>
    <script>
      window.receivedEvents = [];
      const field = document.querySelector('[name="captcha-response"]');
      field.addEventListener('input', () => window.receivedEvents.push('input'));
      field.addEventListener('change', () => window.receivedEvents.push('change'));
    </script>
    """
    browser.get(f"data:text/html;charset=utf-8,{quote(html)}")

    fill_response_field(browser, "captcha-response", "local-test-token")

    state = browser.execute_script(
        """
        const field = document.querySelector('[name="captcha-response"]');
        return {value: field.value, events: window.receivedEvents};
        """
    )
    assert state == {
        "value": "local-test-token",
        "events": ["input", "change"],
    }


def test_fill_response_field_fails_when_target_field_is_missing(browser):
    browser.get("data:text/html,<p>Local test page</p>")

    with pytest.raises(JavascriptException, match="Response field missing-field was not found"):
        fill_response_field(browser, "missing-field", "local-test-token")
