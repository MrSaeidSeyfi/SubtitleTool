import argparse
import logging
import sqlite3
from dataclasses import dataclass
from typing import List
from moviepy import VideoFileClip, TextClip, CompositeVideoClip
from spellchecker import SpellChecker
import whisper

# Logging setup
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

@dataclass
class Subtitle:
    start_time: float
    end_time: float
    text: str

class AudioExtractor:
    def extract_audio(self, mp4_path: str) -> str:
        try:
            video = VideoFileClip(mp4_path)
            audio_path = mp4_path.replace('.mp4', '.wav')
            video.audio.write_audiofile(audio_path)
            return audio_path
        except Exception as e:
            logging.error(f"Error extracting audio from {mp4_path}: {e}")
            raise

class Transcriber:
    def __init__(self):
        try:
            self.model = whisper.load_model("base")
        except Exception as e:
            logging.error(f"Error loading whisper model: {e}")
            raise

    def transcribe(self, audio_path: str) -> List[Subtitle]:
        try:
            result = self.model.transcribe(audio_path, language="en")
            return [
                Subtitle(s['start'], s['end'], s['text'])
                for s in result['segments']
            ]
        except Exception as e:
            logging.error(f"Error transcribing audio {audio_path}: {e}")
            raise

class SubtitleChecker:
    def __init__(self):
        self.spell_checker = SpellChecker()

    def check(self, subtitles: List[Subtitle]) -> List[Subtitle]:
        for sub in subtitles:
            misspelled = self.spell_checker.unknown(sub.text.split())
            if misspelled:
                logging.warning(f"Spelling errors at {sub.start_time}: {misspelled}")
                corrected_text = sub.text
                for word in misspelled:
                    correction = self.spell_checker.correction(word)
                    if correction:
                        corrected_text = corrected_text.replace(word, correction)
                sub.text = corrected_text

            words = sub.text.split()
            for i in range(len(words) - 1):
                if words[i].lower() == words[i + 1].lower():
                    logging.warning(f"Possible grammar issue at {sub.start_time}: Repeated word '{words[i]}'")
            if not sub.text.strip().endswith(('.', '!', '?')):
                logging.warning(f"Possible grammar issue at {sub.start_time}: Missing punctuation")
                sub.text = sub.text.strip() + '.'
        return subtitles

class DatabaseManager:
    def __init__(self, db_path: str):
        self.conn = sqlite3.connect(db_path)
        self.conn.execute('''
            CREATE TABLE IF NOT EXISTS subtitles (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                start_time REAL,
                end_time REAL,
                text TEXT
            )
        ''')

    def insert_subtitles(self, subtitles: List[Subtitle]):
        with self.conn:
            self.conn.executemany('INSERT INTO subtitles (start_time, end_time, text) VALUES (?, ?, ?)',
                                 [(s.start_time, s.end_time, s.text) for s in subtitles])



class SubtitleRenderer:
    def render(self, video_path: str, subtitles: List[Subtitle]) -> str:
        try:
            video = VideoFileClip(video_path)
            text_clips = []
            for s in subtitles:
                # Create text clip with calculated duration
                txt_clip = TextClip(
                    text=s.text,
                    font=r"E:\Project\test\ocr_persian\fonts\Vazir-Regular.ttf",
                    method='caption',
                    size=(int(video.w * 0.8), int(video.h * 0.2)),
                    color='white',
                    stroke_color='black',
                    stroke_width=2,
                    # Set duration for the text clip
                    duration=s.end_time - s.start_time
                ).with_start(s.start_time).with_position(('center', 'bottom'))
                text_clips.append(txt_clip)

            final_video = CompositeVideoClip([video] + text_clips)
            output_path = video_path.replace('.mp4', '_subtitled.mp4')
            final_video.write_videofile(output_path)
            return output_path
        except Exception as e:
            logging.error(f"Error rendering subtitles for {video_path}: {e}")
            raise


class Main:
    def __init__(self):
        self.audio_extractor = AudioExtractor()
        self.transcriber = Transcriber()
        self.subtitle_checker = SubtitleChecker()
        self.db_manager = DatabaseManager('subtitles.db')
        self.subtitle_renderer = SubtitleRenderer()

    def run(self, mp4_path: str):
        try:
            audio_path = self.audio_extractor.extract_audio(mp4_path)
            subtitles = self.transcriber.transcribe(audio_path)
            checked_subtitles = self.subtitle_checker.check(subtitles)
            self.db_manager.insert_subtitles(checked_subtitles)
            output_path = self.subtitle_renderer.render(mp4_path, checked_subtitles)
            logging.info(f"Output saved to {output_path}")
        except Exception as e:
            logging.error(f"Error: {e}")
            raise

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Generate subtitles for MP4 files")
    parser.add_argument("--input", type=str, help="Path to MP4 file")
    args = parser.parse_args()

    Main().run(args.input)