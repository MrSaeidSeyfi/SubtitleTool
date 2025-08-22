import logging
import shutil
from pathlib import Path
from typing import List, Optional, Tuple
from config.settings import INPUT_DIR, OUTPUT_DIR, TEMP_DIR, SUPPORTED_VIDEO_FORMATS

logger = logging.getLogger(__name__)

class StorageManager:
    """Handles file storage and organization"""
    
    def __init__(self, 
                 input_dir: Optional[Path] = None,
                 output_dir: Optional[Path] = None,
                 temp_dir: Optional[Path] = None):
        """
        Initialize storage manager
        
        Args:
            input_dir: Input directory for videos
            output_dir: Output directory for processed videos
            temp_dir: Temporary directory for intermediate files
        """
        self.input_dir = input_dir or INPUT_DIR
        self.output_dir = output_dir or OUTPUT_DIR
        self.temp_dir = temp_dir or TEMP_DIR
        
        self.input_dir.mkdir(parents=True, exist_ok=True)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.temp_dir.mkdir(parents=True, exist_ok=True)
    
    def get_video_files(self, directory: Optional[Path] = None) -> List[Path]:
        """
        Get all supported video files from directory
        
        Args:
            directory: Directory to search (default: input_dir)
            
        Returns:
            List of video file paths
        """
        search_dir = directory or self.input_dir
        
        video_files = []
        for ext in SUPPORTED_VIDEO_FORMATS:
            video_files.extend(search_dir.glob(f"*{ext}"))
            video_files.extend(search_dir.glob(f"*{ext.upper()}"))
        
        logger.info(f"Found {len(video_files)} video files in {search_dir}")
        return sorted(video_files)
    
    def copy_to_input(self, source_path: str) -> Path:
        """
        Copy video file to input directory
        
        Args:
            source_path: Path to source video file
            
        Returns:
            Path to copied file in input directory
        """
        try:
            source = Path(source_path)
            if not source.exists():
                raise FileNotFoundError(f"Source file not found: {source_path}")
            
            dest_path = self.input_dir / source.name
            
            shutil.copy2(source, dest_path)
            
            logger.info(f"Copied {source_path} to {dest_path}")
            return dest_path
            
        except Exception as e:
            logger.error(f"Error copying file {source_path}: {e}")
            raise
    
    def move_to_output(self, source_path: str, new_name: Optional[str] = None) -> Path:
        """
        Move file to output directory
        
        Args:
            source_path: Path to source file
            new_name: Optional new filename
            
        Returns:
            Path to moved file in output directory
        """
        try:
            source = Path(source_path)
            if not source.exists():
                raise FileNotFoundError(f"Source file not found: {source_path}")
            
            if new_name:
                dest_path = self.output_dir / new_name
            else:
                dest_path = self.output_dir / source.name
            
            shutil.move(str(source), str(dest_path))
            
            logger.info(f"Moved {source_path} to {dest_path}")
            return dest_path
            
        except Exception as e:
            logger.error(f"Error moving file {source_path}: {e}")
            raise
    
    def create_temp_file(self, prefix: str = "temp", suffix: str = "") -> Path:
        """
        Create a temporary file
        
        Args:
            prefix: File prefix
            suffix: File suffix
            
        Returns:
            Path to temporary file
        """
        import tempfile
        
        temp_file = tempfile.NamedTemporaryFile(
            prefix=prefix,
            suffix=suffix,
            dir=self.temp_dir,
            delete=False
        )
        temp_file.close()
        
        logger.info(f"Created temporary file: {temp_file.name}")
        return Path(temp_file.name)
    
    def cleanup_temp_files(self, pattern: str = "*") -> int:
        """
        Clean up temporary files
        
        Args:
            pattern: File pattern to match
            
        Returns:
            Number of files cleaned up
        """
        try:
            count = 0
            for temp_file in self.temp_dir.glob(pattern):
                if temp_file.is_file():
                    temp_file.unlink()
                    count += 1
            
            logger.info(f"Cleaned up {count} temporary files")
            return count
            
        except Exception as e:
            logger.warning(f"Error cleaning up temp files: {e}")
            return 0
    
    def get_file_info(self, file_path: str) -> dict:
        """
        Get file information
        
        Args:
            file_path: Path to file
            
        Returns:
            Dictionary with file information
        """
        try:
            file_path = Path(file_path)
            if not file_path.exists():
                raise FileNotFoundError(f"File not found: {file_path}")
            
            stat = file_path.stat()
            
            info = {
                'name': file_path.name,
                'size': stat.st_size,
                'size_mb': round(stat.st_size / (1024 * 1024), 2),
                'created': stat.st_ctime,
                'modified': stat.st_mtime,
                'extension': file_path.suffix.lower(),
                'is_video': file_path.suffix.lower() in SUPPORTED_VIDEO_FORMATS
            }
            
            return info
            
        except Exception as e:
            logger.error(f"Error getting file info for {file_path}: {e}")
            raise
    
    def get_directory_size(self, directory: Optional[Path] = None) -> Tuple[int, float]:
        """
        Get directory size
        
        Args:
            directory: Directory to check (default: output_dir)
            
        Returns:
            Tuple of (file_count, size_mb)
        """
        search_dir = directory or self.output_dir
        
        try:
            file_count = 0
            total_size = 0
            
            for file_path in search_dir.rglob("*"):
                if file_path.is_file():
                    file_count += 1
                    total_size += file_path.stat().st_size
            
            size_mb = round(total_size / (1024 * 1024), 2)
            
            logger.info(f"Directory {search_dir}: {file_count} files, {size_mb} MB")
            return file_count, size_mb
            
        except Exception as e:
            logger.error(f"Error getting directory size for {search_dir}: {e}")
            raise
    
    def backup_file(self, file_path: str, backup_dir: Optional[Path] = None) -> Path:
        """
        Create backup of file
        
        Args:
            file_path: Path to file to backup
            backup_dir: Backup directory (default: temp_dir)
            
        Returns:
            Path to backup file
        """
        try:
            source = Path(file_path)
            if not source.exists():
                raise FileNotFoundError(f"File not found: {file_path}")
            
            backup_dir = backup_dir or self.temp_dir
            backup_dir.mkdir(parents=True, exist_ok=True)
            
            from datetime import datetime
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_name = f"{source.stem}_{timestamp}{source.suffix}"
            backup_path = backup_dir / backup_name
            
            shutil.copy2(source, backup_path)
            
            logger.info(f"Created backup: {backup_path}")
            return backup_path
            
        except Exception as e:
            logger.error(f"Error creating backup of {file_path}: {e}")
            raise
    
    def validate_video_file(self, file_path: str) -> bool:
        """
        Validate video file
        
        Args:
            file_path: Path to video file
            
        Returns:
            True if valid video file
        """
        try:
            file_path = Path(file_path)
            
            if not file_path.exists():
                logger.warning(f"File does not exist: {file_path}")
                return False
            
            if file_path.suffix.lower() not in SUPPORTED_VIDEO_FORMATS:
                logger.warning(f"Unsupported video format: {file_path.suffix}")
                return False
            
            if file_path.stat().st_size < 1024:
                logger.warning(f"File too small: {file_path}")
                return False
            
            logger.info(f"Video file validated: {file_path}")
            return True
            
        except Exception as e:
            logger.error(f"Error validating video file {file_path}: {e}")
            return False 
