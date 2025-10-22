"""
Text Chunking Agent using TF-IDF + Cosine Similarity
Windows-friendly, lightweight, no heavy dependencies
"""
import json
import nltk
from pathlib import Path
from typing import List, Dict, Any
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np

# Download required NLTK data
try:
    nltk.data.find('tokenizers/punkt')
except LookupError:
    print("Downloading NLTK punkt tokenizer...")
    nltk.download('punkt', quiet=True)


class TextChunker:
    """Agent for chunking text into topical segments"""

    def __init__(
        self, 
        transcripts_dir: Path,
        method: str = 'tfidf',
        min_sentences: int = 3,
        max_sentences: int = 15,
        similarity_threshold: float = 0.3
    ):
        self.transcripts_dir = Path(transcripts_dir)
        self.method = method
        self.min_sentences = min_sentences
        self.max_sentences = max_sentences
        self.similarity_threshold = similarity_threshold

    def chunk_by_tfidf(self, sentences: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Chunk sentences using TF-IDF + cosine similarity.
        Fast and reliable method for Windows.
        """
        if len(sentences) < self.min_sentences:
            # Return as single chunk if too few sentences
            return [{
                'chunk_id': 0,
                'sentences': sentences,
                'start': sentences[0]['start'],
                'end': sentences[-1]['end'],
                'timestamp': sentences[0]['timestamp']
            }]

        # Extract text
        texts = [s['text'] for s in sentences]

        # Calculate TF-IDF vectors
        vectorizer = TfidfVectorizer(
            max_features=100,
            stop_words='english',
            ngram_range=(1, 2)
        )

        try:
            tfidf_matrix = vectorizer.fit_transform(texts)
        except ValueError:
            # Fallback if TF-IDF fails (e.g., all stop words)
            return self._chunk_by_fixed_size(sentences)

        # Calculate similarities between consecutive sentences
        similarities = []
        for i in range(len(sentences) - 1):
            sim = cosine_similarity(
                tfidf_matrix[i:i+1], 
                tfidf_matrix[i+1:i+2]
            )[0][0]
            similarities.append(sim)

        # Find chunk boundaries (low similarity = topic change)
        chunks = []
        current_chunk = [sentences[0]]
        chunk_id = 0

        for i, (sentence, similarity) in enumerate(zip(sentences[1:], similarities), 1):
            # Check if we should start a new chunk
            should_split = (
                similarity < self.similarity_threshold and 
                len(current_chunk) >= self.min_sentences
            ) or len(current_chunk) >= self.max_sentences

            if should_split:
                # Save current chunk
                chunks.append({
                    'chunk_id': chunk_id,
                    'sentences': current_chunk,
                    'start': current_chunk[0]['start'],
                    'end': current_chunk[-1]['end'],
                    'timestamp': current_chunk[0]['timestamp']
                })
                # Start new chunk
                current_chunk = [sentence]
                chunk_id += 1
            else:
                current_chunk.append(sentence)

        # Add last chunk
        if current_chunk:
            chunks.append({
                'chunk_id': chunk_id,
                'sentences': current_chunk,
                'start': current_chunk[0]['start'],
                'end': current_chunk[-1]['end'],
                'timestamp': current_chunk[0]['timestamp']
            })

        print(f"Created {len(chunks)} chunks using TF-IDF method")
        return chunks

    def _chunk_by_fixed_size(self, sentences: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Fallback: chunk by fixed size"""
        chunks = []
        chunk_id = 0

        for i in range(0, len(sentences), self.max_sentences):
            chunk_sentences = sentences[i:i + self.max_sentences]
            if chunk_sentences:
                chunks.append({
                    'chunk_id': chunk_id,
                    'sentences': chunk_sentences,
                    'start': chunk_sentences[0]['start'],
                    'end': chunk_sentences[-1]['end'],
                    'timestamp': chunk_sentences[0]['timestamp']
                })
                chunk_id += 1

        return chunks

    def chunk_transcript(self, transcript_data: Dict[str, Any]) -> Dict[str, Any]:
        """Main chunking method"""

        # Extract sentences with timestamps
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

        if not sentences:
            raise ValueError("No sentences found in transcript")

        print(f"Chunking {len(sentences)} sentences...")

        # Chunk based on method
        if self.method == 'tfidf':
            chunks = self.chunk_by_tfidf(sentences)
        else:
            chunks = self._chunk_by_fixed_size(sentences)

        # Format chunks
        formatted_chunks = []
        for chunk in chunks:
            chunk_text = ' '.join([s['text'] for s in chunk['sentences']])
            formatted_chunks.append({
                'chunk_id': chunk['chunk_id'],
                'text': chunk_text,
                'start': chunk['start'],
                'end': chunk['end'],
                'timestamp': chunk['timestamp'],
                'sentence_count': len(chunk['sentences'])
            })

        result = {
            'video_id': transcript_data.get('video_id', 'unknown'),
            'total_chunks': len(formatted_chunks),
            'chunks': formatted_chunks,
            'method': self.method
        }

        # Save chunks
        video_id = transcript_data.get('video_id', 'unknown')
        chunks_file = self.transcripts_dir / f"{video_id}_chunks.json"
        with open(chunks_file, 'w', encoding='utf-8') as f:
            json.dump(result, f, indent=2, ensure_ascii=False)

        print(f"Saved {len(formatted_chunks)} chunks to {chunks_file}")
        return result

    @staticmethod
    def format_timestamp(seconds: float) -> str:
        """Format seconds as MM:SS"""
        minutes = int(seconds // 60)
        secs = int(seconds % 60)
        return f"{minutes:02d}:{secs:02d}"
