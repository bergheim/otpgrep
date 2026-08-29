import subprocess
import sys
from pathlib import Path

import pytest

from otpgrep import extract

FIXTURES = Path(__file__).parent
CASES = [
    line.split("\t")
    for line in (FIXTURES / "expected.tsv").read_text().splitlines()
    if line
]


@pytest.mark.parametrize(("name", "expected"), CASES)
def test_fixture(name: str, expected: str) -> None:
    got = extract((FIXTURES / name).read_text())
    assert got == (None if expected == "FAIL" else expected)


def test_ambiguous_returns_none() -> None:
    assert extract("Your code is 111111 and your code is 222222") is None


def test_cli_exit_codes() -> None:
    run = lambda text: subprocess.run(  # noqa: E731
        [sys.executable, "-m", "otpgrep"], input=text, capture_output=True, text=True
    )
    ok = run("Your login code is 123456")
    assert (ok.returncode, ok.stdout.strip()) == (0, "123456")
    assert run("nothing to see here").returncode == 1
