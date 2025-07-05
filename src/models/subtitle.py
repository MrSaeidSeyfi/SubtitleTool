from dataclasses import dataclass, field
from typing import Optional

@dataclass
class Subtitle:
    """Data class representing a subtitle segment"""
    start_time: float
    end_time: float
    text: str
    confidence: Optional[float] = None
    speaker_id: Optional[int] = None
    speaker_color: Optional[str] = None
    
    def __post_init__(self):
        """Validate subtitle data after initialization"""
        if self.start_time < 0:
            raise ValueError("Start time cannot be negative")
        if self.end_time <= self.start_time:
            raise ValueError("End time must be greater than start time")
        if not self.text.strip():
            raise ValueError("Subtitle text cannot be empty")
    
    @property
    def duration(self) -> float:
        """Get the duration of the subtitle segment"""
        return self.end_time - self.start_time
    
    def to_dict(self) -> dict:
        """Convert subtitle to dictionary"""
        return {
            'start_time': self.start_time,
            'end_time': self.end_time,
            'text': self.text,
            'confidence': self.confidence,
            'speaker_id': self.speaker_id,
            'speaker_color': self.speaker_color
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> 'Subtitle':
        """Create subtitle from dictionary"""
        return cls(
            start_time=data['start_time'],
            end_time=data['end_time'],
            text=data['text'],
            confidence=data.get('confidence'),
            speaker_id=data.get('speaker_id'),
            speaker_color=data.get('speaker_color')
        )
    
    def get_speaker_label(self) -> str:
        """Get speaker label for display"""
        if self.speaker_id is not None:
            return f"Speaker {self.speaker_id + 1}"
        return ""
    
    def get_formatted_text(self, include_speaker: bool = True) -> str:
        """Get formatted text with optional speaker label"""
        if include_speaker and self.speaker_id is not None:
            return f"[{self.get_speaker_label()}] {self.text}"
        return self.text 