from urllib.parse import urlparse, parse_qs
from youtube_transcript_api import YouTubeTranscriptApi
from youtube_transcript_api._errors import TranscriptsDisabled, NoTranscriptFound
import asyncio

def extract_video_id(youtube_url):
    parse_result = urlparse(youtube_url)
    hostname = parse_result.hostname
    if hostname == 'youtu.be':
        return parse_result.path[1:]
    elif hostname in {'www.youtube.com', 'youtube.com', 'm.youtube.com'} or hostname.endswith('youtube.com'):
        if parse_result.path == '/watch':
            return parse_qs(parse_result.query).get('v', [None])[0]
        elif parse_result.path.startswith('/embed/'):
            return parse_result.path.split('/')[2]
    else:
        return None
async def get_transcript(youtube_url):
    video_id = extract_video_id(youtube_url)
    if not video_id:
        return "Invalid or unsupported YouTube URL"
    try:
        # Retrieve the transcript using the video ID
        transcript_list = YouTubeTranscriptApi.list_transcripts(video_id)
        # Find the English transcript or the first available if no English transcript is found
        transcript = transcript_list.find_transcript(['en']).fetch()
        # Combine all text entries in the transcript
        combined_transcript = ' '.join([entry['text'] for entry in transcript])
        return combined_transcript
    except TranscriptsDisabled:
        return "Transcripts are disabled for this video."
    except NoTranscriptFound:
        return "No transcript found."
    except Exception as e:
        return f"An error occurred: {e}"

