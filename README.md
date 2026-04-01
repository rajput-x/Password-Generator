# Password-Generator

A modern Django-based password generator with a security-focused UI, passphrase mode, breach-awareness, and smart strength analysis.

## Overview

This project helps users generate strong credentials quickly with practical real-world presets, animated premium UI, and safety guidance.

It supports:
- Standard password generation
- Passphrase generation
- Preset-based policy selection
- Optional breach check (HIBP range API / k-anonymity)
- Strength analysis with weak-pattern detection

## Key Features

- **Secure random generation** using Python `secrets`
- **Password + passphrase modes**
- **Real-world presets**:
	- Basic Web (balanced)
	- High Security (recommended)
	- Legacy Compatible (no symbols)
	- Passphrase Strong
- **One-click 3 variations**
- **Strength meter with findings** (entropy + pattern penalties)
- **Breach check support** with user guidance
- **Custom animated UI**:
	- Dark/light theme toggle
	- Glassmorphism card styling
	- Particle Shield background
	- Custom dropdown and polished controls

## Tech Stack

- Python
- Django
- HTML/CSS/JavaScript (Django templates + static files)
- SQLite (default)

## Project Structure

```text
Password Generator/
├── README.md
├── password_generator/
│   ├── manage.py
│   ├── requirements.txt
│   ├── .env.example
│   ├── generator/
│   │   ├── views.py
│   │   ├── password_utils.py
│   │   ├── breach_check.py
│   │   ├── tests.py
│   │   ├── templates/generator/index.html
│   │   └── static/generator/
│   │       ├── styles.css
│   │       └── app.js
│   └── password_generator/
│       └── settings.py
└── ...
```

## How to Run Locally

### 1) Prerequisites

- Python 3.10+ (project works with newer versions too)
- `pip`

### 2) Install dependencies

From repository root:

```powershell
cd "password_generator"
pip install -r requirements.txt
```

### 3) Start development server

```powershell
python manage.py runserver
```

Open:
- `http://127.0.0.1:8000/`

## Running Tests

```powershell
cd "password_generator"
python manage.py test
```

## Environment Configuration

Use `.env.example` as reference for optional environment-based settings.

Supported variables:
- `DJANGO_SECRET_KEY`
- `DJANGO_DEBUG`
- `DJANGO_ALLOWED_HOSTS`
- `DJANGO_CSRF_TRUSTED_ORIGINS`
- `DJANGO_SECURE_SSL_REDIRECT`
- `DJANGO_SESSION_COOKIE_SECURE`
- `DJANGO_CSRF_COOKIE_SECURE`

## Security Notes

- Password generation uses cryptographically secure randomness.
- Breach check uses HIBP range API with **k-anonymity** (full password is never sent).
- Strength scoring includes weak-pattern checks (common words, sequences, repetition, low variety).

## Troubleshooting

- If server doesn’t start, verify Django is installed:
	- `pip install -r requirements.txt`
- If static styles are stale, hard refresh browser (`Ctrl + F5`).
- If a Python process is stuck, stop old process and rerun server/tests.

## License

This project is open for learning and portfolio/demo usage.
