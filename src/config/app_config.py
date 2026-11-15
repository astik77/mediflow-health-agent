import base64
from pathlib import Path
from PIL import Image

APP_NAME = "MediFlow"
APP_DESCRIPTION = "Agentic Longitudinal Health Management with Evidence-Grounded Clinical Workflow Coordination"
APP_ICON = "🩺"
APP_TAGLINE = "Evidence-Grounded Longitudinal Health Intelligence"

# App settings
MAX_UPLOAD_SIZE_MB = 20
MAX_PDF_PAGES = 50
SESSION_TIMEOUT_MINUTES = 30
ANALYSIS_DAILY_LIMIT = 15

# UI Design System: Dark Slate & Sky Blue / Teal Palette
PRIMARY_COLOR = "#38BDF8"      # Sky 400 (Vibrant on Dark)
SECONDARY_COLOR = "#2DD4BF"    # Teal 400 (Clinical Glow)
BG_CANVAS = "#0B0F19"          # Midnight Slate (Deep Background)
BG_SURFACE = "#1E293B"         # Slate 800 (Card & Modal Surface)
BG_SURFACE_ALT = "#0F172A"     # Slate 900 (Inset / Contrast Surface)
SLATE_BORDER = "#334155"       # Slate 700 (Hairline Divider & Border)
TEXT_PRIMARY = "#F8FAFC"       # Crisp White
TEXT_MUTED = "#94A3B8"         # Slate 400

# Asset Paths and Cached Base64 Helpers
PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
ASSETS_DIR = PROJECT_ROOT / "assets"
LOGO_PATH = ASSETS_DIR / "mediflow_logo.png"
ICON_PATH = ASSETS_DIR / "mediflow_icon.png"
FAVICON_PATH = ASSETS_DIR / "favicon.png"

_LOGO_B64 = None
_ICON_B64 = None


def get_logo_base64() -> str:
    """Return cached Base64 data URI of the official MediFlow logo."""
    global _LOGO_B64
    if _LOGO_B64 is None:
        try:
            with open(LOGO_PATH, "rb") as f:
                _LOGO_B64 = f"data:image/png;base64,{base64.b64encode(f.read()).decode('utf-8')}"
        except Exception:
            _LOGO_B64 = ""
    return _LOGO_B64


def get_icon_base64() -> str:
    """Return cached Base64 data URI of the official MediFlow icon mark."""
    global _ICON_B64
    if _ICON_B64 is None:
        try:
            with open(ICON_PATH, "rb") as f:
                _ICON_B64 = f"data:image/png;base64,{base64.b64encode(f.read()).decode('utf-8')}"
        except Exception:
            _ICON_B64 = ""
    return _ICON_B64


def get_favicon():
    """Return PIL Image for Streamlit page_icon favicon."""
    try:
        return Image.open(FAVICON_PATH)
    except Exception:
        return "🩺"

