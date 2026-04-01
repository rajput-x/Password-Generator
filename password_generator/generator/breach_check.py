import hashlib
import urllib.error
import urllib.request


PWNED_API_BASE = "https://api.pwnedpasswords.com/range/"


def check_password_breach_count(password, timeout=4):
    """
    Uses HaveIBeenPwned k-anonymity API.
    Returns breach count (int), 0 when safe, or None when unavailable.
    """
    if not password:
        return None

    digest = hashlib.sha1(password.encode("utf-8")).hexdigest().upper()
    prefix, suffix = digest[:5], digest[5:]

    request = urllib.request.Request(
        f"{PWNED_API_BASE}{prefix}",
        headers={"User-Agent": "PasswordGenerator/2.0"},
    )

    try:
        with urllib.request.urlopen(request, timeout=timeout) as response:
            body = response.read().decode("utf-8", errors="ignore")
    except (urllib.error.URLError, TimeoutError, ValueError):
        return None

    for line in body.splitlines():
        if ":" not in line:
            continue
        hash_suffix, count = line.split(":", 1)
        if hash_suffix.strip().upper() == suffix:
            try:
                return int(count.strip())
            except ValueError:
                return None
    return 0
