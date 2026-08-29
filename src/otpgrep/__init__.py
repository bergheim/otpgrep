"""Extract a one-time login code from message text."""

import html
import re
import sys

KEYWORD = re.compile(
    r"engangskode|sikkerhetskode|verifiseringskode|bekreftelseskode"
    r"|verification|passcode|one-time|otp|code|kode|pin",
    re.IGNORECASE,
)

# Digits that identify something other than a login code.
DISQUALIFIER = re.compile(
    r"invoice|faktura|order|ordre|konto|account|client number|kundenummer"
    r"|customer|reference|referanse|zip|postnummer|vat|orgnr|phone|tel|fax",
    re.IGNORECASE,
)

MONEY = re.compile(r"kr|nok|usd|eur|sek|dkk|[$€£%]", re.IGNORECASE)

# A timestamp or a date reads as 4 digits next to a keyword often enough that
# mail headers alone would produce a false code.
DATE_CONTEXT = re.compile(
    r"(?:jan|feb|mar|apr|may|jun|jul|aug|sep|oct|nov|dec)[a-z]*\s+\d{1,2}[\s,]*$"
    r"|\d{1,2}:\d{2}(?::\d{2})?\s*$",
    re.IGNORECASE,
)

STYLE_OR_SCRIPT = re.compile(r"<(style|script)\b.*?</\1>", re.IGNORECASE | re.DOTALL)
TAG = re.compile(r"<[^>]+>")

# Hyphen and word characters on either side rule out dates, phone numbers,
# invoice ids and anything embedded in a longer token. A dot only disqualifies
# when a digit sits on the far side of it, so "code is 602214." still matches
# while "16.05.2026" and "1234.56" do not.
CANDIDATE = re.compile(r"(?<![\w\-])(?<!\d\.)\d{4,8}(?![\w\-])(?!\.\d)")

KEYWORD_WINDOW = 80
DISQUALIFIER_WINDOW = 30
MONEY_WINDOW = 12


def _near(
    pattern: re.Pattern[str], text: str, start: int, end: int, window: int
) -> bool:
    before = text[max(0, start - window) : start]
    after = text[end : end + window]
    return bool(pattern.search(before) or pattern.search(after))


def strip_html(text: str) -> str:
    """Return ``text`` without markup when it carries HTML."""
    if "<" not in text:
        return text
    text = STYLE_OR_SCRIPT.sub(" ", text)
    text = re.sub(r"(?i)<br\s*/?>|</(p|div|tr|h[1-6])>", "\n", text)
    return html.unescape(TAG.sub(" ", text))


def extract(text: str) -> str | None:
    """Return the login code in ``text``, or None when absent or ambiguous."""
    text = strip_html(text)
    keywords = [m.span() for m in KEYWORD.finditer(text)]
    if not keywords:
        return None

    best: dict[str, int] = {}
    for match in CANDIDATE.finditer(text):
        start, end = match.span()
        if _near(DISQUALIFIER, text, start, end, DISQUALIFIER_WINDOW):
            continue
        if _near(MONEY, text, start, end, MONEY_WINDOW):
            continue
        if DATE_CONTEXT.search(text[max(0, start - 24) : start]):
            continue

        distance = min(
            start - k_end if k_end <= start else k_start - end
            for k_start, k_end in keywords
            if k_end <= start or k_start >= end
        )
        if distance > KEYWORD_WINDOW:
            continue

        value = match.group()
        if distance < best.get(value, KEYWORD_WINDOW + 1):
            best[value] = distance

    if not best:
        return None

    ranked = sorted(best.items(), key=lambda item: item[1])
    # ponytail: nearest keyword wins, exact ties are rejected. Score by line
    # position too if a real message ever puts two codes the same distance out.
    if len(ranked) > 1 and ranked[0][1] == ranked[1][1]:
        return None
    return ranked[0][0]


def main() -> int:
    code = extract(sys.stdin.read())
    if code is None:
        return 1
    print(code)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
