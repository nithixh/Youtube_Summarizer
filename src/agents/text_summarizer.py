"""
Summarization Agent using Sumy (extractive summarization)
Windows-friendly, lightweight, reliable
"""
import json
from pathlib import Path
from typing import List, Dict, Any
from sumy.parsers.plaintext import PlaintextParser
from sumy.nlp.tokenizers import Tokenizer
from sumy.summarizers.lex_rank import LexRankSummarizer
from sumy.summarizers.text_rank import TextRankSummarizer
from sumy.nlp.stemmers import Stemmer
from sumy.utils import get_stop_words


class TextSummarizer:
    """Agent for summarizing text chunks"""

    def __init__(
        self, 
        summaries_dir: Path,
        method: str = 'lexrank',
        summary_sentences: int = 3,
        language: str = 'english'
    ):
        self.summaries_dir = Path(summaries_dir)
        self.summaries_dir.mkdir(parents=True, exist_ok=True)
        self.method = method
        self.summary_sentences = summary_sentences
        self.language = language
        self.stemmer = Stemmer(language)
        self.summarizer = self._get_summarizer()

    def _get_summarizer(self):
        """Get the appropriate summarizer"""
        if self.method == 'textrank':
            summarizer = TextRankSummarizer(self.stemmer)
        else:  # Default to LexRank
            summarizer = LexRankSummarizer(self.stemmer)

        summarizer.stop_words = get_stop_words(self.language)
        return summarizer

    def summarize_text(self, text: str) -> str:
        """Summarize a single text chunk"""
        try:
            # Parse text
            parser = PlaintextParser.from_string(text, Tokenizer(self.language))

            # Generate summary
            summary_sentences = self.summarizer(
                parser.document, 
                self.summary_sentences
            )

            # Combine sentences
            summary = ' '.join([str(sentence) for sentence in summary_sentences])

            # Fallback if summary is empty
            if not summary.strip():
                # Return first N sentences as fallback
                sentences = text.split('. ')
                summary = '. '.join(sentences[:self.summary_sentences]) + '.'

            return summary.strip()

        except Exception as e:
            print(f"Summarization error: {e}")
            # Fallback: return first sentences
            sentences = text.split('. ')
            return '. '.join(sentences[:self.summary_sentences]) + '.'

    def generate_chapter_title(self, text: str, chunk_id: int) -> str:
        """Generate a simple chapter title"""
        # Extract key words/phrases from beginning of text
        words = text.split()[:10]

        # Simple title generation
        if len(words) >= 5:
            # Capitalize first few words
            title_words = [w.capitalize() for w in words[:5]]
            title = ' '.join(title_words)

            # Clean up
            title = title.rstrip('.,;:')

            # Limit length
            if len(title) > 50:
                title = title[:47] + '...'

            return title
        else:
            return f"Chapter {chunk_id + 1}"

    def summarize_chunks(self, chunks_data: Dict[str, Any]) -> Dict[str, Any]:
        """Summarize all chunks and create structured output"""

        video_id = chunks_data.get('video_id', 'unknown')
        chunks = chunks_data.get('chunks', [])

        if not chunks:
            raise ValueError("No chunks found to summarize")

        print(f"Summarizing {len(chunks)} chunks...")

        summarized_chapters = []

        for i, chunk in enumerate(chunks):
            chunk_text = chunk.get('text', '')
            chunk_id = chunk.get('chunk_id', i)

            print(f"  Processing chunk {i + 1}/{len(chunks)}...")

            try:
                # Generate summary
                summary = self.summarize_text(chunk_text)

                # Generate title
                title = self.generate_chapter_title(chunk_text, chunk_id)

                chapter_data = {
                    'chapter_id': chunk_id,
                    'title': title,
                    'timestamp': chunk.get('timestamp', '00:00'),
                    'start': chunk.get('start', 0),
                    'end': chunk.get('end', 0),
                    'summary': summary,
                    'original_text': chunk_text,
                    'sentence_count': chunk.get('sentence_count', 0)
                }

                summarized_chapters.append(chapter_data)

            except Exception as e:
                print(f"Error summarizing chunk {chunk_id}: {e}")
                # Add with minimal processing
                summarized_chapters.append({
                    'chapter_id': chunk_id,
                    'title': f"Chapter {chunk_id + 1}",
                    'timestamp': chunk.get('timestamp', '00:00'),
                    'start': chunk.get('start', 0),
                    'end': chunk.get('end', 0),
                    'summary': chunk_text[:200] + '...',
                    'original_text': chunk_text,
                    'sentence_count': chunk.get('sentence_count', 0)
                })

        # Create final summary structure
        result = {
            'video_id': video_id,
            'total_chapters': len(summarized_chapters),
            'chapters': summarized_chapters,
            'method': self.method,
            'summary_sentences': self.summary_sentences
        }

        # Save summaries
        summary_file = self.summaries_dir / f"{video_id}_summary.json"
        with open(summary_file, 'w', encoding='utf-8') as f:
            json.dump(result, f, indent=2, ensure_ascii=False)

        print(f"Saved summary to {summary_file}")
        return result

    def create_text_summary(self, summary_data: Dict[str, Any]) -> str:
        """Create plain text version of summary"""
        lines = []

        video_id = summary_data.get('video_id', 'Unknown')
        total_chapters = summary_data.get('total_chapters', 0)

        lines.append("=" * 60)
        lines.append("YouTube Video Summary")
        lines.append("=" * 60)
        lines.append(f"Video ID: {video_id}")
        lines.append(f"Total Chapters: {total_chapters}")
        lines.append("=" * 60)
        lines.append("")

        for chapter in summary_data.get('chapters', []):
            chapter_num = chapter['chapter_id'] + 1
            title = chapter['title']
            timestamp = chapter.get('timestamp', '00:00')
            summary = chapter['summary']

            lines.append(f"Chapter {chapter_num}: {title}")
            lines.append(f"Timestamp: [{timestamp}]")
            lines.append(f"Summary: {summary}")
            lines.append("-" * 60)
            lines.append("")

        return '\n'.join(lines)
