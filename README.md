# Ecommerce API (Django)

This repository contains a Django project scaffold for an ecommerce API.

## Project layout

- `ecommerceApiproject/` — Django project root (settings, urls, wsgi/asgi)
- `ecommerceEnv/` — Local virtual environment (ignored by Git)

## Quick start

1. Create and activate a virtual environment (optional if using the existing one):
   - Windows PowerShell
     - `python -m venv .venv`
     - `.venv\\Scripts\\Activate.ps1`
2. Install dependencies:
   - `pip install -r requirements.txt`
3. Run migrations and start the dev server:
   - `python manage.py migrate`
   - `python manage.py runserver`

## Notes
- Keep secrets and local settings in a `.env` file (not checked into source control).
- The `ecommerceEnv/` folder is local-only and excluded via `.gitignore`.
