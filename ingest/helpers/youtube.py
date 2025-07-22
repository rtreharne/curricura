import os
import requests
from urllib.parse import urlparse, parse_qs
from youtube_transcript_api import YouTubeTranscriptApi
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
YOUTUBE_API_URL = "https://www.googleapis.com/youtube/v3/videos"


def extract_video_id(url: str) -> str:
    """
    Extracts the video ID from a YouTube URL.
    Supports various YouTube URL formats.
    """
    parsed_url = urlparse(url)
    if parsed_url.hostname in ["www.youtube.com", "youtube.com"]:
        return parse_qs(parsed_url.query).get("v", [None])[0]
    elif parsed_url.hostname in ["youtu.be"]:
        return parsed_url.path.lstrip("/")
    return None


def get_video_metadata(video_id: str) -> dict:
    """
    Fetch video metadata (title, description) using YouTube Data API.
    """
    params = {
        "part": "snippet",
        "id": video_id,
        "key": GOOGLE_API_KEY,
    }
    response = requests.get(YOUTUBE_API_URL, params=params)
    data = response.json()

    if "items" not in data or not data["items"]:
        raise ValueError(f"No video found with ID: {video_id}")

    snippet = data["items"][0]["snippet"]
    return {
        "title": snippet.get("title"),
        "description": snippet.get("description"),
    }


def get_video_transcript(video_id: str) -> str:
    """
    Fetch the transcript using youtube_transcript_api v1.x and return
    a plain text format with timestamps and lines, ready for parse_transcript().
    """
    try:
        api = YouTubeTranscriptApi()
        transcript = api.fetch(video_id, languages=['en'])

        # Build a raw text format: each line is timestamped like "0:01"
        formatted_lines = []
        for entry in transcript:
            start_time = int(entry.start)
            minutes = start_time // 60
            seconds = start_time % 60
            timestamp = f"{minutes}:{seconds:02d}"
            formatted_lines.append(timestamp)
            formatted_lines.append(entry.text)

        return "\n".join(formatted_lines)

    except Exception as e:
        return f"ERROR: {e}"





def fetch_youtube_data(url: str) -> dict:
    """
    Main function to fetch both metadata and transcript for a given YouTube URL.
    """
    video_id = extract_video_id(url)
    if not video_id:
        raise ValueError("Invalid YouTube URL.")

    metadata = get_video_metadata(video_id)
    transcript = get_video_transcript(video_id)

    return {
        "video_id": video_id,
        "title": metadata["title"],
        "description": metadata["description"],
        "transcript": transcript,
    }


# Test script (runs only if file is executed directly)
if __name__ == "__main__":
    test_url = "https://youtu.be/2Igdytf8zW4?si=0FDA-GXaywrepyTm"
    data = fetch_youtube_data(test_url)
    print(f"Title: {data['title']}")
    print(f"Description: {data['description'][:100]}...")  # First 100 chars
    print(f"Transcript sample: {data['transcript']}")
