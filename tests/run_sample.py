"""
Sample test script for YouTube Summarization Agent
Tests the full pipeline with a short video
"""
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from config import config
from src.workflows import SummarizationWorkflow


def test_sample_video():
    """Test with a short sample video"""

    # Use a short public domain video (example)
    # Replace with an actual short test video URL
    test_url = "https://www.youtube.com/watch?v=jNQXAC9IVRw"  # "Me at the zoo" - first YouTube video (18 seconds)

    print("=" * 60)
    print("YouTube Summarization Agent - Test Script")
    print("=" * 60)
    print(f"Test video: {test_url}")
    print("=" * 60)
    print()

    # Create workflow
    workflow = SummarizationWorkflow(config)

    # Process video
    print("Starting processing...\n")

    try:
        for update in workflow.process_video(test_url, cleanup=False):
            step = update.get('step', 'unknown')
            status = update.get('status', 'unknown')
            message = update.get('message', '')
            progress = update.get('progress', 0)

            print(f"[{step:15s}] {progress:3d}% - {message}")

            if status == 'error':
                print(f"\nERROR: {message}")
                return False

            if step == 'completed':
                print("\n" + "=" * 60)
                print("SUCCESS! Processing completed.")
                print("=" * 60)

                video_id = update.get('video_id')
                if video_id:
                    summary_file = config.SUMMARIES_DIR / f"{video_id}_summary.json"
                    print(f"\nSummary saved to: {summary_file}")
                    print(f"View in browser: http://{config.HOST}:{config.PORT}/result/{video_id}")

                return True

    except KeyboardInterrupt:
        print("\n\nTest interrupted by user")
        return False
    except Exception as e:
        print(f"\n\nERROR: {str(e)}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    import os

    # Ensure we're in the right directory
    os.chdir(Path(__file__).parent.parent)

    print("\nIMPORTANT: Make sure FFmpeg is installed and in PATH!")
    print("Press Enter to continue or Ctrl+C to cancel...")
    input()

    success = test_sample_video()

    if success:
        print("\n✅ Test completed successfully!")
        print("Check the data/summaries/ folder for results.")
    else:
        print("\n❌ Test failed. Check error messages above.")

    sys.exit(0 if success else 1)
