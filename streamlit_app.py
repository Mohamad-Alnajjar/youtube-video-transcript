# This script takes a YouTube video URL, extracts the transcript, formats it,
# and saves it as a two-column .docx file.

# To use this script:
# 1. Run the cell.
# 2. When prompted, enter the YouTube video URL.
# 3. The script will attempt to retrieve the transcript in Japanese ('ja').
# 4. If successful, the formatted transcript will be saved as 'formatted_transcript.docx'
#    in the same directory as the notebook.
# streamlit_app.py

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
        if "youtube.com" in video_url or "youtu.be" in video_url:
            parsed_url = urlparse(video_url)
            video_id = parse_qs(parsed_url.query).get('v')
            if not video_id:
                video_id = parsed_url.path.split('/')[-1]
                if not video_id:
                    raise ValueError("Invalid YouTube URL.")
                return video_id
            return video_id[0]
        else:
            return video_url
    except Exception:
        raise ValueError("Invalid YouTube URL.")

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
    Converts transcript list into clean text format.
    """
    return "\n\n".join([f"- {entry['text']}" for entry in transcript_data])

def save_to_docx(text, filename):
    """
    Saves the text into a 2-column Word document.
    """
    document = Document()
    section = document.sections[0]
    section._sectPr.xpath('./w:cols')[0].set('num', '2')  # Two columns
    document.add_paragraph(text)
    document.save(filename)

def main():
    st.set_page_config(page_title="YouTube Transcript to DOCX", page_icon="📄")
    st.title("📄 YouTube Transcript to Word Doc")
    st.write("Enter a YouTube video URL. The app will extract subtitles (Japanese preferred), format them, and give you a downloadable Word file.")

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

if __name__ == "__main__":
    main()
