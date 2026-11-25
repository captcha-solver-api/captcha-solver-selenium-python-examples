![Captcha Solver Selenium Python Examples](assets/selenium-python-examples-banner.png)

# Captcha solving examples with Python and SeleniumBase

Examples of solving popular captcha types with
[`captcha-solver-api`](https://pypi.org/project/captcha-solver-api/),
[Selenium](https://www.selenium.dev/), and
[`seleniumbase`](https://seleniumbase.io/).

The browser examples show how to:

1. Open a page and collect captcha parameters.
2. Send a task to Captcha Solver.
3. Apply the solution in the browser.
4. Check that the page accepted the solution when it exposes a verification result, or confirm
   delivery to the page callback when it does not.

The image, coordinates, and captured Yandex challenge examples instead read test images from
`assets/`, submit them to the API, and print recognized text, coordinates, or the required number
of slider-arrow clicks. They do not open a browser.

## Installation

Requirements:

- Python 3.10 or newer
- Google Chrome for browser-based examples
- A Captcha Solver API key with a positive balance

```bash
git clone https://github.com/captcha-solver-api/captcha-solver-selenium-python-examples.git
cd captcha-solver-selenium-python-examples
python -m venv .venv
```

On macOS and Linux:

```bash
source .venv/bin/activate
python -m pip install -r requirements.txt
cp .env.example .env
```

On Windows:

```powershell
.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
Copy-Item .env.example .env
```

Set your API key in `.env`:

```dotenv
CAPTCHA_API_KEY=your_api_key
CAPTCHA_SOLVE_TIMEOUT=300
```

`CAPTCHA_SOLVE_TIMEOUT` controls how many seconds `CaptchaClient.solve()` waits while polling.
The examples default to 300 seconds when the variable is omitted.

The callback reCAPTCHA v2 example needs its own page integration settings:

```dotenv
RECAPTCHA_V2_CALLBACK_TARGET_URL=https://example.com/page_with_recaptcha_v2_callback
RECAPTCHA_V2_CALLBACK_NAME=verifyRecaptcha
RECAPTCHA_V2_CALLBACK_SUCCESS_SELECTOR=.captcha-success
```

The `.env.example` file contains official public demo URLs for reCAPTCHA v2 and Yandex
SmartCaptcha. All URLs ending in `.example` are intentionally non-working placeholders. Replace
them with pages you own or are authorized to test before running the matching examples.

## Run

Run commands from the repository root.

reCAPTCHA:

```bash
python examples/recaptcha/recaptcha_v2.py
python examples/recaptcha/recaptcha_v2_proxy.py
python examples/recaptcha/recaptcha_v2_callback.py
python examples/recaptcha/recaptcha_v2_callback_proxy.py
python examples/recaptcha/recaptcha_v2_enterprise.py
python examples/recaptcha/recaptcha_v3.py
python examples/recaptcha/recaptcha_v3_enterprise.py
```

Cloudflare:

```bash
python examples/cloudflare/cloudflare_turnstile.py
python examples/cloudflare/cloudflare_challenge_page.py
```

Tencent:

```bash
python examples/tencent/tencent.py
```

GeeTest:

```bash
python examples/geetest/geetest_v3.py
python examples/geetest/geetest_v4.py
```

Yandex SmartCaptcha:

```bash
python examples/yandex/yandex_smartcaptcha.py
python examples/yandex/yandex_smartcaptcha_image.py
python examples/yandex/yandex_smartcaptcha_kaleidoscope.py
```

Local image and coordinates tasks:

```bash
python examples/image/image_to_text.py
python examples/image/image_to_text_digits.py
python examples/image/image_to_text_math.py
python examples/coordinates/coordinates.py
```

The reCAPTCHA v2 and Yandex SmartCaptcha browser examples use their official demos by default.
Set the matching `*_TARGET_URL` variable to use another page you are authorized to test. Proxy
examples additionally require the `PROXY_*` variables from `.env`.

## Examples

| Captcha | File |
|---|---|
| reCAPTCHA v2 | [`recaptcha_v2.py`](examples/recaptcha/recaptcha_v2.py) |
| reCAPTCHA v2 Enterprise | [`recaptcha_v2_enterprise.py`](examples/recaptcha/recaptcha_v2_enterprise.py) |
| reCAPTCHA v2 + proxy | [`recaptcha_v2_proxy.py`](examples/recaptcha/recaptcha_v2_proxy.py) |
| reCAPTCHA v2 callback | [`recaptcha_v2_callback.py`](examples/recaptcha/recaptcha_v2_callback.py) |
| reCAPTCHA v2 callback + proxy | [`recaptcha_v2_callback_proxy.py`](examples/recaptcha/recaptcha_v2_callback_proxy.py) |
| reCAPTCHA v3 | [`recaptcha_v3.py`](examples/recaptcha/recaptcha_v3.py) |
| reCAPTCHA v3 Enterprise | [`recaptcha_v3_enterprise.py`](examples/recaptcha/recaptcha_v3_enterprise.py) |
| Cloudflare Turnstile | [`cloudflare_turnstile.py`](examples/cloudflare/cloudflare_turnstile.py) |
| Cloudflare Challenge | [`cloudflare_challenge_page.py`](examples/cloudflare/cloudflare_challenge_page.py) |
| GeeTest v3 | [`geetest_v3.py`](examples/geetest/geetest_v3.py) |
| GeeTest v4 | [`geetest_v4.py`](examples/geetest/geetest_v4.py) |
| Tencent CAPTCHA | [`tencent.py`](examples/tencent/tencent.py) |
| Yandex SmartCaptcha | [`yandex_smartcaptcha.py`](examples/yandex/yandex_smartcaptcha.py) |
| Yandex SmartCaptcha image | [`yandex_smartcaptcha_image.py`](examples/yandex/yandex_smartcaptcha_image.py) |
| Yandex SmartCaptcha Kaleidoscope | [`yandex_smartcaptcha_kaleidoscope.py`](examples/yandex/yandex_smartcaptcha_kaleidoscope.py) |
| Image captcha, text | [`image_to_text.py`](examples/image/image_to_text.py) |
| Image captcha, digits | [`image_to_text_digits.py`](examples/image/image_to_text_digits.py) |
| Image captcha, math | [`image_to_text_math.py`](examples/image/image_to_text_math.py) |
| Coordinates | [`coordinates.py`](examples/coordinates/coordinates.py) |

## GeeTest

Set the two target URLs in `.env` before running the examples:

```dotenv
GEETEST_V3_TARGET_URL=https://geetest-v3-placeholder.example/demo
GEETEST_V4_TARGET_URL=https://geetest-v4-placeholder.example/demo
```

Replace these placeholders with pages you own or are authorized to test.

GeeTest v3 uses a dynamic, single-use `challenge`. The example requests a fresh `gt` and
`challenge` pair from the target's initialization endpoint before opening its widget. It solves
the task first, then opens the target page, fills `geetest_challenge`, `geetest_validate`, and
`geetest_seccode`, submits the form, and checks the page's response. Adapt the initialization
endpoint when using a different site.

GeeTest v4 does not use the v3 `gt/challenge` pair. The example intercepts `initGeetest4` to
capture `captchaId`, solves the version 4 task, and returns `captcha_id`, `lot_number`,
`pass_token`, `gen_time`, and `captcha_output` together through the widget's `getValidate()`.
It then submits the form and checks the page's verification response.

## Yandex SmartCaptcha

After installation, set `CAPTCHA_API_KEY` in `.env` and run:

```bash
python examples/yandex/yandex_smartcaptcha.py
```

Captured image challenges can be checked separately:

```bash
python examples/yandex/yandex_smartcaptcha_image.py
python examples/yandex/yandex_smartcaptcha_kaleidoscope.py
```

The example uses the official demo at `https://smartcaptcha.cloud.yandex.ru/demo` when
`YANDEX_TARGET_URL` and the optional generic `TARGET_URL` fallback are not set.
The example reads the widget's `data-sitekey` and the browser's User-Agent,
requests a token using `YandexSmartCaptchaTaskProxyless`, fills `smart-token`,
and submits the form. It reports success only after the page returns
`Hello, user!`.

The example uses the same `.env` configuration, shared API client, and
console logging as the other examples. Running it creates a paid solving task.

To adapt it to a page you are authorized to test, set `YANDEX_TARGET_URL` and
update `SITEKEY_SELECTOR`, `SUBMIT_LOCATOR`, and the success check in the script.
If your application uses a callback instead of reading `smart-token`, adapt
the token delivery to that callback as well.

- [Yandex SmartCaptcha task parameters](https://captcha-solver.com/en/docs/captcha-types#yandex-smartcaptcha)
- [Yandex SmartCaptcha code examples](https://captcha-solver.com/en/docs/code-examples#yandex-smartcaptcha)

## Tencent CAPTCHA

Tencent requires a target page that constructs `TencentCaptcha`. Replace the placeholder URL in
`.env` with a page you are authorized to test:

```dotenv
TENCENT_TARGET_URL=https://tencent-captcha-placeholder.example/demo
```

The example intercepts the constructor and confirms that the ticket and `randstr` were delivered
to the page callback. Pages that need an explicit trigger or render a success element may
optionally define `TENCENT_TRIGGER_SELECTOR` or `TENCENT_SUCCESS_SELECTOR`; neither is required
for a page that opens the CAPTCHA automatically and reports through its callback.

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
python -m ruff check .
python -m ruff format --check .
```

## Documentation

- [Captcha Solver API](https://captcha-solver.com/en/docs/captcha-types)
- [Python SDK](https://github.com/captcha-solver-api/python-sdk)

## License

[MIT](LICENSE.md)
