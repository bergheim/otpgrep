# otpgrep

Extract a one-time login code from message text.

Reads text on stdin, prints one code on stdout, exits 0. Prints nothing and
exits non-zero when there is no code or when the match is ambiguous.

```sh
otpgrep < message.txt
otpgrep < message.txt | wl-copy
```

Intended caller is a mako action on a login-code notification: read the
notification body with `makoctl`, pipe it through `otpgrep`, copy the result.
Codes are never copied on arrival, only on an explicit action.

## Extraction rules

- Require a keyword near the digits: code, otp, kode, engangskode.
- Match 4-8 digits adjacent to that keyword.
- Ignore amounts, discounts, dates, order ids and account numbers.
- Fail rather than guess when more than one candidate matches.

## Tests

Fixtures are redacted, expired messages under `tests/`. Format is not settled
yet.
