"""Password strength: the rules everyone writes, then the ones that matter.

The rule-based checker below is the version every tutorial ships, and it is
the weakest part of the file. `Password123@` passes all five rules and is
still a terrible password. What actually separates a strong password from a
weak one is how many guesses it survives, which is what the entropy estimate
and the breach lookup are for.

    python passwordstrengthchecker.py           # scores the sample list
    python passwordstrengthchecker.py --online  # also queries Have I Been Pwned
    python passwordstrengthchecker.py --test    # unit tests, no network
"""

import hashlib
import math
import re
import string
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
COMMON_FILE = HERE / "top-passwords.txt"


def rule_based(password: str) -> list[str]:
    """Every rule the classic checker enforces, reported all at once.

    The usual version uses `elif`, so it names one problem per run and the
    user fixes them one weary round-trip at a time. Collecting the whole list
    costs nothing and is the single biggest usability win available here.
    """
    feedback = []
    if len(password) < 8:
        feedback.append("Use at least 8 characters.")
    if not re.search(r"[a-z]", password):
        feedback.append("Add a lowercase letter.")
    if not re.search(r"[A-Z]", password):
        feedback.append("Add an uppercase letter.")
    if not re.search(r"[0-9]", password):
        feedback.append("Add a digit.")
    if not re.search(r"[^A-Za-z0-9]", password):
        feedback.append("Add a symbol.")
    return feedback


def strength(password: str) -> tuple[str, list[str]]:
    """The verdict the rules alone can give: Strong, or a list of complaints."""
    issues = rule_based(password)
    return ("Strong" if not issues else "Weak"), issues


def entropy_bits(password: str) -> float:
    """Guessing cost, assuming the attacker knows only which pools were used.

    This is an upper bound and a generous one: it treats every character as an
    independent random draw. A password built out of a dictionary word scores
    far higher here than it deserves, which is exactly why the blacklist and
    the breach lookup exist.
    """
    pool = 0
    if any(c.islower() for c in password):
        pool += 26
    if any(c.isupper() for c in password):
        pool += 26
    if any(c.isdigit() for c in password):
        pool += 10
    if any(c in string.punctuation for c in password):
        pool += len(string.punctuation)
    return len(password) * math.log2(max(pool, 1))


def has_runs(p: str) -> bool:
    """Repeats and keyboard walks -- the patterns entropy cannot see."""
    return bool(re.search(r"(.)\1\1", p)) or bool(
        re.search(r"012|123|234|abc|qwe", p.lower()))


def load_common() -> set[str]:
    """The blacklist, or an empty set if the file was never downloaded."""
    if not COMMON_FILE.exists():
        return set()
    return {line.strip().lower()
            for line in COMMON_FILE.read_text(encoding="utf-8").splitlines()
            if line.strip()}


COMMON = load_common()


def is_common(password: str) -> bool:
    return password.lower() in COMMON


def hibp_count(password: str) -> int:
    """How many breaches this password appears in, without sending it anywhere.

    Only the first five characters of the SHA-1 leave this machine. The server
    returns every suffix sharing that prefix -- some hundreds of them -- and
    the match is made locally, so the service never learns which one was
    asked about. That is the k-anonymity trick, and it is the only reason
    sending a password to a third party is defensible at all.
    """
    import urllib.request

    sha1 = hashlib.sha1(password.encode("utf-8")).hexdigest().upper()
    prefix, suffix = sha1[:5], sha1[5:]
    url = f"https://api.pwnedpasswords.com/range/{prefix}"
    with urllib.request.urlopen(url, timeout=10) as response:
        body = response.read().decode("utf-8")
    for line in body.splitlines():
        found, count = line.split(":")
        if found.strip() == suffix:
            return int(count)
    return 0


LEVELS = ["Very Weak", "Weak", "Fair", "Good", "Strong", "Excellent"]


def full_check(password: str, online: bool = False) -> dict:
    """All five signals, scored together.

    `breaches` is None rather than 0 when the lookup did not happen. The
    difference matters: 0 means the service was asked and had never seen it,
    None means nobody checked, and collapsing the two would hand a password
    a point it never earned.
    """
    issues = rule_based(password)
    bits = entropy_bits(password)
    common = is_common(password)
    breaches = None
    if online:
        try:
            breaches = hibp_count(password)
        except Exception as exc:                      # offline, blocked, down
            print(f"  (breach lookup unavailable: {exc})")

    score = 0
    if len(password) >= 12:
        score += 1
    if not issues:
        score += 1
    if bits >= 60:
        score += 1
    if not common:
        score += 1
    if breaches == 0:
        score += 1

    return {
        "level": LEVELS[score],
        "score": score,
        "bits": round(bits, 1),
        "issues": issues,
        "common": common,
        "patterned": has_runs(password),
        "breaches": breaches,
    }


SAMPLES = [
    "Password123",
    "Password",
    "password123",
    "PASSWORD123",
    "Password@",
    "Password123@",
    "correct horse battery staple",
    "aaa111AAA!!!",
    "7#kQx2!vLm9Zt4Rd",
]


def main(online: bool = False) -> None:
    print(f"{'password':32} {'verdict':11} {'bits':>6}  notes")
    print("-" * 78)
    for password in SAMPLES:
        result = full_check(password, online=online)
        notes = []
        if result["issues"]:
            notes.append(f"{len(result['issues'])} rule(s) failed")
        if result["common"]:
            notes.append("on the common list")
        if result["patterned"]:
            notes.append("repeats or a keyboard walk")
        if result["breaches"]:
            notes.append(f"seen in {result['breaches']:,} breaches")
        print(f"{password:32} {result['level']:11} {result['bits']:6.1f}  "
              f"{'; '.join(notes) or 'nothing flagged'}")
    if not online:
        print("\nBreach lookup skipped. Re-run with --online to include it.")
    if not COMMON:
        print(f"No blacklist at {COMMON_FILE.name}, so the common-password "
              f"check passed everything by default.")


if __name__ == "__main__":
    if "--test" in sys.argv:
        import unittest

        class TestChecker(unittest.TestCase):
            def test_rules_report_everything_at_once(self):
                self.assertEqual(len(rule_based("abc")), 4)

            def test_strong_password_has_no_issues(self):
                self.assertEqual(strength("Password123@")[0], "Strong")

            def test_entropy_grows_with_length(self):
                self.assertLess(entropy_bits("Ab1!"), entropy_bits("Ab1!Ab1!"))

            def test_runs_detected(self):
                self.assertTrue(has_runs("aaa123"))
                self.assertFalse(has_runs("7#kQx2!vLm9Zt4Rd"))

            def test_unchecked_breaches_stay_none(self):
                self.assertIsNone(full_check("Password123@")["breaches"])

        unittest.main(argv=sys.argv[:1], exit=False)
    else:
        main(online="--online" in sys.argv)
