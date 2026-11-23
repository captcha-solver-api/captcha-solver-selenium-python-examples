![Captcha Solver Selenium Python Examples](assets/selenium-python-examples-banner.png)

# Captcha solving examples with Python and SeleniumBase

Examples of solving popular captcha types with
[`captcha-solver-api`](https://pypi.org/project/captcha-solver-api/),
[Selenium](https://www.selenium.dev/), and
[`seleniumbase`](https://seleniumbase.io/).

Browser-based examples show how to:

1. Open a page and collect captcha parameters.
2. Send a task to Captcha Solver.
3. Apply the solution in the browser.
4. Check that the page accepted the solution.

Local image examples instead show how to read bundled assets, create an SDK
task, and interpret the returned text, coordinates, or click count. Applying
those results and confirming acceptance require the original browser page.

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
python -m examples.recaptcha.recaptcha_v2
```

The reCAPTCHA v2 example uses the official Google demo by default, and the
Yandex SmartCaptcha example uses the official Yandex demo. Other browser examples use the
type-specific target variables from `.env.example`; replace their `example.com` placeholders
with pages you are authorized to test. Set `CAPTCHA_SUCCESS_TEXT` to the exact confirmation text
returned by that target page.

> [!IMPORTANT]
> Browser and local examples create paid solving tasks. A solution returned by the SDK proves
> only that the service completed the task. Browser examples separately verify the configured
> page signal; local image examples cannot prove page acceptance.

## Examples

Examples are grouped by CAPTCHA provider or challenge type. Run them as Python modules from the
repository root so imports remain stable on every operating system.

| Group | Captcha | File |
|---|---|---|
| reCAPTCHA | v2 | [`recaptcha_v2.py`](examples/recaptcha/recaptcha_v2.py) |
| reCAPTCHA | v2 + proxy | [`recaptcha_v2_proxy.py`](examples/recaptcha/recaptcha_v2_proxy.py) |
| reCAPTCHA | v2 callback | [`recaptcha_v2_callback.py`](examples/recaptcha/recaptcha_v2_callback.py) |
| reCAPTCHA | v2 callback, automatic discovery | [`recaptcha_v2_callback_auto.py`](examples/recaptcha/recaptcha_v2_callback_auto.py) |
| reCAPTCHA | v2 callback + proxy | [`recaptcha_v2_callback_proxy.py`](examples/recaptcha/recaptcha_v2_callback_proxy.py) |
| reCAPTCHA | v3 | [`recaptcha_v3.py`](examples/recaptcha/recaptcha_v3.py) |
| Cloudflare | Turnstile | [`turnstile.py`](examples/cloudflare/turnstile.py) |
| Cloudflare | Challenge | [`cloudflare_challenge.py`](examples/cloudflare/cloudflare_challenge.py) |
| Tencent | Tencent CAPTCHA | [`tencent.py`](examples/tencent/tencent.py) |
| Yandex | SmartCaptcha token | [`yandex_smartcaptcha.py`](examples/yandex/yandex_smartcaptcha.py) |
| Yandex | SmartCaptcha image | [`yandex_smartcaptcha_image.py`](examples/yandex/yandex_smartcaptcha_image.py) |
| Yandex | SmartCaptcha Kaleidoscope | [`yandex_smartcaptcha_kaleidoscope.py`](examples/yandex/yandex_smartcaptcha_kaleidoscope.py) |
| Image-to-text | Browser screenshot | [`image_to_text.py`](examples/image/image_to_text.py) |
| Image-to-text | Browser canvas | [`normal_captcha_canvas.py`](examples/image/normal_captcha_canvas.py) |
| Image-to-text | Recognition parameters | [`normal_captcha_params.py`](examples/image/normal_captcha_params.py) |
| Image-to-text | Bundled image | [`image_to_text_local.py`](examples/image/image_to_text_local.py) |
| Coordinates | Browser clicks | [`coordinates.py`](examples/coordinates/coordinates.py) |
| Coordinates | Bundled image | [`coordinates_local.py`](examples/coordinates/coordinates_local.py) |

### Solution fields and proxy usage

| Task family | Proxy status | `solve()` result used by the example |
|---|---|---|
| reCAPTCHA v2/v3 | Proxyless or Proxy, as named in the file | `gRecaptchaResponse` token |
| Turnstile / Cloudflare Challenge | Proxyless | `token`; Challenge also requires a new `cf_clearance` cookie |
| Yandex SmartCaptcha token | Proxyless | `token` |
| Yandex SmartCaptcha image | Not applicable; images are uploaded directly | ordered `coordinates` |
| Yandex Kaleidoscope | Not applicable; image data is uploaded directly | slider-arrow click count string |
| Image-to-text | Not applicable; image data is uploaded directly | recognized `text` |
| Coordinates | Not applicable; image data is uploaded directly | ordered `coordinates` |
| Tencent | Proxyless | ticket/randstr solution passed to the page callback |

These values are the return value of `CaptchaClient.solve()`, not the complete transport response.
Uncaught configuration, browser, SDK, and verification errors terminate the Python process with a
non-zero exit code; browser context managers close their sessions during normal exception cleanup.

## Yandex SmartCaptcha

After installation, set `CAPTCHA_API_KEY` in `.env` and run:

```bash
python -m examples.yandex.yandex_smartcaptcha
```

Leave `YANDEX_SMARTCAPTCHA_TARGET_URL` empty to use `https://captcha-api.yandex.ru/demo`.
The example reads the widget's `data-sitekey` and the browser's User-Agent,
requests a token using `YandexSmartCaptchaTaskProxyless`, fills `smart-token`,
and submits the form. It reports success only after the page returns
`Hello, user!`.

The example loads the same `.env` template as the other examples but keeps client creation,
parameter extraction, task construction, submission, and verification in its own file.

Two image-based examples use captured assets and do not open a browser:

```bash
python -m examples.yandex.yandex_smartcaptcha_image
python -m examples.yandex.yandex_smartcaptcha_kaleidoscope
```

The image example returns ordered points to click. The Kaleidoscope example
returns the required number of slider-arrow clicks. These examples demonstrate
task creation and result handling; applying a captured result and checking that
a live page accepts it are necessarily site-specific.

## Bundled image assets

Reusable captures are grouped under `assets/`:

- `assets/image-to-text/` contains text, digits, and math CAPTCHA images plus math instructions;
- `assets/coordinates/` contains generic coordinates, fruit, and traffic-light challenges plus
  traffic-light instructions;
- `assets/yandex/` contains SmartCaptcha image, instruction, and Kaleidoscope captures.

Run the basic local examples with:

```bash
python -m examples.image.image_to_text_local
python -m examples.coordinates.coordinates_local
```

To adapt it to a page you are authorized to test, set `YANDEX_SMARTCAPTCHA_TARGET_URL` and update
`SITEKEY_SELECTOR`, `SUBMIT_LOCATOR`, and the success check in the script.
If your application uses a callback instead of reading `smart-token`, adapt
the token delivery to that callback as well.

- [Yandex SmartCaptcha task parameters](https://captcha-solver.com/en/docs/captcha-types#yandex-smartcaptcha)
- [Yandex SmartCaptcha code examples](https://captcha-solver.com/en/docs/code-examples#yandex-smartcaptcha)

## Tencent CAPTCHA

Tencent requires your own target page and selectors:

```dotenv
TENCENT_TARGET_URL=https://example.com/page_with_tencent_captcha
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
python -m unittest discover -s tests -v
```

## Documentation

- [Captcha Solver API](https://captcha-solver.com/en/docs/captcha-types)
- [Python SDK](https://github.com/captcha-solver-api/python-sdk)

## License

[MIT](LICENSE.md)
