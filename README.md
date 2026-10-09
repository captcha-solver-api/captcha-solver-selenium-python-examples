![Captcha Solver Selenium Python Examples](assets/selenium-python-examples-banner.png)

# Captcha solving examples with Python and SeleniumBase

Examples of solving popular captcha types with
[`captcha-solver-api`](https://pypi.org/project/captcha-solver-api/),
[Selenium](https://www.selenium.dev/), and
[`seleniumbase`](https://seleniumbase.io/).

Each example shows how to:

1. Open a page and collect captcha parameters.
2. Send a task to Captcha Solver.
3. Apply the solution in the browser.
4. Check that the page accepted the solution.

## Installation

Requirements:

- Python 3.9 or newer
- Google Chrome
- A Captcha Solver API key with a positive balance

```bash
git clone https://github.com/captcha-solver-api/captcha-solver-selenium-python-examples.git
cd captcha-solver-selenium-python-examples
python -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
cp .env.example .env
```

On Windows:

```powershell
.venv\Scripts\Activate.ps1
Copy-Item .env.example .env
```

Set your API key in `.env`:

```dotenv
CAPTCHA_API_KEY=your_api_key
```

## Run

```bash
python examples/recaptcha_v2.py
```

The reCAPTCHA v2 example uses the official Google demo by default. Set
`TARGET_URL` in `.env` to run another example against a page you are
authorized to test.

## Examples

| Captcha | File |
|---|---|
| reCAPTCHA v2 | [`recaptcha_v2.py`](examples/recaptcha_v2.py) |
| reCAPTCHA v2 + proxy | [`recaptcha_v2_proxy.py`](examples/recaptcha_v2_proxy.py) |
| reCAPTCHA v2 callback | [`recaptcha_v2_callback_variant1.py`](examples/recaptcha_v2_callback_variant1.py) |
| reCAPTCHA v2 callback, automatic discovery | [`recaptcha_v2_callback_variant2.py`](examples/recaptcha_v2_callback_variant2.py) |
| reCAPTCHA v2 callback + proxy | [`recaptcha_v2_callback_proxy.py`](examples/recaptcha_v2_callback_proxy.py) |
| reCAPTCHA v3 | [`recaptcha_v3.py`](examples/recaptcha_v3.py) |
| reCAPTCHA v3 interception | [`recaptcha_v3_extended_js_script.py`](examples/recaptcha_v3_extended_js_script.py) |
| Cloudflare Turnstile | [`cloudflare_turnstile.py`](examples/cloudflare_turnstile.py) |
| Cloudflare Challenge | [`cloudflare_challenge_page.py`](examples/cloudflare_challenge_page.py) |
| Tencent CAPTCHA | [`tencent.py`](examples/tencent.py) |
| Image captcha, screenshot | [`normal_captcha_screenshot.py`](examples/normal_captcha_screenshot.py) |
| Image captcha, canvas | [`normal_captcha_canvas.py`](examples/normal_captcha_canvas.py) |
| Image captcha with parameters | [`normal_captcha_screenshot_params.py`](examples/normal_captcha_screenshot_params.py) |
| Coordinates | [`coordinates.py`](examples/coordinates.py) |

## Tencent CAPTCHA

Tencent requires your own target page and selectors:

```dotenv
TARGET_URL=https://your-site.example/tencent-captcha
TENCENT_TRIGGER_SELECTOR=#open-captcha
TENCENT_SUCCESS_SELECTOR=.verification-success
```

Leave `TENCENT_TRIGGER_SELECTOR` empty if the page opens the captcha
automatically.

## Proxy

```dotenv
PROXY_TYPE=http
PROXY_ADDRESS=proxy.example.com
PROXY_PORT=8080
PROXY_LOGIN=
PROXY_PASSWORD=
```

The browser and API task use the same proxy.

## Checks

```bash
python -m pip install ruff
ruff check .
ruff format --check .
```

## Documentation

- [Captcha Solver API](https://captcha-solver.com/en/docs/captcha-types)
- [Python SDK](https://github.com/captcha-solver-api/python-sdk)

## License

[MIT](LICENSE.md)
