# otpgrep

Extract a one-time login code from message text.

Reads text on stdin, prints one code on stdout, exits 0. Prints nothing and
exits non-zero when there is no code or when the match is ambiguous.

```sh
otpgrep < message.txt
otpgrep < message.txt | wl-copy
```

A candidate is 4-8 digits that no word character, hyphen or dot touches, so
dates, phone numbers and ids embedded in longer tokens never qualify. The
candidate closest to a keyword wins; an exact tie between two different numbers
is treated as ambiguous and fails.

Intended caller is a mako action on a login-code notification: read the
notification body with `makoctl`, pipe it through `otpgrep`, copy the result.
Codes are never copied on arrival, only on an explicit action.

## Extraction rules

- Require a keyword near the digits: code, otp, kode, engangskode.
- Match 4-8 digits adjacent to that keyword.
- Ignore amounts, discounts, dates, order ids and account numbers.
- Fail rather than guess when more than one candidate matches.

## Development

```sh
uv sync
uv run pytest
uv run ruff check .
```

## Tests

Fixtures live under `tests/`, one file per sender. Each is a real message that
has been redacted: recipient, personal names, customer and invoice numbers are
replaced, and every code is rewritten to a fake value.

`tests/expected.tsv` maps a fixture to its expected result: either the code the
extractor must print, or `FAIL` when it must exit non-zero.

HTML-only mail (TikTok, OpenAI sign-in alerts) has no plain text part and is
not represented yet.
