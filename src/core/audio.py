import logging
from pathlib import Path
from typing import Optional
from moviepy import VideoFileClip
from config.settings import TEMP_DIR

logger = logging.getLogger(__name__)

class AudioExtractor:
    """Handles audio extraction from video files"""
    
    def __init__(self, temp_dir: Optional[Path] = None):
        self.temp_dir = temp_dir or TEMP_DIR
    
    def extract_audio(self, video_path: str) -> str:
        """
        Extract audio from video file
        
        Args:
            video_path: Path to the video file
            
        Returns:
            Path to the extracted audio file
            
        Raises:
            Exception: If audio extraction fails
        """
        try:
            video_path = Path(video_path)
            if not video_path.exists():
                raise FileNotFoundError(f"Video file not found: {video_path}")
            
            logger.info(f"Extracting audio from {video_path}")
            
            # Load video
            video = VideoFileClip(str(video_path))
            
            # Generate audio output path
            audio_filename = f"{video_path.stem}.wav"
            audio_path = self.temp_dir / audio_filename
            
            # Extract audio
            video.audio.write_audiofile(str(audio_path))
            
            # Clean up
            video.close()
            
            logger.info(f"Audio extracted to {audio_path}")
            return str(audio_path)
            
        except Exception as e:
            logger.error(f"Error extracting audio from {video_path}: {e}")
            raise
    
    def cleanup_audio(self, audio_path: str) -> None:
        """
        Clean up temporary audio file
        
        Args:
            audio_path: Path to the audio file to delete
        """
        try:
            audio_file = Path(audio_path)
            if audio_file.exists():
                audio_file.unlink()
                logger.info(f"Cleaned up audio file: {audio_path}")
        except Exception as e:
            logger.warning(f"Failed to cleanup audio file {audio_path}: {e}") 