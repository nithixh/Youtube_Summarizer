"""
Configuration management for YouTube Summarization Agent
"""
import os
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class Config:
    """Application configuration"""

    # Flask Configuration
    SECRET_KEY = os.getenv('SECRET_KEY', 'dev-secret-key-change-in-production')
    DEBUG = os.getenv('FLASK_DEBUG', 'True').lower() == 'true'

    # Server Configuration
    HOST = os.getenv('HOST', '127.0.0.1')
    PORT = int(os.getenv('PORT', 5000))

    # Data Directories
    DATA_DIR = Path(os.getenv('DATA_DIR', 'data'))
    DOWNLOADS_DIR = DATA_DIR / 'downloads'
    TRANSCRIPTS_DIR = DATA_DIR / 'transcripts'
    SUMMARIES_DIR = DATA_DIR / 'summaries'

    # Ensure directories exist
    for directory in [DATA_DIR, DOWNLOADS_DIR, TRANSCRIPTS_DIR, SUMMARIES_DIR]:
        directory.mkdir(parents=True, exist_ok=True)

    # Transcription Settings
    WHISPER_MODEL = os.getenv('WHISPER_MODEL', 'base')

    # Chunking Settings
    CHUNKING_METHOD = os.getenv('CHUNKING_METHOD', 'tfidf')
    MIN_CHUNK_SENTENCES = int(os.getenv('MIN_CHUNK_SENTENCES', 3))
    MAX_CHUNK_SENTENCES = int(os.getenv('MAX_CHUNK_SENTENCES', 15))
    SIMILARITY_THRESHOLD = float(os.getenv('SIMILARITY_THRESHOLD', 0.3))

    # Summarization Settings
    SUMMARIZER = os.getenv('SUMMARIZER', 'sumy')
    SUMMARY_SENTENCES = int(os.getenv('SUMMARY_SENTENCES', 3))

    # Processing Limits
    MAX_VIDEO_LENGTH_MINUTES = int(os.getenv('MAX_VIDEO_LENGTH_MINUTES', 120))
    ALLOWED_DOMAINS = os.getenv('ALLOWED_DOMAINS', 'youtube.com,youtu.be').split(',')

    # Database Configuration
    USE_DATABASE = os.getenv('USE_DATABASE', 'true').lower() == 'true'
    DATABASE_PATH = DATA_DIR / os.getenv('DATABASE_PATH', 'summaries.db').split('/')[-1]

    # Download Settings
    DOWNLOAD_FORMAT = os.getenv('DOWNLOAD_FORMAT', 'mp3')
    AUDIO_QUALITY = int(os.getenv('AUDIO_QUALITY', 192))

config = Config()
