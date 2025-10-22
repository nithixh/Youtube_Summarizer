"""
Transcription Agent using faster-whisper
Windows-friendly with prebuilt wheels
"""
import json
from pathlib import Path
from typing import Dict, List, Any
from faster_whisper import WhisperModel


class WhisperTranscriber:
    """Agent for transcribing audio using faster-whisper"""

    def __init__(self, transcripts_dir: Path, model_name: str = 'base'):
        self.transcripts_dir = Path(transcripts_dir)
        self.transcripts_dir.mkdir(parents=True, exist_ok=True)
        self.model_name = model_name
        self.model = None

    def load_model(self):
        """Lazy load Whisper model"""
        if self.model is None:
            print(f"Loading Whisper model: {self.model_name}...")
            # Use CPU with int8 for Windows compatibility
            self.model = WhisperModel(
                self.model_name, 
                device="cpu",
                compute_type="int8"
            )
        return self.model

    def transcribe_audio(self, audio_path: str, video_id: str) -> Dict[str, Any]:
        """Transcribe audio file to text with timestamps"""

        if not Path(audio_path).exists():
            raise FileNotFoundError(f"Audio file not found: {audio_path}")

        model = self.load_model()

        print(f"Transcribing audio: {Path(audio_path).name}")

        try:
            # Transcribe with word-level timestamps
            segments, info = model.transcribe(
                audio_path,
                word_timestamps=True,
                language='en'  # Auto-detect if None
            )

            # Process segments
            transcript_segments = []
            full_text = []

            for segment in segments:
                segment_data = {
                    'id': segment.id,
                    'start': round(segment.start, 2),
                    'end': round(segment.end, 2),
                    'text': segment.text.strip()
                }

                # Add words if available
                if hasattr(segment, 'words') and segment.words:
                    segment_data['words'] = [
                        {
                            'word': word.word.strip(),
                            'start': round(word.start, 2),
                            'end': round(word.end, 2)
                        }
                        for word in segment.words
                    ]

                transcript_segments.append(segment_data)
                full_text.append(segment.text.strip())

            # Create transcript data
            transcript_data = {
                'video_id': video_id,
                'language': info.language,
                'duration': info.duration,
                'full_text': ' '.join(full_text),
                'segments': transcript_segments
            }

            # Save to file
            transcript_file = self.transcripts_dir / f"{video_id}_transcript.json"
            with open(transcript_file, 'w', encoding='utf-8') as f:
                json.dump(transcript_data, f, indent=2, ensure_ascii=False)

            print(f"Transcription completed: {len(transcript_segments)} segments")

            return {
                'transcript_file': str(transcript_file),
                'transcript_data': transcript_data,
                'word_count': len(' '.join(full_text).split())
            }

        except Exception as e:
            raise Exception(f"Transcription failed: {str(e)}")

    def load_transcript(self, transcript_file: str) -> Dict[str, Any]:
        """Load existing transcript from file"""
        try:
            with open(transcript_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            raise Exception(f"Failed to load transcript: {str(e)}")

    def format_timestamp(self, seconds: float) -> str:
        """Format seconds as MM:SS"""
        minutes = int(seconds // 60)
        secs = int(seconds % 60)
        return f"{minutes:02d}:{secs:02d}"

    def get_sentences_with_timestamps(self, transcript_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Extract sentences with timestamps"""
        sentences = []
        for segment in transcript_data.get('segments', []):
            text = segment['text'].strip()
            if text:
                sentences.append({
                    'text': text,
                    'start': segment['start'],
                    'end': segment['end'],
                    'timestamp': self.format_timestamp(segment['start'])
                })
        return sentences
