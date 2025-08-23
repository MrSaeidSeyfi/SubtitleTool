import argparse
import logging
import sys
from pathlib import Path
from typing import Optional

project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from config.settings import setup_logging, INPUT_DIR
from src.core.audio import AudioExtractor
from src.core.transcription import Transcriber
from src.core.validation import SubtitleValidator
from src.core.rendering import SubtitleRenderer
from src.services.storage import StorageManager
from src.services.translation import TranslationService

logger = logging.getLogger(__name__)

class SubtitleToolCLI:
	"""Command line interface for SubtitleTool"""
	
	def __init__(self):
		"""Initialize CLI components"""
		self.audio_extractor = AudioExtractor()
		self.transcriber = Transcriber()
		self.validator = SubtitleValidator()
		self.storage_manager = StorageManager()
		self.translation_service = TranslationService()
		self.renderer = None  # Will be initialized per process_video
	
	def process_video(self, video_path: str,
				 	skip_validation: bool = False,
				 	translate: bool = False,
				 	src_lang: str = "eng_Latn",
				 	tgt_lang: str = "pes_Arab") -> None:
		"""
		Process video file to generate subtitles
		
		Args:
			video_path: Path to input video file
			skip_validation: Skip subtitle validation
			translate: Enable translation
			src_lang: Source language code for translation
			tgt_lang: Target language code for translation
		"""
		try:
			logger.info(f"Starting processing: {video_path}")
			
			if not self.storage_manager.validate_video_file(video_path):
				logger.error("Invalid video file")
				return
			
			logger.info("Extracting audio...")
			audio_path = self.audio_extractor.extract_audio(video_path)
			
			try:
				logger.info("Transcribing audio...")
				subtitles = self.transcriber.transcribe(audio_path)
				
				if not skip_validation:
					logger.info("Validating subtitles...")
					subtitles = self.validator.validate_and_correct(subtitles)
					subtitles = self.validator.validate_subtitle_timing(subtitles)
				
				if translate:
					logger.info(f"Translating subtitles from {src_lang} to {tgt_lang}...")
					subtitles = self.translation_service.translate_subtitles(subtitles, src_lang, tgt_lang)
					logger.info("Translation completed - rendering translated subtitles on video")
				else:
					logger.info("No translation requested - rendering original subtitles on video")
				
				logger.info("Rendering video with subtitles...")
				# Initialize renderer with target language
				self.renderer = SubtitleRenderer(target_language=tgt_lang)

				logger.info("Generating SRT subtitle file...")
				subtitle_path = self.renderer.render_subtitle_file(
					video_path, subtitles, 'srt'
				)
				logger.info(f"Subtitle file created: {subtitle_path}")
				

				output_path = self.renderer.render(video_path, subtitles)
				logger.info(f"Video rendered successfully: {output_path}")
				
				logger.info("Processing completed successfully!")
				
			finally:
				self.audio_extractor.cleanup_audio(audio_path)
				
		except Exception as e:
			logger.error(f"Error processing video: {e}")
			raise
	
	def list_videos(self, directory: Optional[str] = None) -> None:
		"""List available video files"""
		try:
			search_dir = Path(directory) if directory else INPUT_DIR
			video_files = self.storage_manager.get_video_files(search_dir)
			
			if not video_files:
				print(f"No video files found in {search_dir}")
				return
			
			print(f"\nVideo files in {search_dir}:")
			print("-" * 60)
			for video_file in video_files:
				info = self.storage_manager.get_file_info(str(video_file))
				print(f"{video_file.name:<30} {info['size_mb']:>8.1f} MB")
			
		except Exception as e:
			logger.error(f"Error listing videos: {e}")
	
	def list_languages(self) -> None:
		"""List supported languages for translation"""
		try:
			languages = self.translation_service.get_supported_languages()
			
			print("\nSupported languages for translation:")
			print("-" * 60)
			for i, lang in enumerate(languages, 1):
				print(f"{i:3d}. {lang}")
			
			print(f"\nTotal: {len(languages)} languages supported")
			
		except Exception as e:
			logger.error(f"Error listing languages: {e}")
	
	def test_translation(self) -> None:
		"""Test translation API connection"""
		try:
			print("Testing translation API connection...")
			if self.translation_service.test_connection():
				print("✓ Translation API connection successful")
			else:
				print("✗ Translation API connection failed")
		except Exception as e:
			logger.error(f"Error testing translation: {e}")
	
	def cleanup(self) -> None:
		"""Clean up temporary files"""
		try:
			count = self.storage_manager.cleanup_temp_files()
			print(f"Cleaned up {count} temporary files")
		except Exception as e:
			logger.error(f"Error during cleanup: {e}")

def main():
	"""Main CLI entry point"""
	parser = argparse.ArgumentParser(
		description="SubtitleTool - Generate videos with embedded subtitles, with optional translation",
		formatter_class=argparse.RawDescriptionHelpFormatter,
		epilog="""
Examples:
  %(prog)s --input video.mp4
  %(prog)s --input video.mp4 --translate --src-lang eng_Latn --tgt-lang pes_Arab
  %(prog)s --list-languages
  %(prog)s --test-translation
  %(prog)s --list
		"""
	)
	
	parser.add_argument("--input", "-i", type=str, help="Input video file path")
	
	parser.add_argument("--skip-validation", action="store_true", 
					   help="Skip subtitle validation and correction")
	
	parser.add_argument("--translate", action="store_true",
					   help="Enable subtitle translation")
	parser.add_argument("--src-lang", type=str, default="eng_Latn",
					   help="Source language code for translation (default: eng_Latn)")
	parser.add_argument("--tgt-lang", type=str, default="pes_Arab",
					   help="Target language code for translation (default: pes_Arab)")
	
	parser.add_argument("--list", "-l", action="store_true", 
					   help="List available video files")
	parser.add_argument("--list-languages", action="store_true",
					   help="List supported languages for translation")
	parser.add_argument("--test-translation", action="store_true",
					   help="Test translation API connection")
	parser.add_argument("--cleanup", action="store_true", 
					   help="Clean up temporary files")
	
	parser.add_argument("--verbose", "-v", action="store_true", 
					   help="Enable verbose logging")
	parser.add_argument("--quiet", "-q", action="store_true", 
					   help="Suppress logging output")
	
	args = parser.parse_args()
	
	if args.quiet:
		setup_logging("ERROR")
	elif args.verbose:
		setup_logging("DEBUG")
	else:
		setup_logging("INFO")
	
	cli = SubtitleToolCLI()
	
	try:
		if args.list:
			cli.list_videos()
		elif args.list_languages:
			cli.list_languages()
		elif args.test_translation:
			cli.test_translation()
		elif args.cleanup:
			cli.cleanup()
		elif args.input:
			cli.process_video(
				video_path=args.input,
				skip_validation=args.skip_validation,
				translate=args.translate,
				src_lang=args.src_lang,
				tgt_lang=args.tgt_lang
			)
		else:
			parser.print_help()
			
	except KeyboardInterrupt:
		logger.info("Processing interrupted by user")
		sys.exit(1)
	except Exception as e:
		logger.error(f"Error: {e}")
		sys.exit(1)

if __name__ == "__main__":
	main() 
