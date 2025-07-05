# Project constants
PROJECT_NAME = "SubtitleTool"
VERSION = "1.0.0"

# File extensions
SUPPORTED_VIDEO_FORMATS = ['.mp4', '.avi', '.mov', '.mkv']
SUPPORTED_AUDIO_FORMATS = ['.wav', '.mp3', '.aac', '.flac', '.m4a']
SUBTITLE_FORMATS = ['.srt', '.vtt', '.ass', '.ssa']

# Whisper model settings
DEFAULT_WHISPER_MODEL = "base"
DEFAULT_LANGUAGE = "en"

# Video rendering settings
DEFAULT_FONT_PATH = r"E:\Project\SubtitleTool\data\fonts\Vazir-Regular.ttf"
DEFAULT_FONT_SIZE_RATIO = 0.3
DEFAULT_SUBTITLE_HEIGHT_RATIO = 0.5
DEFAULT_TEXT_COLOR = 'white'
DEFAULT_STROKE_COLOR = 'black'
DEFAULT_STROKE_WIDTH = 2

# Database settings
DEFAULT_DB_NAME = "subtitles.db"

# Logging
DEFAULT_LOG_LEVEL = "INFO"
DEFAULT_LOG_FORMAT = "%(asctime)s - %(levelname)s - %(message)s" 