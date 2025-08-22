import logging
from typing import List
import whisper
from src.models.subtitle import Subtitle
from config.settings import WHISPER_MODEL, LANGUAGE

logger = logging.getLogger(__name__)

class Transcriber:
    """Handles speech-to-text transcription using Whisper"""
    
    def __init__(self, model_name: str = None, language: str = None):
        """
        Initialize transcriber with Whisper model
        
        Args:
            model_name: Whisper model name (default from settings)
            language: Language code (default from settings)
        """
        self.model_name = model_name or WHISPER_MODEL
        self.language = language or LANGUAGE
        self.model = None
        self._load_model()
    
    def _load_model(self) -> None:
        """Load Whisper model"""
        try:
            logger.info(f"Loading Whisper model: {self.model_name}")
            self.model = whisper.load_model(self.model_name)
            logger.info("Whisper model loaded successfully")
        except Exception as e:
            logger.error(f"Error loading Whisper model: {e}")
            raise
    
    def transcribe(self, audio_path: str) -> List[Subtitle]:
        """
        Transcribe audio file to subtitles
        
        Args:
            audio_path: Path to the audio file
            
        Returns:
            List of Subtitle objects
            
        Raises:
            Exception: If transcription fails
        """
        try:
            logger.info(f"Transcribing audio: {audio_path}")
            
            # Perform transcription
            
            result = self.model.transcribe(
                audio_path, 
                language=self.language,
                verbose=True
            )
            
            subtitles = []
            for segment in result['segments']:
                subtitle = Subtitle(
                    start_time=segment['start'],
                    end_time=segment['end'],
                    text=segment['text'].strip(),
                    confidence=segment.get('avg_logprob')
                )
                subtitles.append(subtitle)
            
            logger.info(f"Transcription completed: {len(subtitles)} segments")
            return subtitles
            
        except Exception as e:
            logger.error(f"Error transcribing audio {audio_path}: {e}")
            raise
    
    def transcribe_with_timestamps(self, audio_path: str, timestamps: List[tuple]) -> List[Subtitle]:
        """
        Transcribe audio with custom timestamps
        
        Args:
            audio_path: Path to the audio file
            timestamps: List of (start, end) time tuples
            
        Returns:
            List of Subtitle objects
        """
        try:
            logger.info(f"Transcribing audio with custom timestamps: {audio_path}")
            
            subtitles = []
            for start_time, end_time in timestamps:
                result = self.model.transcribe(
                    audio_path,
                    language=self.language,
                    start=start_time,
                    end=end_time
                )
                
                if result['segments']:
                    segment = result['segments'][0]
                    subtitle = Subtitle(
                        start_time=start_time,
                        end_time=end_time,
                        text=segment['text'].strip(),
                        confidence=segment.get('avg_logprob')
                    )
                    subtitles.append(subtitle)
            
            logger.info(f"Custom transcription completed: {len(subtitles)} segments")
            return subtitles
            
        except Exception as e:
            logger.error(f"Error transcribing audio with timestamps {audio_path}: {e}")
            raise 
