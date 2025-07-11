import streamlit as st
from youtube_transcript_api import YouTubeTranscriptApi, NoTranscriptFound, TranscriptsDisabled
from urllib.parse import urlparse, parse_qs
from docx import Document
import os

def extract_video_id(video_url):
    """
    Extracts the YouTube video ID from the full URL.
    """
    try:
        parsed_url = urlparse(video_url)
        if "youtube.com" in parsed_url.netloc:
            # Standard YouTube URL, get 'v' param
            video_id = parse_qs(parsed_url.query).get('v')
            if video_id:
                return video_id[0]
            # Sometimes the video ID is in the path, like /embed/VIDEOID
            path_parts = parsed_url.path.split('/')
            if len(path_parts) >= 2 and path_parts[1] == "embed":
                return path_parts[2]
            raise ValueError("Invalid YouTube URL: video ID not found.")
        elif "youtu.be" in parsed_url.netloc:
            # Short URL, video ID is path part
            video_id = parsed_url.path.lstrip('/')
            if video_id:
                return video_id
            raise ValueError("Invalid YouTube URL: video ID not found.")
        else:
            # If input looks like a video id already, return as is
            if len(video_url) == 11:
                return video_url
            raise ValueError("Invalid YouTube URL.")
    except Exception as e:
        raise ValueError(f"Invalid YouTube URL: {e}")

def get_transcript(video_id, languages=['ja', 'en']):
    """
    Fetches transcript from YouTube.
    """
    try:
        return YouTubeTranscriptApi.get_transcript(video_id, languages=languages)
    except NoTranscriptFound:
        try:
            transcripts = YouTubeTranscriptApi.list_transcripts(video_id)
            return transcripts.find_transcript(languages).fetch()
        except Exception as e:
            st.error(f"Transcript error: {e}")
            return None
    except TranscriptsDisabled:
        st.warning("Subtitles are disabled for this video.")
        return None
    except Exception as e:
        st.error(f"Unexpected error: {e}")
        return None

def format_transcript(transcript_data):
    """
    Converts transcript list into clean text format with timestamps.
    """
    lines = []
    for entry in transcript_data:
        start = entry['start']
        text = entry['text']
        lines.append(f"[{start:.2f}s] {text}")
    return "\n\n".join(lines)

def save_to_docx(text, filename):
    """
    Saves the text into a Word document.
    """
    document = Document()
    section = document.sections[0]
    # Commented out to avoid possible errors:
    # section._sectPr.xpath('./w:cols')[0].set('num', '2')  # Two columns
    # Add each paragraph separately for better formatting
    for paragraph in text.split("\n\n"):
        document.add_paragraph(paragraph)
    document.save(filename)

def main():
    st.set_page_config(page_title="YouTube Transcript to DOCX", page_icon="📄")
    st.title("📄 YouTube Transcript to Word Doc")
    st.write("Enter a YouTube video URL. The app will extract subtitles (Japanese preferred), format them, and give you a downloadable Word file.")
    
    # Debug message to confirm app runs
    st.write("App started — waiting for input.")

    video_url = st.text_input("🎥 YouTube Video URL")

    if st.button("Generate Transcript"):
        if not video_url.strip():
            st.error("Please enter a valid YouTube video URL.")
            return

        try:
            video_id = extract_video_id(video_url)
            transcript = get_transcript(video_id, ['ja', 'en'])

            if transcript:
                formatted_text = format_transcript(transcript)
                filename = f"{video_id}_transcript.docx"
                save_to_docx(formatted_text, filename)

                with open(filename, "rb") as file:
                    st.success("✅ Transcript generated successfully!")
                    st.download_button(
                        label="📥 Download .docx File",
                        data=file,
                        file_name=filename,
                        mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document"
                    )
                os.remove(filename)
            else:
                st.warning("Transcript not available in Japanese or English.")
        except ValueError as e:
            st.error(str(e))

# Call main directly to ensure Streamlit runs it
main()
