# SubtitleTool

A Python tool to generate videos with embedded subtitles, with optional translation support.

## Features

- **Video Processing**: Extract audio from video files
- **Speech Recognition**: Transcribe audio using OpenAI Whisper
- **Subtitle Generation**: Create videos with embedded subtitles
- **Translation**: Translate subtitles and render them on video (optional)
- **Video Rendering**: Burn subtitles into video with custom styling
- **Validation**: Check and correct subtitle timing and text

## Quick Start

```bash
# Install dependencies
pip install -r requirements.txt

# Process a video file (renders video with original subtitles)
python src/cli.py --input video.mp4

# Process with translation (renders video with translated subtitles)
python src/cli.py --input video.mp4 --translate --src-lang eng_Latn --tgt-lang pes_Arab

# List supported languages
python src/cli.py --list-languages

# Test translation API
python src/cli.py --test-translation
```

## Usage Examples

```bash
# List available videos
python src/cli.py --list

# Generate video with original English subtitles
python src/cli.py --input video.mp4

# Generate video with Persian subtitles (translated from English)
python src/cli.py --input video.mp4 --translate --src-lang eng_Latn --tgt-lang pes_Arab

# Generate video with Spanish subtitles
python src/cli.py --input video.mp4 --translate --src-lang eng_Latn --tgt-lang spa_Latn

# Skip validation and translate to French
python src/cli.py --input video.mp4 --skip-validation --translate --src-lang eng_Latn --tgt-lang fra_Latn

# Clean up temp files
python src/cli.py --cleanup
```

## Output

The tool generates:
1. **Video file** with embedded subtitles (original or translated)
2. **SRT file** with the same subtitles for reference

When translation is enabled, both the video and SRT file contain the translated text.
When translation is disabled, both contain the original transcribed text.

## Translation Support

The tool supports translation to/from 200+ languages using the Hugging Face translation API. Common language codes include:

- `eng_Latn` - English (Latin script)
- `pes_Arab` - Persian/Farsi (Arabic script)
- `spa_Latn` - Spanish (Latin script)
- `fra_Latn` - French (Latin script)
- `deu_Latn` - German (Latin script)
- `rus_Cyrl` - Russian (Cyrillic script)
- `zho_Hans` - Chinese Simplified (Han script)
- `jpn_Jpan` - Japanese (Japanese script)
- `kor_Hang` - Korean (Hangul script)

Use `--list-languages` to see all supported language codes.

## Project Structure

```
SubtitleTool/
├── src/
│   ├── cli.py              # Command line interface
│   ├── core/               # Core processing modules
│   ├── models/             # Data models
│   └── services/           # Storage and translation services
├── config/                 # Configuration files
├── data/                   # Input/output directories
└── requirements.txt        # Dependencies
```

## Supported Formats

- **Video**: MP4, AVI, MOV, MKV
- **Audio**: WAV, MP3, AAC, FLAC, M4A
- **Subtitles**: SRT

