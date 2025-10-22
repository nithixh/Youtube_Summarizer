"""
Flask application for YouTube Summarization Agent
"""
import json
import os
from flask import Flask, render_template, request, jsonify, Response, send_file
from flask_cors import CORS
from pathlib import Path
from pydantic import BaseModel, validator

from config import config
from src.workflows import SummarizationWorkflow
from src.utils import DatabaseManager


# Create Flask app
app = Flask(__name__, template_folder='src/templates', static_folder='src/static')
app.config['SECRET_KEY'] = config.SECRET_KEY
CORS(app)

# Initialize workflow
workflow = SummarizationWorkflow(config)


# Pydantic validation model
class YouTubeURLInput(BaseModel):
    url: str
    cleanup: bool = True

    @validator('url')
    def validate_url(cls, v):
        if not v.strip():
            raise ValueError('URL cannot be empty')
        if not any(domain in v.lower() for domain in ['youtube.com', 'youtu.be']):
            raise ValueError('Must be a valid YouTube URL')
        return v.strip()


@app.route('/')
def index():
    """Main page"""
    return render_template('index.html')


@app.route('/summarize', methods=['POST'])
def summarize():
    """Summarize YouTube video"""
    try:
        # Validate input
        data = request.get_json()
        input_data = YouTubeURLInput(**data)

        # Process video and stream updates
        def generate_updates():
            try:
                for update in workflow.process_video(input_data.url, input_data.cleanup):
                    yield f"data: {json.dumps(update)}\\n\\n"
            except Exception as e:
                error_update = {
                    'step': 'error',
                    'status': 'error',
                    'message': f'Processing failed: {str(e)}',
                    'progress': 0
                }
                yield f"data: {json.dumps(error_update)}\\n\\n"

        return Response(
            generate_updates(),
            mimetype='text/event-stream',
            headers={
                'Cache-Control': 'no-cache',
                'Connection': 'keep-alive',
                'X-Accel-Buffering': 'no'
            }
        )

    except Exception as e:
        return jsonify({
            'error': 'Invalid input',
            'message': str(e)
        }), 400


@app.route('/result/<video_id>')
def show_result(video_id):
    """Show summary results"""
    try:
        summary_file = config.SUMMARIES_DIR / f"{video_id}_summary.json"

        if not summary_file.exists():
            return render_template('error.html', 
                                 error_message=f"Summary not found for video ID: {video_id}"), 404

        with open(summary_file, 'r', encoding='utf-8') as f:
            summary_data = json.load(f)

        return render_template('result.html', 
                             summary=summary_data,
                             video_id=video_id)
    except Exception as e:
        return render_template('error.html', 
                             error_message=f"Error loading results: {str(e)}"), 500


@app.route('/download/<video_id>/<format>')
def download_summary(video_id, format):
    """Download summary file"""
    try:
        summary_file = config.SUMMARIES_DIR / f"{video_id}_summary.json"

        if not summary_file.exists():
            return jsonify({'error': 'Summary not found'}), 404

        with open(summary_file, 'r', encoding='utf-8') as f:
            summary_data = json.load(f)

        if format == 'txt':
            # Create text version
            from src.agents import TextSummarizer
            summarizer = TextSummarizer(config.SUMMARIES_DIR)
            content = summarizer.create_text_summary(summary_data)

            # Save to temp file
            temp_file = config.SUMMARIES_DIR / f"{video_id}_summary.txt"
            with open(temp_file, 'w', encoding='utf-8') as f:
                f.write(content)

            return send_file(
                temp_file,
                mimetype='text/plain',
                as_attachment=True,
                download_name=f"{video_id}_summary.txt"
            )

        elif format == 'json':
            return send_file(
                summary_file,
                mimetype='application/json',
                as_attachment=True,
                download_name=f"{video_id}_summary.json"
            )
        else:
            return jsonify({'error': 'Invalid format'}), 400

    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/history')
def show_history():
    """Show processing history"""
    try:
        if not config.USE_DATABASE:
            return render_template('error.html',
                                 error_message="History feature is disabled"), 404

        db = DatabaseManager(config.DATABASE_PATH)
        summaries = db.get_recent_summaries()

        return render_template('history.html', summaries=summaries)
    except Exception as e:
        return render_template('error.html',
                             error_message=f"Error loading history: {str(e)}"), 500


@app.errorhandler(404)
def not_found(error):
    return render_template('error.html', error_message="Page not found"), 404


@app.errorhandler(500)
def internal_error(error):
    return render_template('error.html', error_message="Internal server error"), 500


if __name__ == '__main__':
    print("="*60)
    print("🎥 YouTube Summarization Agent")
    print("="*60)
    print(f"Running on: http://{config.HOST}:{config.PORT}")
    print(f"Data directory: {config.DATA_DIR}")
    print(f"Whisper model: {config.WHISPER_MODEL}")
    print(f"Chunking method: {config.CHUNKING_METHOD}")
    print(f"Summarizer: {config.SUMMARIZER}")
    print("="*60)
    print("\nPress Ctrl+C to stop\n")

    app.run(
        host=config.HOST,
        port=config.PORT,
        debug=config.DEBUG
    )
