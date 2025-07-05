import logging
import sqlite3
from pathlib import Path
from typing import List, Optional, Dict, Any
from src.models.subtitle import Subtitle
from config.settings import DB_PATH

logger = logging.getLogger(__name__)

class DatabaseManager:
    """Handles SQLite database operations for subtitles"""
    
    def __init__(self, db_path: Optional[str] = None):
        """
        Initialize database manager
        
        Args:
            db_path: Path to SQLite database file
        """
        self.db_path = db_path or str(DB_PATH)
        self._init_database()
    
    def _init_database(self) -> None:
        """Initialize database tables"""
        try:
            # Check if database exists and has the correct schema
            if self._needs_migration():
                logger.info("Database schema needs migration, recreating database...")
                self._recreate_database()
            
            with sqlite3.connect(self.db_path) as conn:
                conn.execute('''
                    CREATE TABLE IF NOT EXISTS subtitles (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        video_path TEXT NOT NULL,
                        start_time REAL NOT NULL,
                        end_time REAL NOT NULL,
                        text TEXT NOT NULL,
                        confidence REAL,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    )
                ''')
                
                conn.execute('''
                    CREATE TABLE IF NOT EXISTS videos (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        path TEXT UNIQUE NOT NULL,
                        duration REAL,
                        processed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    )
                ''')
                
                conn.execute('''
                    CREATE INDEX IF NOT EXISTS idx_subtitles_video 
                    ON subtitles(video_path)
                ''')
                
                conn.execute('''
                    CREATE INDEX IF NOT EXISTS idx_subtitles_time 
                    ON subtitles(start_time, end_time)
                ''')
                
            logger.info("Database initialized successfully")
            
        except Exception as e:
            logger.error(f"Error initializing database: {e}")
            raise
    
    def _needs_migration(self) -> bool:
        """Check if database needs migration"""
        try:
            if not Path(self.db_path).exists():
                return False
            
            with sqlite3.connect(self.db_path) as conn:
                # Check if subtitles table exists
                cursor = conn.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='subtitles'")
                if not cursor.fetchone():
                    return True
                
                # Check if video_path column exists
                cursor = conn.execute("PRAGMA table_info(subtitles)")
                columns = [row[1] for row in cursor.fetchall()]
                return 'video_path' not in columns
                
        except Exception as e:
            logger.warning(f"Error checking database schema: {e}")
            return True
    
    def _recreate_database(self) -> None:
        """Recreate database with new schema"""
        try:
            db_file = Path(self.db_path)
            if db_file.exists():
                # Create backup
                backup_path = db_file.with_suffix('.db.backup')
                db_file.rename(backup_path)
                logger.info(f"Created backup of old database: {backup_path}")
            
            # Create new database
            with sqlite3.connect(self.db_path) as conn:
                conn.execute('''
                    CREATE TABLE subtitles (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        video_path TEXT NOT NULL,
                        start_time REAL NOT NULL,
                        end_time REAL NOT NULL,
                        text TEXT NOT NULL,
                        confidence REAL,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    )
                ''')
                
                conn.execute('''
                    CREATE TABLE videos (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        path TEXT UNIQUE NOT NULL,
                        duration REAL,
                        processed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    )
                ''')
                
                conn.execute('''
                    CREATE INDEX idx_subtitles_video 
                    ON subtitles(video_path)
                ''')
                
                conn.execute('''
                    CREATE INDEX idx_subtitles_time 
                    ON subtitles(start_time, end_time)
                ''')
            
            logger.info("Database recreated successfully")
            
        except Exception as e:
            logger.error(f"Error recreating database: {e}")
            raise
    
    def insert_subtitles(self, video_path: str, subtitles: List[Subtitle]) -> None:
        """
        Insert subtitles into database
        
        Args:
            video_path: Path to the video file
            subtitles: List of subtitle objects
        """
        try:
            with sqlite3.connect(self.db_path) as conn:
                # Insert video record
                conn.execute('''
                    INSERT OR REPLACE INTO videos (path, processed_at)
                    VALUES (?, CURRENT_TIMESTAMP)
                ''', (video_path,))
                
                # Insert subtitles
                conn.executemany('''
                    INSERT INTO subtitles (video_path, start_time, end_time, text, confidence)
                    VALUES (?, ?, ?, ?, ?)
                ''', [
                    (video_path, s.start_time, s.end_time, s.text, s.confidence)
                    for s in subtitles
                ])
                
            logger.info(f"Inserted {len(subtitles)} subtitles for {video_path}")
            
        except Exception as e:
            logger.error(f"Error inserting subtitles: {e}")
            raise
    
    def get_subtitles(self, video_path: str) -> List[Subtitle]:
        """
        Get subtitles for a video
        
        Args:
            video_path: Path to the video file
            
        Returns:
            List of subtitle objects
        """
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.row_factory = sqlite3.Row
                cursor = conn.execute('''
                    SELECT start_time, end_time, text, confidence
                    FROM subtitles
                    WHERE video_path = ?
                    ORDER BY start_time
                ''', (video_path,))
                
                subtitles = []
                for row in cursor.fetchall():
                    subtitle = Subtitle(
                        start_time=row['start_time'],
                        end_time=row['end_time'],
                        text=row['text'],
                        confidence=row['confidence']
                    )
                    subtitles.append(subtitle)
                
                logger.info(f"Retrieved {len(subtitles)} subtitles for {video_path}")
                return subtitles
                
        except Exception as e:
            logger.error(f"Error retrieving subtitles: {e}")
            raise
    
    def get_video_info(self, video_path: str) -> Optional[Dict[str, Any]]:
        """
        Get video information
        
        Args:
            video_path: Path to the video file
            
        Returns:
            Video information dictionary or None
        """
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.row_factory = sqlite3.Row
                cursor = conn.execute('''
                    SELECT path, duration, processed_at
                    FROM videos
                    WHERE path = ?
                ''', (video_path,))
                
                row = cursor.fetchone()
                if row:
                    return dict(row)
                return None
                
        except Exception as e:
            logger.error(f"Error retrieving video info: {e}")
            raise
    
    def update_video_duration(self, video_path: str, duration: float) -> None:
        """
        Update video duration
        
        Args:
            video_path: Path to the video file
            duration: Video duration in seconds
        """
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.execute('''
                    UPDATE videos
                    SET duration = ?
                    WHERE path = ?
                ''', (duration, video_path))
                
            logger.info(f"Updated duration for {video_path}: {duration}s")
            
        except Exception as e:
            logger.error(f"Error updating video duration: {e}")
            raise
    
    def delete_subtitles(self, video_path: str) -> None:
        """
        Delete all subtitles for a video
        
        Args:
            video_path: Path to the video file
        """
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.execute('DELETE FROM subtitles WHERE video_path = ?', (video_path,))
                conn.execute('DELETE FROM videos WHERE path = ?', (video_path,))
                
            logger.info(f"Deleted subtitles for {video_path}")
            
        except Exception as e:
            logger.error(f"Error deleting subtitles: {e}")
            raise
    
    def get_processed_videos(self) -> List[str]:
        """
        Get list of processed video paths
        
        Returns:
            List of video paths
        """
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.execute('SELECT path FROM videos ORDER BY processed_at DESC')
                return [row[0] for row in cursor.fetchall()]
                
        except Exception as e:
            logger.error(f"Error retrieving processed videos: {e}")
            raise
    
    def get_subtitle_count(self, video_path: str) -> int:
        """
        Get number of subtitles for a video
        
        Args:
            video_path: Path to the video file
            
        Returns:
            Number of subtitles
        """
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.execute('''
                    SELECT COUNT(*) FROM subtitles WHERE video_path = ?
                ''', (video_path,))
                return cursor.fetchone()[0]
                
        except Exception as e:
            logger.error(f"Error counting subtitles: {e}")
            raise
    
    def search_subtitles(self, query: str, video_path: Optional[str] = None) -> List[Subtitle]:
        """
        Search subtitles by text content
        
        Args:
            query: Search query
            video_path: Optional video path to limit search
            
        Returns:
            List of matching subtitle objects
        """
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.row_factory = sqlite3.Row
                
                if video_path:
                    cursor = conn.execute('''
                        SELECT start_time, end_time, text, confidence
                        FROM subtitles
                        WHERE video_path = ? AND text LIKE ?
                        ORDER BY start_time
                    ''', (video_path, f'%{query}%'))
                else:
                    cursor = conn.execute('''
                        SELECT start_time, end_time, text, confidence
                        FROM subtitles
                        WHERE text LIKE ?
                        ORDER BY start_time
                    ''', (f'%{query}%',))
                
                subtitles = []
                for row in cursor.fetchall():
                    subtitle = Subtitle(
                        start_time=row['start_time'],
                        end_time=row['end_time'],
                        text=row['text'],
                        confidence=row['confidence']
                    )
                    subtitles.append(subtitle)
                
                logger.info(f"Found {len(subtitles)} subtitles matching '{query}'")
                return subtitles
                
        except Exception as e:
            logger.error(f"Error searching subtitles: {e}")
            raise 