# Captcha Solver Selenium Python Examples

Runnable SeleniumBase examples for the official
[`captcha-solver-api`](https://pypi.org/project/captcha-solver-api/) Python SDK.
The scripts open public captcha demo pages, extract the live parameters or image,
send a task through the Captcha Solver API, and apply the answer in the browser.

## Installation

Python 3.9 or newer and Chrome are required.

```bash
git clone https://github.com/captcha-solver-api/captcha-solver-selenium-python-examples.git
cd captcha-solver-selenium-python-examples
python -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
cp .env.example .env
```

On Windows, activate the environment with `.venv\Scripts\activate`.

Set your API key in `.env`:

```dotenv
CAPTCHA_API_KEY=your_api_key
```

Proxy examples also require `PROXY_TYPE`, `PROXY_ADDRESS`, `PROXY_PORT`, and,
when necessary, `PROXY_LOGIN` and `PROXY_PASSWORD`.

## Examples

| Script | Browser flow |
|---|---|
| `recaptcha_v2.py` | Extract the sitekey, solve reCAPTCHA v2, fill the response field, and submit |
| `recaptcha_v2_proxy.py` | Use the same proxy for Selenium and the API task |
| `recaptcha_v2_callback_variant1.py` | Invoke the callback whose name is known by the demo |
| `recaptcha_v2_callback_variant2.py` | Discover the callback automatically in reCAPTCHA internals |
| `recaptcha_v2_callback_proxy.py` | Solve the callback flow through a matching proxy |
| `recaptcha_v3.py` | Extract `sitekey` and `action` from page scripts and apply the token |
| `recaptcha_v3_extended_js_script.py` | Entry point for the script-inspection v3 flow |
| `cloudflare_turnstile.py` | Solve a standalone Turnstile widget and submit the form |
| `cloudflare_challenge_page.py` | Intercept `turnstile.render`, solve the challenge, and invoke its callback |
| `normal_captcha_screenshot.py` | Screenshot the captcha element and enter the recognized text |
| `normal_captcha_canvas.py` | Extract the image through canvas and enter the recognized text |
| `normal_captcha_screenshot_params.py` | Add numeric and length hints to image recognition |
| `coordinates.py` | Extract a click-captcha image and click the returned coordinates |

Run any example from the repository root:

```bash
python examples/recaptcha_v2.py
python examples/recaptcha_v2_callback_variant2.py
python examples/cloudflare_turnstile.py
python examples/cloudflare_challenge_page.py
python examples/normal_captcha_canvas.py
python examples/coordinates.py
```

The browser remains visible so the full flow can be observed. Every script uses
fresh values from the loaded page instead of storing challenge parameters.

## Proxy examples

The proxy used to load a captcha page must match the proxy sent in the API task.
Configure it in `.env`, then run:

```bash
python examples/recaptcha_v2_proxy.py
python examples/recaptcha_v2_callback_proxy.py
```

## Unsupported comparison scenarios

The SDK currently has no MTCaptcha or text-question task, and reCAPTCHA v3 is
proxyless. Those examples are intentionally omitted rather than sending an
unsupported task shape to the API.

## Documentation

- [Captcha Solver API documentation](https://captcha-solver.com/en/docs/captcha-types)
- [Python SDK](https://github.com/captcha-solver-api/python-sdk)

Use these examples only on websites you own or are authorized to automate.

## License

MIT. See [LICENSE.md](LICENSE.md) and [THIRD_PARTY_NOTICES.md](THIRD_PARTY_NOTICES.md).
