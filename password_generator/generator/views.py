# generator/views.py
from django.shortcuts import render

from .breach_check import check_password_breach_count
from .password_utils import (
    DEFAULT_PRESET_KEY,
    PASSWORD_PRESETS,
    estimate_passphrase_strength,
    estimate_password_strength,
    generate_passphrase,
    generate_password,
    get_preset_config,
    selected_character_pool_size,
)

def _parse_bool(post_data, key, default=False):
    return key in post_data if key in post_data else default

def index(request):
    password = None
    variations = []
    breach_count = None
    breach_message = None
    error = None

    mode = "password"
    selected_preset = DEFAULT_PRESET_KEY

    length = 16
    include_uppercase = True
    include_lowercase = True
    include_numbers = True
    include_symbols = True
    exclude_ambiguous = False

    word_count = 5
    separator = "-"
    capitalize_words = False
    append_number = True
    append_symbol = True

    strength = None
    recommendation_message = None

    if request.method == "POST":
        selected_preset = request.POST.get("preset", DEFAULT_PRESET_KEY)
        if selected_preset not in PASSWORD_PRESETS:
            selected_preset = DEFAULT_PRESET_KEY
        action = request.POST.get("action", "generate")

        if action == "apply_preset":
            preset_config = get_preset_config(selected_preset)
            mode = preset_config.get("mode", "password")
            length = preset_config.get("length", 16)
            include_uppercase = preset_config.get("include_uppercase", True)
            include_lowercase = preset_config.get("include_lowercase", True)
            include_numbers = preset_config.get("include_numbers", True)
            include_symbols = preset_config.get("include_symbols", True)
            exclude_ambiguous = preset_config.get("exclude_ambiguous", False)
            word_count = preset_config.get("word_count", 5)
            separator = preset_config.get("separator", "-")
            capitalize_words = preset_config.get("capitalize_words", False)
            append_number = preset_config.get("append_number", True)
            append_symbol = preset_config.get("append_symbol", True)
        else:
            mode = request.POST.get("mode", "password")
            length = int(request.POST.get("length", 16))
            include_uppercase = _parse_bool(request.POST, "uppercase", True)
            include_lowercase = _parse_bool(request.POST, "lowercase", True)
            include_numbers = _parse_bool(request.POST, "numbers", True)
            include_symbols = _parse_bool(request.POST, "symbols", True)
            exclude_ambiguous = _parse_bool(request.POST, "exclude_ambiguous", False)

            word_count = int(request.POST.get("word_count", 5))
            separator = request.POST.get("separator", "-")[:2]
            capitalize_words = _parse_bool(request.POST, "capitalize_words", False)
            append_number = _parse_bool(request.POST, "append_number", True)
            append_symbol = _parse_bool(request.POST, "append_symbol", True)

            if mode == "password":
                if length < 8 or length > 64:
                    error = "Choose a password length between 8 and 64."
                elif not any([include_uppercase, include_lowercase, include_numbers, include_symbols]):
                    error = "Select at least one character set."
                else:
                    password = generate_password(
                        length=length,
                        include_uppercase=include_uppercase,
                        include_lowercase=include_lowercase,
                        include_numbers=include_numbers,
                        include_symbols=include_symbols,
                        exclude_ambiguous=exclude_ambiguous,
                    )
                    pool_size = selected_character_pool_size(
                        include_uppercase=include_uppercase,
                        include_lowercase=include_lowercase,
                        include_numbers=include_numbers,
                        include_symbols=include_symbols,
                        exclude_ambiguous=exclude_ambiguous,
                    )
                    strength = estimate_password_strength(password, pool_size)
            else:
                if word_count < 3 or word_count > 8:
                    error = "Choose a passphrase word count between 3 and 8."
                else:
                    password = generate_passphrase(
                        word_count=word_count,
                        separator=separator,
                        capitalize_words=capitalize_words,
                        append_number=append_number,
                        append_symbol=append_symbol,
                    )
                    strength = estimate_passphrase_strength(
                        password,
                        word_count=word_count,
                        append_number=append_number,
                        append_symbol=append_symbol,
                    )

            if not password and not error:
                error = "Unable to generate value with the selected options."

            if password and action == "variations":
                if mode == "password":
                    variations = [
                        generate_password(
                            length=length,
                            include_uppercase=include_uppercase,
                            include_lowercase=include_lowercase,
                            include_numbers=include_numbers,
                            include_symbols=include_symbols,
                            exclude_ambiguous=exclude_ambiguous,
                        )
                        for _ in range(3)
                    ]
                else:
                    variations = [
                        generate_passphrase(
                            word_count=word_count,
                            separator=separator,
                            capitalize_words=capitalize_words,
                            append_number=append_number,
                            append_symbol=append_symbol,
                        )
                        for _ in range(3)
                    ]

            if password and _parse_bool(request.POST, "check_breach", False):
                breach_count = check_password_breach_count(password)
                if breach_count is None:
                    breach_message = "Breach service is currently unavailable."
                elif breach_count == 0:
                    breach_message = "No breach record found for this password hash."
                else:
                    breach_message = f"Warning: found {breach_count} breach matches for this password."

            if password and strength and strength.get("score", 0) <= 2:
                recommendation_message = "Tip: This password is still on the weaker side. Try Generate 3 Variations or increase length for better safety."

            if password and breach_count and breach_count > 0:
                recommendation_message = "This value appears in breach data. Please regenerate immediately and avoid reusing it anywhere."

    return render(
        request,
        "generator/index.html",
        {
            "presets": PASSWORD_PRESETS,
            "selected_preset": selected_preset,
            "mode": mode,
            "password": password,
            "variations": [item for item in variations if item],
            "breach_count": breach_count,
            "breach_message": breach_message,
            "error": error,
            "length": length,
            "include_uppercase": include_uppercase,
            "include_lowercase": include_lowercase,
            "include_numbers": include_numbers,
            "include_symbols": include_symbols,
            "exclude_ambiguous": exclude_ambiguous,
            "word_count": word_count,
            "separator": separator,
            "capitalize_words": capitalize_words,
            "append_number": append_number,
            "append_symbol": append_symbol,
            "strength": strength,
            "recommendation_message": recommendation_message,
        },
    )
