
import argparse
import logging
import sys
from pathlib import Path
from typing import Optional

project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from config.settings import setup_logging, INPUT_DIR, OUTPUT_DIR
from src.core.audio import AudioExtractor
from src.core.transcription import Transcriber
from src.core.validation import SubtitleValidator
from src.core.rendering import SubtitleRenderer
from src.services.database import DatabaseManager
from src.services.storage import StorageManager

logger = logging.getLogger(__name__)

class SubtitleToolCLI:
    """Command line interface for SubtitleTool"""
    
    def __init__(self):
        """Initialize CLI components"""
        self.audio_extractor = AudioExtractor()
        self.transcriber = Transcriber()
        self.validator = SubtitleValidator()
        self.renderer = SubtitleRenderer()
        self.db_manager = DatabaseManager()
        self.storage_manager = StorageManager()
    
    def process_video(self, video_path: str, 
                     output_format: str = 'video',
                     subtitle_format: Optional[str] = None,
                     skip_validation: bool = False,
                     skip_rendering: bool = False) -> None:
        """
        Process video file to generate subtitles
        
        Args:
            video_path: Path to input video file
            output_format: Output format ('video', 'subtitle', 'both')
            subtitle_format: Subtitle file format ('srt', 'vtt', 'ass')
            skip_validation: Skip subtitle validation
            skip_rendering: Skip video rendering
        """
        try:
            logger.info(f"Starting processing: {video_path}")
            
            # Validate input file
            if not self.storage_manager.validate_video_file(video_path):
                logger.error("Invalid video file")
                return
            
            # Extract audio
            logger.info("Extracting audio...")
            audio_path = self.audio_extractor.extract_audio(video_path)
            
            try:
                # Transcribe audio
                logger.info("Transcribing audio...")
                subtitles = self.transcriber.transcribe(audio_path)
                
                # Validate and correct subtitles
                if not skip_validation:
                    logger.info("Validating subtitles...")
                    subtitles = self.validator.validate_and_correct(subtitles)
                    subtitles = self.validator.validate_subtitle_timing(subtitles)
                
                # Store in database
                logger.info("Storing subtitles in database...")
                self.db_manager.insert_subtitles(video_path, subtitles)
                
                # Generate output
                if output_format in ['video', 'both'] and not skip_rendering:
                    logger.info("Rendering video with subtitles...")
                    output_path = self.renderer.render(video_path, subtitles)
                    logger.info(f"Video rendered: {output_path}")
                
                if output_format in ['subtitle', 'both'] and subtitle_format:
                    logger.info(f"Generating subtitle file ({subtitle_format})...")
                    subtitle_path = self.renderer.render_subtitle_file(
                        video_path, subtitles, subtitle_format
                    )
                    logger.info(f"Subtitle file created: {subtitle_path}")
                
                logger.info("Processing completed successfully!")
                
            finally:
                # Clean up audio file
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
    
    def search_subtitles(self, query: str, video_path: Optional[str] = None) -> None:
        """Search subtitles by text content"""
        try:
            subtitles = self.db_manager.search_subtitles(query, video_path)
            
            if not subtitles:
                print(f"No subtitles found matching '{query}'")
                return
            
            print(f"\nSubtitles matching '{query}':")
            print("-" * 80)
            for subtitle in subtitles:
                print(f"{subtitle.start_time:>8.2f}s - {subtitle.end_time:>8.2f}s: {subtitle.text}")
            
        except Exception as e:
            logger.error(f"Error searching subtitles: {e}")
    
    def show_stats(self) -> None:
        """Show processing statistics"""
        try:
            processed_videos = self.db_manager.get_processed_videos()
            
            print("\nProcessing Statistics:")
            print("-" * 40)
            print(f"Total videos processed: {len(processed_videos)}")
            
            if processed_videos:
                print("\nRecently processed videos:")
                for video_path in processed_videos[:5]:
                    count = self.db_manager.get_subtitle_count(video_path)
                    print(f"  {Path(video_path).name}: {count} subtitles")
            
            # Directory stats
            input_count, input_size = self.storage_manager.get_directory_size(INPUT_DIR)
            output_count, output_size = self.storage_manager.get_directory_size(OUTPUT_DIR)
            
            print(f"\nStorage:")
            print(f"  Input directory: {input_count} files, {input_size} MB")
            print(f"  Output directory: {output_count} files, {output_size} MB")
            
        except Exception as e:
            logger.error(f"Error showing stats: {e}")
    
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
        description="SubtitleTool - Generate subtitles for video files",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s --input video.mp4
  %(prog)s --input video.mp4 --output subtitle --format srt
  %(prog)s --input video.mp4 --output both --format srt
  %(prog)s --list
  %(prog)s --search "hello world"
  %(prog)s --stats
        """
    )
    
    # Input/output options
    parser.add_argument("--input", "-i", type=str, help="Input video file path")
    parser.add_argument("--output", "-o", choices=['video', 'subtitle', 'both'], 
                       default='video', help="Output format (default: video)")
    parser.add_argument("--format", "-f", choices=['srt', 'vtt', 'ass'], 
                       default='srt', help="Subtitle file format (default: srt)")
    
    # Processing options
    parser.add_argument("--skip-validation", action="store_true", 
                       help="Skip subtitle validation and correction")
    parser.add_argument("--skip-rendering", action="store_true", 
                       help="Skip video rendering (only generate subtitle file)")
    
    # Utility commands
    parser.add_argument("--list", "-l", action="store_true", 
                       help="List available video files")
    parser.add_argument("--search", "-s", type=str, 
                       help="Search subtitles by text content")
    parser.add_argument("--video", type=str, 
                       help="Limit search to specific video file")
    parser.add_argument("--stats", action="store_true", 
                       help="Show processing statistics")
    parser.add_argument("--cleanup", action="store_true", 
                       help="Clean up temporary files")
    
    # Logging options
    parser.add_argument("--verbose", "-v", action="store_true", 
                       help="Enable verbose logging")
    parser.add_argument("--quiet", "-q", action="store_true", 
                       help="Suppress logging output")
    
    args = parser.parse_args()
    
    # Setup logging
    if args.quiet:
        setup_logging("ERROR")
    elif args.verbose:
        setup_logging("DEBUG")
    else:
        setup_logging("INFO")
    
    # Initialize CLI
    cli = SubtitleToolCLI()
    
    try:
        # Handle different commands
        if args.list:
            cli.list_videos()
        elif args.search:
            cli.search_subtitles(args.search, args.video)
        elif args.stats:
            cli.show_stats()
        elif args.cleanup:
            cli.cleanup()
        elif args.input:
            cli.process_video(
                video_path=args.input,
                output_format=args.output,
                subtitle_format=args.format if args.output in ['subtitle', 'both'] else None,
                skip_validation=args.skip_validation,
                skip_rendering=args.skip_rendering
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