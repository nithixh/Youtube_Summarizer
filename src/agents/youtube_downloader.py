"""
YouTube Downloader Agent using yt-dlp
Windows-friendly implementation
"""
import os
import re
import yt_dlp
from pathlib import Path
from typing import Dict, Any, Optional
from urllib.parse import urlparse, parse_qs


class YouTubeDownloader:
    """Agent for downloading YouTube videos/audio"""

    def __init__(self, downloads_dir: Path, allowed_domains: list = None):
        self.downloads_dir = Path(downloads_dir)
        self.downloads_dir.mkdir(parents=True, exist_ok=True)
        self.allowed_domains = allowed_domains or ['youtube.com', 'youtu.be']

    def validate_url(self, url: str) -> bool:
        """Validate YouTube URL"""
        try:
            parsed = urlparse(url)
            domain = parsed.netloc.lower().replace('www.', '')
            return any(allowed in domain for allowed in self.allowed_domains)
        except Exception:
            return False

    def extract_video_id(self, url: str) -> Optional[str]:
        """Extract video ID from YouTube URL"""
        patterns = [
            r'(?:youtube\.com/watch\?v=|youtu\.be/)([a-zA-Z0-9_-]{11})',
            r'youtube\.com/embed/([a-zA-Z0-9_-]{11})',
        ]
        for pattern in patterns:
            match = re.search(pattern, url)
            if match:
                return match.group(1)
        return None

    def get_video_info(self, url: str) -> Dict[str, Any]:
        """Get video information without downloading"""
        ydl_opts = {
            'quiet': True,
            'no_warnings': True,
            'extract_flat': True,
        }

        try:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(url, download=False)
                return {
                    'id': info.get('id', ''),
                    'title': info.get('title', 'Unknown'),
                    'duration': info.get('duration', 0),
                    'uploader': info.get('uploader', 'Unknown'),
                    'description': info.get('description', '')[:500],
                }
        except Exception as e:
            raise Exception(f"Failed to get video info: {str(e)}")

    def download_audio(self, url: str, max_duration_minutes: int = 120) -> Dict[str, Any]:
        """Download audio from YouTube video"""

        if not self.validate_url(url):
            raise ValueError(f"Invalid YouTube URL or not from allowed domains")

        # Get video info
        video_info = self.get_video_info(url)
        video_id = video_info['id']

        # Check duration
        if video_info['duration'] > (max_duration_minutes * 60):
            raise ValueError(
                f"Video too long ({video_info['duration']//60} min). "
                f"Max allowed: {max_duration_minutes} min"
            )

        # Set download options
        output_path = str(self.downloads_dir / f"{video_id}.%(ext)s")

        ydl_opts = {
            'format': 'bestaudio/best',
            'outtmpl': output_path,
            'postprocessors': [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'mp3',
                'preferredquality': '192',
            }],
            'quiet': True,
            'no_warnings': True,
        }

        try:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                ydl.download([url])

            audio_file = self.downloads_dir / f"{video_id}.mp3"

            if not audio_file.exists():
                raise Exception("Audio file not found after download")

            return {
                'audio_path': str(audio_file),
                'video_info': video_info,
                'file_size': audio_file.stat().st_size
            }

        except Exception as e:
            raise Exception(f"Download failed: {str(e)}")

    def cleanup_file(self, file_path: str) -> bool:
        """Delete downloaded file"""
        try:
            if os.path.exists(file_path):
                os.remove(file_path)
                return True
            return False
        except Exception:
            return False
