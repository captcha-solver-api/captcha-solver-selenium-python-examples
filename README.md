# Captcha Solver Selenium Python Examples

Practical browser automation examples using Python, SeleniumBase, and the official
[`captcha-solver-api`](https://pypi.org/project/captcha-solver-api/) SDK.

Each script is split into small steps that can be copied into an existing Selenium
project: discover captcha parameters, create an API task, wait for the solution,
and apply the result in the browser.

## Included examples

| Script | Scenario |
|---|---|
| `examples/recaptcha_v2.py` | Discover and solve a reCAPTCHA v2 widget |
| `examples/recaptcha_v3.py` | Request and apply a score-based reCAPTCHA v3 token |
| `examples/turnstile.py` | Solve a standalone Cloudflare Turnstile widget |
| `examples/cloudflare_challenge.py` | Intercept the parameters and callback of a Cloudflare Challenge |
| `examples/image_to_text.py` | Screenshot an image captcha and fill the recognized text |
| `examples/coordinates.py` | Screenshot a click captcha and apply returned coordinates |

## Installation

Python 3.9 or newer and Chrome are required.

```bash
git clone https://github.com/captcha-solver-api/captcha-solver-selenium-python-examples.git
cd captcha-solver-selenium-python-examples
python -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
```

On Windows, activate the environment with `.venv\Scripts\activate`.

## Configuration

Copy the example configuration and add your API key and target page details:

```bash
cp .env.example .env
```

At minimum, set:

```dotenv
CAPTCHA_API_KEY=your_api_key
TARGET_URL=https://example.com/captcha
```

The examples deliberately use configurable target URLs and selectors. Captcha
markup differs between websites, so update `CAPTCHA_SELECTOR`, `ANSWER_SELECTOR`,
and `SUBMIT_SELECTOR` in `.env` to match the page you are automating. reCAPTCHA v3
also requires `WEBSITE_KEY`, `PAGE_ACTION`, and `MIN_SCORE`.

## Running an example

```bash
python examples/recaptcha_v2.py
python examples/turnstile.py
python examples/cloudflare_challenge.py
python examples/image_to_text.py
python examples/coordinates.py
```

The browser is visible by default so you can inspect every step. Change
`headless=False` in a script after confirming that the flow works for your page.

## Adapting the examples

Token captchas are bound to details of the page and browser session. Use fresh
parameters from the current page, submit the token before it expires, and keep
the browser proxy consistent with the proxy supplied to a proxied API task.

Cloudflare Challenge requires interception before `turnstile.render()` runs.
The challenge example installs its interception script before navigation,
captures `action`, `cData`, `chlPageData`, callback, and browser User-Agent, then
applies the returned token through the captured callback.

Use these examples only on websites you own or are authorized to automate.

## Documentation

- [Captcha Solver API documentation](https://captcha-solver.com/en/docs/captcha-types)
- [Python SDK](https://github.com/captcha-solver-api/python-sdk)

## License

MIT. See [LICENSE.md](LICENSE.md).
