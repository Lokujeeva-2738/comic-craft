from pathlib import Path
import os

from dotenv import load_dotenv


# =========================================================
# Base Directories
# =========================================================

BASE_DIR = Path(__file__).resolve().parent.parent

APP_DIR = BASE_DIR / "app"
STATIC_DIR = BASE_DIR / "static"
TEMPLATES_DIR = BASE_DIR / "templates"

PANELS_DIR = STATIC_DIR / "panels"
EXPORTS_DIR = STATIC_DIR / "exports"
FONTS_DIR = STATIC_DIR / "fonts"


# =========================================================
# Environment
# =========================================================

ENV_FILE = BASE_DIR / ".env"

load_dotenv(ENV_FILE)

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY", "")

API_KEY = GEMINI_API_KEY or GOOGLE_API_KEY


# =========================================================
# Gemini Models
# =========================================================

GEMINI_TEXT_MODEL = "gemini-3.8-flash"
GEMINI_PRO_MODEL = "gemini-2.5-pro"
GEMINI_IMAGE_MODEL = "gemini-3.1-flash-image"


# =========================================================
# Application Settings
# =========================================================

APP_NAME = "ComicCraft"
APP_VERSION = "1.0.0"

DEBUG = os.getenv("DEBUG", "true").lower() == "true"

DEFAULT_PANEL_COUNT = 5
MAX_PANEL_COUNT = 10


# =========================================================
# Create Required Directories
# =========================================================

STATIC_DIR.mkdir(parents=True, exist_ok=True)
PANELS_DIR.mkdir(parents=True, exist_ok=True)
EXPORTS_DIR.mkdir(parents=True, exist_ok=True)
FONTS_DIR.mkdir(parents=True, exist_ok=True)
TEMPLATES_DIR.mkdir(parents=True, exist_ok=True)