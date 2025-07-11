import streamlit as st
from youtube_transcript_api import YouTubeTranscriptApi, NoTranscriptFound, TranscriptsDisabled
from urllib.parse import urlparse, parse_qs
from docx import Document
import os

def extract_video_id(video_url):
    try:
        parsed_url = urlparse(video_url)
        if "youtube.com" in parsed_url.netloc:
            video_id = parse_qs(parsed_url.query).get('v')
            if video_id:
                return video_id[0]
        elif "youtu.be" in parsed_url.netloc:
            return parsed_url.path.lstrip('/')
        elif len(video_url) == 11:
            return video_url
        raise ValueError("Invalid YouTube URL or ID.")
    except Exception as e:
        raise ValueError(f"Invalid YouTube URL: {e}")

def get_transcript(video_id, languages=['ja', 'en']):
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
    return "\n\n".join([f"[{entry['start']:.2f}s] {entry['text']}" for entry in transcript_data])

def save_to_docx(text, filename):
    document = Document()
    for paragraph in text.split("\n\n"):
        document.add_paragraph(paragraph)
    document.save(filename)

def main():
    st.set_page_config(page_title="YouTube Transcript to Word", page_icon="📄")
    st.title("📄 YouTube Transcript to Word")
    st.write("Paste a YouTube video URL. The app will extract the subtitles (Japanese preferred) and let you download them as a Word file.")

    video_url = st.text_input("🎥 Enter YouTube Video URL")

    if st.button("Generate Transcript"):
        if not video_url.strip():
            st.error("Please enter a valid YouTube video URL.")
            return

        try:
            video_id = extract_video_id(video_url)
            transcript = get_transcript(video_id)

            if transcript:
                formatted_text = format_transcript(transcript)
                filename = f"{video_id}_transcript.docx"
                save_to_docx(formatted_text, filename)

                with open(filename, "rb") as file:
                    st.success("✅ Transcript generated!")
                    st.download_button(
                        label="📥 Download Word File",
                        data=file,
                        file_name=filename,
                        mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document"
                    )
                os.remove(filename)
            else:
                st.warning("Transcript not available in Japanese or English.")
        except ValueError as e:
            st.error(str(e))

main()
