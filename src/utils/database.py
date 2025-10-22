"""
Simple SQLite database manager for storing summary history
"""
import sqlite3
import json
from pathlib import Path
from typing import List, Dict, Any, Optional
from datetime import datetime


class DatabaseManager:
    """Manage SQLite database for summary history"""

    def __init__(self, db_path: Path):
        self.db_path = Path(db_path)
        self.init_database()

    def init_database(self):
        """Initialize database schema"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()

            cursor.execute("""
                CREATE TABLE IF NOT EXISTS summaries (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    video_id TEXT NOT NULL UNIQUE,
                    video_title TEXT,
                    url TEXT,
                    summary_file TEXT,
                    total_chapters INTEGER,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)

            conn.commit()

    def add_summary(
        self, 
        video_id: str,
        video_title: str,
        url: str,
        summary_file: str,
        total_chapters: int
    ) -> bool:
        """Add a new summary to database"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()

                cursor.execute("""
                    INSERT OR REPLACE INTO summaries 
                    (video_id, video_title, url, summary_file, total_chapters)
                    VALUES (?, ?, ?, ?, ?)
                """, (video_id, video_title, url, summary_file, total_chapters))

                conn.commit()
                return True
        except Exception as e:
            print(f"Database error: {e}")
            return False

    def get_recent_summaries(self, limit: int = 20) -> List[Dict[str, Any]]:
        """Get recent summaries"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()

                cursor.execute("""
                    SELECT video_id, video_title, url, summary_file, 
                           total_chapters, created_at
                    FROM summaries
                    ORDER BY created_at DESC
                    LIMIT ?
                """, (limit,))

                rows = cursor.fetchall()

                summaries = []
                for row in rows:
                    summaries.append({
                        'video_id': row[0],
                        'video_title': row[1],
                        'url': row[2],
                        'summary_file': row[3],
                        'total_chapters': row[4],
                        'created_at': row[5]
                    })

                return summaries
        except Exception as e:
            print(f"Database error: {e}")
            return []

    def get_summary_by_id(self, video_id: str) -> Optional[Dict[str, Any]]:
        """Get summary by video ID"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()

                cursor.execute("""
                    SELECT video_id, video_title, url, summary_file,
                           total_chapters, created_at
                    FROM summaries
                    WHERE video_id = ?
                """, (video_id,))

                row = cursor.fetchone()

                if row:
                    return {
                        'video_id': row[0],
                        'video_title': row[1],
                        'url': row[2],
                        'summary_file': row[3],
                        'total_chapters': row[4],
                        'created_at': row[5]
                    }
                return None
        except Exception as e:
            print(f"Database error: {e}")
            return None
