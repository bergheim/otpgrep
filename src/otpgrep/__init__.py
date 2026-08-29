"""Extract a one-time login code from message text."""

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

# Hyphen and word characters on either side rule out dates, phone numbers,
# invoice ids and anything embedded in a longer token.
CANDIDATE = re.compile(r"(?<![\w\-.])\d{4,8}(?![\w\-.])")

KEYWORD_WINDOW = 80
DISQUALIFIER_WINDOW = 30
MONEY_WINDOW = 12


def _near(
    pattern: re.Pattern[str], text: str, start: int, end: int, window: int
) -> bool:
    before = text[max(0, start - window) : start]
    after = text[end : end + window]
    return bool(pattern.search(before) or pattern.search(after))


def extract(text: str) -> str | None:
    """Return the login code in ``text``, or None when absent or ambiguous."""
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
