import os
import re
from uuid import uuid4

import streamlit as st

from src.download import video_title, download_subtitles, postprocess
from src.llm import create_timecodes

from dotenv import load_dotenv

load_dotenv()

def main():
    st.title("YouTube Timecodes Generator")

    # Language selection
    languages = {
        "Arabic": "ar",
        "Bengali": "bn",
        "Bulgarian": "bg",
        "Catalan": "ca",
        "Chinese": "cn",
        "Croatian": "hr",
        "Czech": "cs",
        "Danish": "da",
        "Dutch": "nl",
        "English": "en",
        "Finnish": "fi",
        "French": "fr",
        "German": "de",
        "Greek": "el",
        "Gujarati": "gu",
        "Hebrew": "he",
        "Hindi": "hi",
        "Hungarian": "hu",
        "Indonesian": "id",
        "Italian": "it",
        "Japanese": "ja",
        "Kannada": "kn",
        "Korean": "ko",
        "Latvian": "lv",
        "Lithuanian": "lt",
        "Malay": "ms",
        "Malayalam": "ml",
        "Marathi": "mr",
        "Norwegian": "no",
        "Polish": "pl",
        "Portuguese": "pt",
        "Romanian": "ro",
        "Russian": "ru",
        "Serbian": "sr",
        "Slovak": "sk",
        "Slovenian": "sl",
        "Spanish": "es",
        "Swedish": "sv",
        "Tamil": "ta",
        "Telugu": "te",
        "Thai": "th",
        "Turkish": "tr",
        "Ukrainian": "uk",
        "Vietnamese": "vi",
    }
    selected_language = st.selectbox(
        "Select subtitle language:",
        options=list(languages.keys()),
        index=9  # Default to English
    )
    
    # Paste url to youtube video
    youtube_url = st.text_input("Enter the link to the video on YouTube:")

    # Regex check youtube url
    if re.match(r"^https://www.youtube.com/watch\?v=[a-zA-Z0-9_-]*$", youtube_url) or \
        re.match(r"^https://www.youtube.com/shorts/[a-zA-Z0-9_-]*$", youtube_url):
        # Display video
        st.video(youtube_url)

        transcribe_button = st.empty()
        title_placeholder = st.empty()
        progress_placeholder = st.empty()

        # Button to download audio from youtube video
        if transcribe_button.button("Generate timecodes"):
            # Download audio
            try:
                import code
                transcribe_button.empty()

                # Set video title
                title = video_title(youtube_url)
                title_placeholder.title(title)
                
                progress_placeholder.text("Downloading subtitles...")

                # Create a runtimes folder and runtime id
                directory = os.getcwd() + "/runtimes"
                if not os.path.exists(directory):
                    os.makedirs(directory)
                runtime_id = str(uuid4())
                output_path = directory + "/" + runtime_id
                
                # Download audio to runtimes/ folder with selected language
                output_path = download_subtitles(
                    youtube_url, 
                    output_path,
                    language=languages[selected_language]
                )
                subtitle_text = postprocess(output_path)
            
            except Exception as e:
                print(e)
                st.error("Please enter correct YouTube link or subtitles might not be available in selected language!")
                transcribe_button.empty()
                title_placeholder.empty()
                progress_placeholder.empty()
                st.stop()

            # Summarize
            try:
                assert os.environ["LLM_API_KEY"], "LLM_API_KEY not found!"

                progress_placeholder.text("Timecodes creating...")

                # Summarize text
                timecodes = create_timecodes(subtitle_text, selected_language)

                st.text_area("Result", timecodes, height=300)
            except Exception as e:
                print(e)
                st.error("Timecodes generation error. Please try again!")
                title_placeholder.empty()
                progress_placeholder.empty()
                st.stop()

            progress_placeholder.empty()

if __name__ == "__main__":
    main()