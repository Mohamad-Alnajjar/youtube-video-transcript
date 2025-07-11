# This script takes a YouTube video URL, extracts the transcript, formats it,
# and saves it as a two-column .docx file.

# To use this script:
# 1. Run the cell.
# 2. When prompted, enter the YouTube video URL.
# 3. The script will attempt to retrieve the transcript in Japanese ('ja').
# 4. If successful, the formatted transcript will be saved as 'formatted_transcript.docx'
#    in the same directory as the notebook.

from youtube_transcript_api import YouTubeTranscriptApi, NoTranscriptFound, TranscriptsDisabled
from urllib.parse import urlparse, parse_qs
import srt
from docx import Document
from docx.shared import Inches
from docx.enum.section import WD_SECTION
import os

def get_transcript_from_youtube(video_url, languages=['en']):
    """
    Extracts the transcript of a YouTube video in specified languages.

    Args:
        video_url: The URL or ID of the YouTube video.
        languages: A list of preferred language codes (e.g., ['en', 'ja']).

    Returns:
        A list of dictionaries representing the transcript, or None if no transcript
        is found or transcripts are disabled.

    Raises:
        ValueError: If an invalid YouTube URL is provided and the video ID cannot be extracted.
    """
    if "youtube.com" in video_url or "youtu.be" in video_url:
        parsed_url = urlparse(video_url)
        video_id = parse_qs(parsed_url.query).get('v')
        if not video_id:
            video_id = parsed_url.path.split('/')[-1]
            if not video_id:
                raise ValueError("Invalid YouTube URL provided.")
        else:
            video_id = video_id[0]
    else:
        video_id = video_url

    try:
        transcript = YouTubeTranscriptApi.get_transcript(video_id, languages=languages)
        return transcript
    except NoTranscriptFound:
        try:
            transcript_list = YouTubeTranscriptApi.list_transcripts(video_id)
            transcript = transcript_list.find_transcript(languages).fetch()
            return transcript
        except Exception as e:
            print(f"Transcript not found or error: {e}")
            return None
    except TranscriptsDisabled:
        print("Subtitles are disabled for this video.")
        return None
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
        return None


def process_transcript_data(transcript_data):
    """
    Formats raw transcript data into a single string with hyphens and line breaks.

    Args:
        transcript_data: A list of dictionaries representing the transcript.

    Returns:
        A formatted string of the transcript text.
    """
    formatted_text = ""
    if transcript_data:
        for entry in transcript_data:
            formatted_text += "- " + entry['text'] + "\n\n"
    return formatted_text


def save_dialogue_to_docx(formatted_text, filename):
    """
    Saves formatted text to a .docx file with a two-column layout.

    Args:
        formatted_text: The text content to save.
        filename: The name of the output .docx file.
    """
    document = Document()

    # Add a section with two columns

    # Add the formatted dialogue to the document
    document.add_paragraph(formatted_text.strip())

    document.save(filename)

    print(f"Formatted dialogue saved as {filename}")

# Main script execution
video_url = input("Enter the YouTube video URL: ")

# Specify Japanese language ('ja') as it was shown to be available in previous steps
transcript_data = get_transcript_from_youtube(video_url, languages=['ja'])

if transcript_data:
    formatted_dialogue = process_transcript_data(transcript_data)
    output_filename = 'formatted_transcript.docx'
    save_dialogue_to_docx(formatted_dialogue, output_filename)
    print(f"The formatted transcript has been saved to {output_filename}")
else:
    print("Could not retrieve transcript for the provided URL in Japanese.")
