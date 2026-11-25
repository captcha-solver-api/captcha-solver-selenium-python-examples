"""Unit tests for configuration and lifecycle helpers."""

import pytest

from examples.common import logged_example, required_env, selenium_proxy


def test_required_env_uses_first_configured_name(monkeypatch):
    monkeypatch.delenv("SPECIFIC_URL", raising=False)
    monkeypatch.setenv("FALLBACK_URL", "https://fallback.example")

    assert required_env("SPECIFIC_URL", "FALLBACK_URL") == "https://fallback.example"


def test_required_env_reports_all_missing_names(monkeypatch):
    monkeypatch.delenv("FIRST_VALUE", raising=False)
    monkeypatch.delenv("SECOND_VALUE", raising=False)

    with pytest.raises(
        RuntimeError,
        match="Set FIRST_VALUE or SECOND_VALUE in the environment or .env file",
    ):
        required_env("FIRST_VALUE", "SECOND_VALUE")


@pytest.mark.parametrize(
    ("login", "password", "expected"),
    [
        ("demo-user", "demo-password", "demo-user:demo-password@proxy.example:8080"),
        (None, None, "proxy.example:8080"),
    ],
)
def test_selenium_proxy_formats_optional_credentials(monkeypatch, login, password, expected):
    monkeypatch.setenv("PROXY_TYPE", "http")
    monkeypatch.setenv("PROXY_ADDRESS", "proxy.example")
    monkeypatch.setenv("PROXY_PORT", "8080")
    if login is None:
        monkeypatch.delenv("PROXY_LOGIN", raising=False)
        monkeypatch.delenv("PROXY_PASSWORD", raising=False)
    else:
        monkeypatch.setenv("PROXY_LOGIN", login)
        monkeypatch.setenv("PROXY_PASSWORD", password)

    assert selenium_proxy() == expected


def test_logged_example_reports_success(capsys):
    @logged_example
    def example():
        return "result"

    assert example() == "result"
    assert capsys.readouterr().out.splitlines() == ["Started", "Finished"]


def test_logged_example_reraises_and_reports_failure(capsys):
    @logged_example
    def example():
        raise ValueError("broken example")

    with pytest.raises(ValueError, match="broken example"):
        example()

    output = capsys.readouterr().out
    assert "An error occurred: broken example" in output
    assert "Example failed; check the traceback to identify the failed stage" in output
