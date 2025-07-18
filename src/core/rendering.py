import logging
from pathlib import Path
from typing import List, Optional
from moviepy import VideoFileClip, TextClip, CompositeVideoClip
from src.models.subtitle import Subtitle
from config.settings import (
    FONT_PATH, FONT_SIZE_RATIO, SUBTITLE_HEIGHT_RATIO,
    TEXT_COLOR, STROKE_COLOR, STROKE_WIDTH, OUTPUT_DIR
)

logger = logging.getLogger(__name__)

class SubtitleRenderer:
    """Handles video rendering with subtitles"""
    
    def __init__(self, 
                 font_path: Optional[str] = None,
                 output_dir: Optional[Path] = None):
        """
        Initialize subtitle renderer
        
        Args:
            font_path: Path to font file
            output_dir: Output directory for rendered videos
        """
        self.font_path = font_path or str(FONT_PATH)
        self.output_dir = output_dir or OUTPUT_DIR
        
        # Validate font path
        if not Path(self.font_path).exists():
            logger.warning(f"Font file not found: {self.font_path}")
            self.font_path = None  # Use default font
    
    def render(self, video_path: str, subtitles: List[Subtitle]) -> str:
        """
        Render video with subtitles
        
        Args:
            video_path: Path to input video file
            subtitles: List of subtitle objects
            
        Returns:
            Path to output video file
            
        Raises:
            Exception: If rendering fails
        """
        try:
            video_path = Path(video_path)
            if not video_path.exists():
                raise FileNotFoundError(f"Video file not found: {video_path}")
            
            logger.info(f"Rendering subtitles for {video_path}")
            
            # Load video
            video = VideoFileClip(str(video_path))
            
            # Create text clips
            text_clips = self._create_text_clips(video, subtitles)
            
            # Composite video with subtitles
            final_video = CompositeVideoClip([video] + text_clips)
            
            # Generate output path
            output_filename = f"{video_path.stem}_subtitled{video_path.suffix}"
            output_path = self.output_dir / output_filename
            
            # Write final video
            logger.info("Writing final video...")
            final_video.write_videofile(
                str(output_path),
                codec='libx264',
                audio_codec='aac',
                temp_audiofile='temp-audio.m4a',
                remove_temp=True
            )
            
            # Clean up
            video.close()
            final_video.close()
            
            logger.info(f"Video rendered successfully: {output_path}")
            return str(output_path)
            
        except Exception as e:
            logger.error(f"Error rendering subtitles for {video_path}: {e}")
            raise
    
    def _create_text_clips(self, video: VideoFileClip, subtitles: List[Subtitle]) -> List[TextClip]:
        """
        Create text clips for subtitles
        
        Args:
            video: VideoFileClip object
            subtitles: List of subtitle objects
            
        Returns:
            List of TextClip objects
        """
        text_clips = []
        
        for subtitle in subtitles:
            try:
                # Calculate text size based on video dimensions
                text_width = int(video.w * FONT_SIZE_RATIO)
                text_height = int(video.h * SUBTITLE_HEIGHT_RATIO)
                
                # Create text clip
                txt_clip = TextClip(
                    text=subtitle.text,
                    font=self.font_path,
                    method='caption',
                    size=(text_width, text_height),
                    color=TEXT_COLOR,
                    stroke_color=STROKE_COLOR,
                    stroke_width=STROKE_WIDTH,
                    duration=subtitle.duration
                ).with_start(subtitle.start_time).with_position(('center', 'bottom'))
                
                text_clips.append(txt_clip)
                
            except Exception as e:
                logger.warning(f"Error creating text clip for subtitle at {subtitle.start_time}s: {e}")
                continue
        
        logger.info(f"Created {len(text_clips)} text clips")
        return text_clips
    
    def render_subtitle_file(self, video_path: str, subtitles: List[Subtitle], 
                           format: str = 'srt') -> str:
        """
        Render subtitles to file format
        
        Args:
            video_path: Path to video file
            subtitles: List of subtitle objects
            format: Subtitle format (srt, vtt, ass)
            
        Returns:
            Path to subtitle file
        """
        try:
            video_path = Path(video_path)
            output_filename = f"{video_path.stem}.{format}"
            output_path = self.output_dir / output_filename
            
            if format.lower() == 'srt':
                self._write_srt_file(subtitles, output_path)
            elif format.lower() == 'vtt':
                self._write_vtt_file(subtitles, output_path)
            elif format.lower() == 'ass':
                self._write_ass_file(subtitles, output_path)
            else:
                raise ValueError(f"Unsupported subtitle format: {format}")
            
            logger.info(f"Subtitle file created: {output_path}")
            return str(output_path)
            
        except Exception as e:
            logger.error(f"Error creating subtitle file: {e}")
            raise
    
    def _write_srt_file(self, subtitles: List[Subtitle], output_path: Path) -> None:
        """Write subtitles in SRT format"""
        with open(output_path, 'w', encoding='utf-8') as f:
            for i, subtitle in enumerate(subtitles, 1):
                start_time = self._format_time_srt(subtitle.start_time)
                end_time = self._format_time_srt(subtitle.end_time)
                
                f.write(f"{i}\n")
                f.write(f"{start_time} --> {end_time}\n")
                f.write(f"{subtitle.text}\n\n")
    
    def _write_vtt_file(self, subtitles: List[Subtitle], output_path: Path) -> None:
        """Write subtitles in VTT format"""
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write("WEBVTT\n\n")
            
            for subtitle in subtitles:
                start_time = self._format_time_vtt(subtitle.start_time)
                end_time = self._format_time_vtt(subtitle.end_time)
                
                f.write(f"{start_time} --> {end_time}\n")
                f.write(f"{subtitle.text}\n\n")
    
    def _write_ass_file(self, subtitles: List[Subtitle], output_path: Path) -> None:
        """Write subtitles in ASS format"""
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write("[Script Info]\n")
            f.write("Title: Generated Subtitles\n")
            f.write("ScriptType: v4.00+\n\n")
            
            f.write("[V4+ Styles]\n")
            f.write("Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding\n")
            f.write("Style: Default,Arial,20,&H00FFFFFF,&H000000FF,&H00000000,&H00000000,0,0,0,0,100,100,0,0,1,2,2,2,10,10,10,1\n\n")
            
            f.write("[Events]\n")
            f.write("Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text\n")
            
            for subtitle in subtitles:
                start_time = self._format_time_ass(subtitle.start_time)
                end_time = self._format_time_ass(subtitle.end_time)
                
                f.write(f"Dialogue: 0,{start_time},{end_time},Default,,0,0,0,,{subtitle.text}\n")
    
    def _format_time_srt(self, seconds: float) -> str:
        """Format time for SRT format (HH:MM:SS,mmm)"""
        hours = int(seconds // 3600)
        minutes = int((seconds % 3600) // 60)
        secs = int(seconds % 60)
        millisecs = int((seconds % 1) * 1000)
        return f"{hours:02d}:{minutes:02d}:{secs:02d},{millisecs:03d}"
    
    def _format_time_vtt(self, seconds: float) -> str:
        """Format time for VTT format (HH:MM:SS.mmm)"""
        hours = int(seconds // 3600)
        minutes = int((seconds % 3600) // 60)
        secs = int(seconds % 60)
        millisecs = int((seconds % 1) * 1000)
        return f"{hours:02d}:{minutes:02d}:{secs:02d}.{millisecs:03d}"
    
    def _format_time_ass(self, seconds: float) -> str:
        """Format time for ASS format (H:MM:SS.cc)"""
        hours = int(seconds // 3600)
        minutes = int((seconds % 3600) // 60)
        secs = int(seconds % 60)
        centisecs = int((seconds % 1) * 100)
        return f"{hours}:{minutes:02d}:{secs:02d}.{centisecs:02d}" 