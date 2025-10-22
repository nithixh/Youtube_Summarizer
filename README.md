# 🎥 YouTube Summarization Agent

A complete, Windows-friendly web application that automatically downloads, transcribes, and summarizes YouTube videos into structured, chaptered summaries using **100% free, local tools**.

![Python](https://img.shields.io/badge/Python-3.9+-blue)
![Platform](https://img.shields.io/badge/Platform-Windows-success)
![License](https://img.shields.io/badge/License-MIT-green)

## ✨ Features

- **🔒 100% Local Processing** - All processing happens on your machine
- **🪟 Windows-Optimized** - Uses packages with prebuilt wheels for easy installation
- **⚡ Fast & Reliable** - Uses faster-whisper and lightweight summarization
- **📊 Smart Chunking** - TF-IDF + cosine similarity for topic detection
- **📝 Extractive Summaries** - Sumy-based summarization (no heavy LLMs needed)
- **📥 Multiple Formats** - Download as TXT or JSON
- **📚 History Tracking** - Optional SQLite database

## 🛠️ Tech Stack (All Windows-Friendly!)

| Component | Technology | Why This Choice |
|-----------|------------|-----------------|
| **Video Download** | yt-dlp | Single executable, works perfectly on Windows |
| **Transcription** | faster-whisper | Prebuilt wheels, faster than openai-whisper |
| **Chunking** | scikit-learn TF-IDF | Lightweight, no GPU needed |
| **Summarization** | Sumy (LexRank) | Pure Python, extractive (reliable) |
| **Backend** | Flask 3.0 | Simple, proven, easy to run |
| **Frontend** | Bootstrap 5 | Clean UI, no build process |
| **Database** | SQLite | Built into Python |

## 📋 Prerequisites

Before installation, ensure you have:

1. **Python 3.9+** ([Download from python.org](https://www.python.org/downloads/))
2. **FFmpeg** (required for audio processing)
   - Download from: https://github.com/BtbN/FFmpeg-Builds/releases
   - Extract and add to PATH (see instructions below)

## 🚀 Installation (Windows)

### Step 1: Install Python

1. Download Python 3.9 or newer from [python.org](https://www.python.org/downloads/)
2. **Important**: Check "Add Python to PATH" during installation
3. Verify installation:
   ```cmd
   python --version
   ```

### Step 2: Install FFmpeg

1. Download FFmpeg from [GitHub](https://github.com/BtbN/FFmpeg-Builds/releases)
   - Get `ffmpeg-master-latest-win64-gpl.zip`
2. Extract to a folder (e.g., `C:\ffmpeg`)
3. Add to PATH:
   - Open "Environment Variables" (search in Windows)
   - Under "System Variables", find "Path"
   - Click "Edit" → "New"
   - Add: `C:\ffmpeg\bin` (adjust path as needed)
   - Click "OK" on all windows
4. Verify installation:
   ```cmd
   ffmpeg -version
   ```

### Step 3: Setup Application

1. **Extract the ZIP file** to your desired location (e.g., `C:\Users\YourName\youtube_summarizer`)

2. **Open Command Prompt** in that folder:
   - Hold Shift and right-click in the folder
   - Select "Open PowerShell window here" or "Open command window here"

3. **Create virtual environment**:
   ```cmd
   python -m venv venv
   ```

4. **Activate virtual environment**:
   ```cmd
   venv\Scripts\activate
   ```
   You should see `(venv)` in your command prompt.

5. **Install dependencies**:
   ```cmd
   pip install --upgrade pip
   pip install -r requirements.txt
   ```
   This will take a few minutes. All packages have prebuilt wheels for Windows!

6. **Download NLTK data** (one-time):
   ```cmd
   python -c "import nltk; nltk.download('punkt')"
   ```

7. **Copy environment file**:
   ```cmd
   copy .env.example .env
   ```

## 🎯 Running the Application

### First Time Setup

```cmd
REM Navigate to project folder
cd youtube_summarizer_windows

REM Activate virtual environment
venv\Scripts\activate

REM Run the application
python app.py
```

### Subsequent Runs

Simply run:
```cmd
venv\Scripts\activate
python app.py
```

The application will start on **http://127.0.0.1:5000**

Open this URL in your web browser!

## 📖 How to Use

1. **Open the web interface**: Navigate to http://127.0.0.1:5000 in your browser
2. **Paste YouTube URL**: Enter any YouTube video URL
3. **Click "Summarize Video"**: Watch the progress in real-time
4. **View Results**: See chaptered summaries with timestamps
5. **Download**: Get summaries as TXT or JSON files

### Processing Time

| Video Length | Typical Processing Time |
|--------------|------------------------|
| 10 minutes   | 2-4 minutes |
| 30 minutes   | 5-10 minutes |
| 60 minutes   | 10-20 minutes |

*Times depend on your CPU speed*

## ⚙️ Configuration

Edit `.env` file to customize settings:

```env
# Transcription Model
WHISPER_MODEL=base
# Options: tiny (fastest), base (balanced), small, medium, large

# Chunking Method  
CHUNKING_METHOD=tfidf
# Options: tfidf (recommended, fast), semantic (slower, requires sentence-transformers)

# Number of sentences per summary
SUMMARY_SENTENCES=3

# Video length limit (minutes)
MAX_VIDEO_LENGTH_MINUTES=120
```

## 🎨 Project Structure

```
youtube_summarizer_windows/
├── app.py                      # Main Flask application
├── config.py                   # Configuration management
├── requirements.txt            # Python dependencies
├── .env.example                # Configuration template
├── src/
│   ├── agents/                 # AI processing agents
│   │   ├── youtube_downloader.py
│   │   ├── whisper_transcriber.py
│   │   ├── text_chunker.py
│   │   └── text_summarizer.py
│   ├── workflows/              # Orchestration logic
│   │   └── main_workflow.py
│   ├── utils/                  # Database & helpers
│   │   └── database.py
│   ├── templates/              # HTML templates
│   │   ├── index.html
│   │   ├── result.html
│   │   ├── history.html
│   │   └── error.html
│   └── static/                 # CSS/JS (if needed)
├── data/                       # Generated data
│   ├── downloads/              # Temporary audio files
│   ├── transcripts/            # Transcript JSON files
│   └── summaries/              # Summary JSON files
└── tests/                      # Test scripts
```

## 🔧 Troubleshooting

### Common Issues on Windows

#### 1. "Python not found"
- Make sure Python is added to PATH during installation
- Restart Command Prompt after installation

#### 2. "ffmpeg not found"
- Verify FFmpeg is in PATH: `ffmpeg -version`
- Restart Command Prompt after adding to PATH
- Try full path: `C:\ffmpeg\bin\ffmpeg.exe`

#### 3. "No module named 'flask'"
- Make sure virtual environment is activated: `venv\Scripts\activate`
- Reinstall: `pip install -r requirements.txt`

#### 4. Download fails
- Check your internet connection
- Some videos may be geo-restricted or age-restricted
- Try a different video to test

#### 5. Transcription is slow
- Use smaller model: Set `WHISPER_MODEL=tiny` in `.env`
- Close other applications to free up CPU
- Consider upgrading to `base` model for better accuracy

#### 6. Out of memory errors
- Use smaller whisper model (`tiny` or `base`)
- Process shorter videos
- Close other applications

### Getting Help

1. Check the **Troubleshooting** section above
2. Verify all prerequisites are installed
3. Try the sample video provided in tests/
4. Check console output for specific error messages

## 🧪 Testing

A sample test script is included:

```cmd
python tests/run_sample.py
```

This will process a short public domain video and save results to `samples/`.

## 🎓 How It Works

### 1. Download Phase
- Uses **yt-dlp** to download audio from YouTube
- Extracts MP3 format (192kbps quality)
- Validates video duration limits

### 2. Transcription Phase
- **faster-whisper** transcribes audio to text
- Generates word-level timestamps
- Works entirely offline (after model download)

### 3. Chunking Phase
- Breaks transcript into sentences using NLTK
- Calculates **TF-IDF vectors** for each sentence
- Groups similar sentences using **cosine similarity**
- Creates topical segments (3-15 sentences each)

### 4. Summarization Phase
- Uses **Sumy's LexRank** algorithm
- Extractive summarization (selects actual sentences)
- No hallucination risk (unlike generative models)
- Fast and deterministic

## 🔄 Chunking Methods Explained

### TF-IDF Method (Default, Recommended)
- **Fast**: No model loading required
- **Reliable**: Pure mathematical approach
- **How**: Calculates term importance, groups similar sentences
- **Best for**: Most videos, Windows systems

### Semantic Method (Optional)
- **Slower**: Requires sentence-transformers model
- **Better**: Understands context more deeply
- **How**: Uses neural embeddings for similarity
- **Best for**: Complex technical content
- **Setup**: Uncomment lines in requirements.txt

## 📊 Output Formats

### JSON Format
```json
{
  "video_id": "dQw4w9WgXcQ",
  "total_chapters": 5,
  "chapters": [
    {
      "chapter_id": 0,
      "title": "Introduction to Topic",
      "timestamp": "00:15",
      "summary": "Key points extracted from this section...",
      "original_text": "Full transcript text..."
    }
  ]
}
```

### TXT Format
```
==================================================
YouTube Video Summary
==================================================
Video ID: dQw4w9WgXcQ
Total Chapters: 5
==================================================

Chapter 1: Introduction to Topic
Timestamp: [00:15]
Summary: Key points extracted from this section...
--------------------------------------------------
```

## 🚀 Advanced Configuration

### Using Different Models

**Whisper Models** (in `.env`):
- `tiny` - Fastest, lowest accuracy (~1GB RAM)
- `base` - **Recommended**, good balance (~1GB RAM)
- `small` - Better accuracy (~2GB RAM)
- `medium` - High accuracy (~5GB RAM)
- `large` - Best accuracy (~10GB RAM)

### Enabling Semantic Chunking

1. Edit `requirements.txt`, uncomment:
   ```
   sentence-transformers==2.2.2
   ```
2. Reinstall:
   ```cmd
   pip install -r requirements.txt
   ```
3. Edit `.env`:
   ```
   CHUNKING_METHOD=semantic
   ```

### Using Transformer Summarization

For better (but slower) summaries:

1. Edit `requirements.txt`, uncomment:
   ```
   torch==2.1.0
   transformers==4.35.0
   ```
2. Reinstall packages
3. Edit `.env`:
   ```
   SUMMARIZER=transformer
   ```

**Note**: This downloads ~500MB of models and requires more RAM.

## 🔒 Privacy & Security

- **All processing is local** - no data sent to cloud services
- **YouTube URLs** are the only external requests (via yt-dlp)
- **No tracking or analytics**
- **No API keys required**
- Downloaded audio files can be auto-deleted after processing

## 📝 License

MIT License - see LICENSE file for details.

## 🙏 Acknowledgments

- **[yt-dlp](https://github.com/yt-dlp/yt-dlp)** - YouTube downloader
- **[faster-whisper](https://github.com/guillaumekln/faster-whisper)** - Fast transcription
- **[Sumy](https://github.com/miso-belica/sumy)** - Extractive summarization
- **[scikit-learn](https://scikit-learn.org/)** - Machine learning tools
- **[Flask](https://flask.palletsprojects.com/)** - Web framework
- **[Bootstrap](https://getbootstrap.com/)** - UI framework

## 📞 Support

For issues or questions:
1. Check the **Troubleshooting** section
2. Review error messages in the console
3. Ensure all prerequisites are installed correctly

---

**Built for Windows users who want reliable, local video summarization without complex setup!** 🎉
