from dataclasses import dataclass
from typing import Optional

@dataclass
class Subtitle:
    """Data class representing a subtitle segment"""
    start_time: float
    end_time: float
    text: str
    confidence: Optional[float] = None
    
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
            'confidence': self.confidence
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> 'Subtitle':
        """Create subtitle from dictionary"""
        return cls(
            start_time=data['start_time'],
            end_time=data['end_time'],
            text=data['text'],
            confidence=data.get('confidence')
        ) 