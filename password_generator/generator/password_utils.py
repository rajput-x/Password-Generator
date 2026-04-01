import math
import random
import secrets
import string


AMBIGUOUS_CHARACTERS = set("O0oIl1|`'\"")
DEFAULT_PRESET_KEY = "basic_web"

COMMON_WEAK_TERMS = (
    "password",
    "admin",
    "qwerty",
    "welcome",
    "letmein",
    "iloveyou",
    "123456",
    "abc123",
)

SEQUENCE_STRINGS = (
    "abcdefghijklmnopqrstuvwxyz",
    "0123456789",
    "qwertyuiopasdfghjklzxcvbnm",
)

PASSWORD_PRESETS = {
    "basic_web": {
        "label": "Basic Web (balanced)",
        "description": "Great default for everyday accounts with balanced security and compatibility.",
        "mode": "password",
        "length": 12,
        "include_uppercase": True,
        "include_lowercase": True,
        "include_numbers": True,
        "include_symbols": False,
        "exclude_ambiguous": False,
    },
    "high_security": {
        "label": "High Security (recommended)",
        "description": "For banking, email, and critical accounts. Uses longer, fully mixed passwords.",
        "mode": "password",
        "length": 20,
        "include_uppercase": True,
        "include_lowercase": True,
        "include_numbers": True,
        "include_symbols": True,
        "exclude_ambiguous": False,
    },
    "legacy_compatible": {
        "label": "Legacy Compatible (no symbols)",
        "description": "Use when older sites reject symbols but you still want strong structure.",
        "mode": "password",
        "length": 16,
        "include_uppercase": True,
        "include_lowercase": True,
        "include_numbers": True,
        "include_symbols": False,
        "exclude_ambiguous": True,
    },
    "passphrase": {
        "label": "Passphrase Strong",
        "description": "Memorable multi-word passphrase with extra suffix protection.",
        "mode": "passphrase",
        "word_count": 6,
        "separator": "-",
        "capitalize_words": False,
        "append_number": True,
        "append_symbol": True,
    },
}

PASSPHRASE_WORDS = [
    "amber", "anchor", "apple", "atlas", "aurora", "badge", "bamboo", "beacon", "berry", "blaze",
    "breeze", "brick", "cactus", "canvas", "cedar", "chess", "cloud", "comet", "copper", "coral",
    "cosmos", "crystal", "dawn", "delta", "drift", "echo", "ember", "falcon", "field", "flame",
    "forest", "frost", "galaxy", "garden", "glacier", "gold", "harbor", "horizon", "ivory", "jungle",
    "keystone", "lantern", "legend", "lemon", "lotus", "lunar", "maple", "matrix", "meadow", "meteor",
    "mint", "mirror", "mist", "nebula", "nectar", "night", "nova", "oasis", "onyx", "opal",
    "orbit", "ocean", "pearl", "phoenix", "pine", "pixel", "pluto", "prairie", "pulse", "quartz",
    "quest", "raven", "reef", "river", "rocket", "sable", "saffron", "sage", "shadow", "signal",
    "silver", "sky", "solstice", "spark", "spice", "spruce", "star", "storm", "summit", "sunrise",
    "thunder", "tiger", "topaz", "trail", "tulip", "turbo", "velvet", "violet", "voyage", "willow",
]


def _build_selected_groups(include_uppercase, include_lowercase, include_numbers, include_symbols):
    groups = []
    if include_uppercase:
        groups.append(string.ascii_uppercase)
    if include_lowercase:
        groups.append(string.ascii_lowercase)
    if include_numbers:
        groups.append(string.digits)
    if include_symbols:
        groups.append(string.punctuation)
    return groups


def generate_password(
    length,
    include_uppercase=True,
    include_lowercase=True,
    include_numbers=True,
    include_symbols=True,
    exclude_ambiguous=False,
):
    groups = _build_selected_groups(
        include_uppercase,
        include_lowercase,
        include_numbers,
        include_symbols,
    )

    if not groups:
        return None

    filtered_groups = []
    for group in groups:
        if exclude_ambiguous:
            filtered = "".join(ch for ch in group if ch not in AMBIGUOUS_CHARACTERS)
            if filtered:
                filtered_groups.append(filtered)
        else:
            filtered_groups.append(group)

    if not filtered_groups:
        return None

    if length < len(filtered_groups):
        return None

    all_characters = "".join(filtered_groups)
    if not all_characters:
        return None

    password_chars = [secrets.choice(group) for group in filtered_groups]
    password_chars.extend(secrets.choice(all_characters) for _ in range(length - len(filtered_groups)))
    random.SystemRandom().shuffle(password_chars)
    return "".join(password_chars)


def estimate_password_strength(password, character_pool_size):
    if not password or character_pool_size <= 0:
        return {"label": "Very Weak", "score": 0, "entropy_bits": 0}

    raw_entropy_bits = len(password) * math.log2(character_pool_size)
    penalty_bits, findings = _estimate_weak_pattern_penalty(password)
    entropy_bits = max(0, raw_entropy_bits - penalty_bits)

    if entropy_bits < 35:
        label, score = "Weak", 1
    elif entropy_bits < 55:
        label, score = "Fair", 2
    elif entropy_bits < 75:
        label, score = "Strong", 3
    else:
        label, score = "Very Strong", 4

    return {
        "label": label,
        "score": score,
        "entropy_bits": round(entropy_bits, 1),
        "raw_entropy_bits": round(raw_entropy_bits, 1),
        "findings": findings,
    }


def selected_character_pool_size(
    include_uppercase,
    include_lowercase,
    include_numbers,
    include_symbols,
    exclude_ambiguous=False,
):
    groups = _build_selected_groups(
        include_uppercase,
        include_lowercase,
        include_numbers,
        include_symbols,
    )
    pool = "".join(groups)
    if exclude_ambiguous:
        pool = "".join(ch for ch in pool if ch not in AMBIGUOUS_CHARACTERS)
    return len(pool)


def generate_passphrase(
    word_count=4,
    separator="-",
    capitalize_words=False,
    append_number=False,
    append_symbol=False,
):
    if word_count < 3 or word_count > 8:
        return None

    words = [secrets.choice(PASSPHRASE_WORDS) for _ in range(word_count)]
    if capitalize_words:
        words = [word.capitalize() for word in words]

    passphrase = separator.join(words)
    if append_number:
        passphrase += str(secrets.randbelow(90) + 10)
    if append_symbol:
        passphrase += secrets.choice("!@#$%^&*")
    return passphrase


def estimate_passphrase_strength(passphrase, word_count, append_number=False, append_symbol=False):
    if not passphrase:
        return {"label": "Very Weak", "score": 0, "entropy_bits": 0}

    base_entropy = word_count * math.log2(len(PASSPHRASE_WORDS))
    if append_number:
        base_entropy += math.log2(90)
    if append_symbol:
        base_entropy += math.log2(8)

    if base_entropy < 40:
        label, score = "Weak", 1
    elif base_entropy < 60:
        label, score = "Fair", 2
    elif base_entropy < 80:
        label, score = "Strong", 3
    else:
        label, score = "Very Strong", 4

    return {"label": label, "score": score, "entropy_bits": round(base_entropy, 1)}


def get_preset_config(preset_key):
    return PASSWORD_PRESETS.get(preset_key, PASSWORD_PRESETS[DEFAULT_PRESET_KEY]).copy()


def _estimate_weak_pattern_penalty(password):
    lower = password.lower()
    penalty_bits = 0.0
    findings = []

    if any(term in lower for term in COMMON_WEAK_TERMS):
        penalty_bits += 12
        findings.append("Contains common weak words or patterns")

    if _has_linear_sequence(lower, min_length=4):
        penalty_bits += 8
        findings.append("Contains predictable sequences")

    longest_repeat_run = _longest_repeat_run(password)
    if longest_repeat_run >= 3:
        penalty_bits += (longest_repeat_run - 2) * 2
        findings.append("Contains repeated characters")

    unique_ratio = len(set(password)) / max(1, len(password))
    if unique_ratio < 0.45:
        penalty_bits += 6
        findings.append("Low character variety")

    if password.isalpha() or password.isdigit():
        penalty_bits += 6
        findings.append("Single character type pattern")

    return penalty_bits, findings


def _has_linear_sequence(password_lower, min_length=4):
    for sequence in SEQUENCE_STRINGS:
        for i in range(0, len(sequence) - min_length + 1):
            chunk = sequence[i:i + min_length]
            if chunk in password_lower or chunk[::-1] in password_lower:
                return True
    return False


def _longest_repeat_run(text):
    if not text:
        return 0

    max_run = 1
    current_run = 1
    for index in range(1, len(text)):
        if text[index] == text[index - 1]:
            current_run += 1
            max_run = max(max_run, current_run)
        else:
            current_run = 1
    return max_run