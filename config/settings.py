import os
import logging
from pathlib import Path
from .constants import *

# Project paths
PROJECT_ROOT = Path(__file__).parent.parent
DATA_DIR = PROJECT_ROOT / "data"
INPUT_DIR = DATA_DIR / "input"
OUTPUT_DIR = DATA_DIR / "output"
TEMP_DIR = DATA_DIR / "temp"

# Ensure directories exist
INPUT_DIR.mkdir(parents=True, exist_ok=True)
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
TEMP_DIR.mkdir(parents=True, exist_ok=True)

# Font path
FONT_PATH = Path(DEFAULT_FONT_PATH)

# Logging configuration
def setup_logging(level=DEFAULT_LOG_LEVEL):
    """Setup logging configuration"""
    logging.basicConfig(
        level=getattr(logging, level.upper()),
        format=DEFAULT_LOG_FORMAT,
        handlers=[
            logging.StreamHandler(),
            logging.FileHandler(PROJECT_ROOT / "subtitle_tool.log")
        ]
    )

# Environment variables
def get_env_setting(key, default=None):
    """Get setting from environment variable"""
    return os.getenv(key, default)

# Model settings
WHISPER_MODEL = get_env_setting("WHISPER_MODEL", DEFAULT_WHISPER_MODEL)
LANGUAGE = get_env_setting("LANGUAGE", DEFAULT_LANGUAGE)

# Video settings
FONT_SIZE = int(get_env_setting("FONT_SIZE", DEFAULT_FONT_SIZE))
TEXT_COLOR = get_env_setting("TEXT_COLOR", DEFAULT_TEXT_COLOR)
STROKE_COLOR = get_env_setting("STROKE_COLOR", DEFAULT_STROKE_COLOR)
STROKE_WIDTH = int(get_env_setting("STROKE_WIDTH", DEFAULT_STROKE_WIDTH)) 