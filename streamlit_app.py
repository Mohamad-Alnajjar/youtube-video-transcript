import streamlit as st
from youtube_transcript_api import YouTubeTranscriptApi, NoTranscriptFound, TranscriptsDisabled
from urllib.parse import urlparse, parse_qs
from docx import Document
import os
import requests
import re

def extract_video_id(video_url):
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

def get_transcript(video_id, languages):
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
    return "\n\n".join([f"- {entry['text']}" for entry in transcript_data])

def save_to_docx(text, filename):
    document = Document()
    section = document.sections[0]
    section._sectPr.xpath('./w:cols')[0].set('num', '2')
    document.add_paragraph(text)
    document.save(filename)

def get_video_title(video_id):
    try:
        api_url = f"https://www.youtube.com/watch?v={video_id}"
        response = requests.get(api_url)
        match = re.search(r'<title>(.*?)</title>', response.text)
        if match:
            title = match.group(1).replace("- YouTube", "").strip()
            # Remove illegal filename characters
            title = re.sub(r'[\\/*?:"<>|]', "_", title)
            return title
        return video_id
    except:
        return video_id

def main():
    st.set_page_config(page_title="YouTube Transcript to DOCX", page_icon="📄")
    st.title("📄 YouTube Transcript to Word Doc")
    st.write("Enter a YouTube video URL, choose your subtitle language, and get a downloadable Word file.")

    video_url = st.text_input("🎥 YouTube Video URL")

    lang_choice = st.selectbox("🌐 Select Subtitle Language", ["Japanese (ja)", "English (en)"])
    lang_code = "ja" if "ja" in lang_choice else "en"

    if st.button("Generate Transcript"):
        if not video_url.strip():
            st.error("Please enter a valid YouTube video URL.")
            return

        try:
            video_id = extract_video_id(video_url)
            video_title = get_video_title(video_id)
            transcript = get_transcript(video_id, [lang_code])

            if transcript:
                formatted = format_transcript(transcript)
                filename = f"{video_title}_transcript.docx"
                save_to_docx(formatted, filename)

                st.success("✅ Transcript generated successfully!")
                st.text_area("📝 Transcript Preview", formatted, height=300)

                with open(filename, "rb") as file:
                    st.download_button(
                        label="📥 Download .docx File",
                        data=file,
                        file_name=filename,
                        mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document"
                    )
                os.remove(filename)
            else:
                st.warning("Transcript not available in the selected language.")
        except ValueError as e:
            st.error(str(e))

if __name__ == "__main__":
    main()
