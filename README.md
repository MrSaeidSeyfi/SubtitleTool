# SubtitleTool

This project is a tool that automatically adds subtitles to your videos. It can transcribe speech from any video file and optionally translate the subtitles into different languages.

## What it does

- **Extracts audio** from your video files
- **Transcribes speech** using AI to create subtitles
- **Translates subtitles** into 200+ languages (optional)
- **Burns subtitles** directly onto your video
- **Generates SRT files** for use in other video editors
  
<img width="800" height="178" alt="Screenshot 2025-08-23 163443" src="https://github.com/user-attachments/assets/6a027661-14d2-43c1-ad84-c42a1f271f57" />

## Quick Start

1. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

2. **Basic usage - add English subtitles:**
   ```bash
   python src/cli.py --input video_path.mp4
   ```

3. **Add translated subtitles:**
   ```bash
   python src/cli.py --input video_path.mp4 --translate --src-lang eng_Latn --tgt-lang pes_Arab
   ```

4. **Use custom font:**
   ```bash
   python src/cli.py --input your_video.mp4 --font-family "Arial"
   ```

## Examples

```bash
# List available videos
python src/cli.py --list

# Use custom font and translate to Spanish
python src/cli.py --input video.mp4 --translate --src-lang eng_Latn --tgt-lang spa_Latn --font-family "Times New Roman"

# See all supported languages
python src/cli.py --list-languages
```

## Supported Formats

- **Video:** MP4, AVI, MOV, MKV
- **Audio:** WAV, MP3, AAC, FLAC, M4A
- **Output:** Video with embedded subtitles + SRT file

## How it works

1. Upload your video file to the `data/input/` folder
2. Run the tool with your desired options
3. Get a new video with subtitles burned in
4. Find your processed video in `data/results/`
   
## Project Results
<div align="center">

[<img alt="Result 1" src="docs/thumbs/result1.jpg" width="300">](https://github.com/user-attachments/assets/40ac13de-5012-4289-9827-c7a66725066f)
[<img alt="Result 2" src="docs/thumbs/result2.jpg" width="300">](https://github.com/user-attachments/assets/0a049a6f-2b73-4568-be3b-ab51d1263e6e)
[<img alt="Result 3" src="docs/thumbs/result3.jpg" width="300">](https://github.com/user-attachments/assets/1bce8428-6bb0-468b-8dfc-ead2d4ff9f0b)
[<img alt="Result 4" src="docs/thumbs/result4.jpg" width="300">](https://github.com/user-attachments/assets/4a440694-8b1d-47c4-98f3-ad52e88b364a)

</div>

## Notes
- The tool automatically handles different languages and scripts
- Translation is optional - you can just get transcribed subtitles
- Large videos are processed efficiently using batch translation
- Custom fonts can be specified for different subtitle styles

That's it! Just drop a video in the input folder and run the tool.
