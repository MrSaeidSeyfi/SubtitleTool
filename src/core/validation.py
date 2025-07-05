import logging
import re
from typing import List
from spellchecker import SpellChecker
from src.models.subtitle import Subtitle

logger = logging.getLogger(__name__)

class SubtitleValidator:
    """Handles subtitle validation and correction"""
    
    def __init__(self):
        """Initialize spell checker"""
        self.spell_checker = SpellChecker()
    
    def validate_and_correct(self, subtitles: List[Subtitle]) -> List[Subtitle]:
        """
        Validate and correct subtitle text
        
        Args:
            subtitles: List of subtitle objects
            
        Returns:
            List of corrected subtitle objects
        """
        logger.info("Starting subtitle validation and correction")
        
        for subtitle in subtitles:
            self._check_spelling(subtitle)
            self._check_grammar(subtitle)
            self._check_punctuation(subtitle)
            self._check_formatting(subtitle)
        
        logger.info("Subtitle validation and correction completed")
        return subtitles
    
    def _check_spelling(self, subtitle: Subtitle) -> None:
        """Check and correct spelling errors"""
        try:
            # Split text into words, preserving punctuation
            words = re.findall(r'\b\w+\b', subtitle.text)
            
            if not words:
                return
            
            # Find misspelled words
            misspelled = self.spell_checker.unknown(words)
            
            if misspelled:
                logger.warning(f"Spelling errors at {subtitle.start_time}s: {misspelled}")
                
                # Correct misspelled words
                corrected_text = subtitle.text
                for word in misspelled:
                    correction = self.spell_checker.correction(word)
                    if correction and correction != word:
                        # Use word boundaries to avoid partial replacements
                        pattern = r'\b' + re.escape(word) + r'\b'
                        corrected_text = re.sub(pattern, correction, corrected_text)
                
                subtitle.text = corrected_text
                
        except Exception as e:
            logger.warning(f"Error during spelling check: {e}")
    
    def _check_grammar(self, subtitle: Subtitle) -> None:
        """Check for common grammar issues"""
        try:
            words = subtitle.text.split()
            
            # Check for repeated words
            for i in range(len(words) - 1):
                if (words[i].lower() == words[i + 1].lower() and 
                    len(words[i]) > 2):  # Ignore short words like "a", "an"
                    logger.warning(f"Repeated word at {subtitle.start_time}s: '{words[i]}'")
            
            # Check for common grammar patterns
            text_lower = subtitle.text.lower()
            
            # Check for double spaces
            if '  ' in subtitle.text:
                subtitle.text = ' '.join(subtitle.text.split())
                logger.info(f"Fixed double spaces at {subtitle.start_time}s")
            
            # Check for common contractions
            contractions = {
                "dont": "don't",
                "cant": "can't",
                "wont": "won't",
                "isnt": "isn't",
                "arent": "aren't",
                "havent": "haven't",
                "hasnt": "hasn't"
            }
            
            for wrong, correct in contractions.items():
                if wrong in text_lower:
                    pattern = r'\b' + re.escape(wrong) + r'\b'
                    subtitle.text = re.sub(pattern, correct, subtitle.text, flags=re.IGNORECASE)
                    logger.info(f"Fixed contraction at {subtitle.start_time}s: {wrong} -> {correct}")
                    
        except Exception as e:
            logger.warning(f"Error during grammar check: {e}")
    
    def _check_punctuation(self, subtitle: Subtitle) -> None:
        """Check and fix punctuation issues"""
        try:
            text = subtitle.text.strip()
            
            # Add period if missing at end
            if text and not text.endswith(('.', '!', '?', ':', ';')):
                subtitle.text = text + '.'
                logger.info(f"Added missing punctuation at {subtitle.start_time}s")
            
            # Fix multiple punctuation marks
            subtitle.text = re.sub(r'[.!?]{2,}', '.', subtitle.text)
            
            # Fix spacing around punctuation
            subtitle.text = re.sub(r'\s+([.!?,:;])', r'\1', subtitle.text)
            
        except Exception as e:
            logger.warning(f"Error during punctuation check: {e}")
    
    def _check_formatting(self, subtitle: Subtitle) -> None:
        """Check and fix formatting issues"""
        try:
            # Remove extra whitespace
            subtitle.text = ' '.join(subtitle.text.split())
            
            # Capitalize first letter
            if subtitle.text and subtitle.text[0].isalpha():
                subtitle.text = subtitle.text[0].upper() + subtitle.text[1:]
            
            # Fix common formatting issues
            subtitle.text = re.sub(r'\s+', ' ', subtitle.text)  # Multiple spaces
            subtitle.text = re.sub(r'^\s+|\s+$', '', subtitle.text)  # Leading/trailing spaces
            
        except Exception as e:
            logger.warning(f"Error during formatting check: {e}")
    
    def validate_subtitle_timing(self, subtitles: List[Subtitle]) -> List[Subtitle]:
        """
        Validate subtitle timing and fix overlaps
        
        Args:
            subtitles: List of subtitle objects
            
        Returns:
            List of validated subtitle objects
        """
        logger.info("Validating subtitle timing")
        
        if not subtitles:
            return subtitles
        
        # Sort by start time
        subtitles.sort(key=lambda x: x.start_time)
        
        # Check for overlaps and fix them
        for i in range(len(subtitles) - 1):
            current = subtitles[i]
            next_sub = subtitles[i + 1]
            
            if current.end_time > next_sub.start_time:
                # Fix overlap by adjusting end time
                overlap = current.end_time - next_sub.start_time
                current.end_time = next_sub.start_time - 0.1  # Small gap
                logger.warning(f"Fixed overlap at {current.start_time}s: reduced duration by {overlap:.2f}s")
        
        logger.info("Subtitle timing validation completed")
        return subtitles 