# kids_games_streamlit_v5.py
# Updated for Streamlit Cloud: No PyAudio, browser mic support via st.audio_input

import streamlit as st
import random
import os
import io
import speech_recognition as sr

# --- Configuration ---
APP_TITLE = "Patrick's Speech Games!"
YOUR_NAME = "Patrick"
CHEER_SOUND_FILENAME = "cheer.wav"

st.set_page_config(page_title=APP_TITLE, layout="wide", initial_sidebar_state="expanded")

# --- Status Initialization ---
initialization_status = []

# Text-to-Speech using pyttsx3 (optional)
TTS_ENABLED = False
try:
    import pyttsx3
    tts_engine = pyttsx3.init()
    TTS_ENABLED = True
    initialization_status.append(("success", "✅ Text-to-Speech Ready"))
except Exception as e:
    initialization_status.append(("warning", f"⚠️ TTS Error: {e}"))

# Speech recognition setup
SPEECH_REC_ENABLED = True
recognizer = sr.Recognizer()
initialization_status.append(("success", "✅ Speech Recognition Ready"))

# Cheer sound setup (optional)
sound_file_path = os.path.join(os.path.dirname(__file__), CHEER_SOUND_FILENAME)
CHEER_SOUND_EXISTS = os.path.exists(sound_file_path)
if CHEER_SOUND_EXISTS:
    initialization_status.append(("success", "✅ Cheer Sound Found"))
else:
    initialization_status.append(("warning", "⚠️ Cheer Sound Not Found"))

# --- Functions ---
def speak_text(text):
    if TTS_ENABLED:
        try:
            tts_engine.stop()
            tts_engine.say(text)
            tts_engine.runAndWait()
            return True
        except Exception:
            return False
    return False

def play_local_sound(file_path):
    if not os.path.exists(file_path):
        return
    try:
        with open(file_path, "rb") as f:
            audio_bytes = f.read()
        audio_format = 'audio/wav' if file_path.lower().endswith('.wav') else 'audio/mpeg'
        st.audio(audio_bytes, format=audio_format, autoplay=True)
    except Exception as e:
        st.error(f"Error playing sound: {e}", icon="🔊")

def recognize_speech_from_audiofile(audiofile):
    try:
        with sr.AudioFile(audiofile) as source:
            audio_data = recognizer.record(source)
        return recognizer.recognize_google(audio_data).lower(), None
    except sr.UnknownValueError:
        return None, "Could not understand audio"
    except Exception as e:
        return None, str(e)

def word_reader_game():
    st.header("Game 1: Word Reader")
    st.write("Type a word and I will read it out loud.")
    word = st.text_input("Enter a word:", key="word_input")
    if word:
        st.write(f"You entered: **{word}**")
        speak_text(word)

WORD_LIST_RST = [
    "star", "rust", "storm", "rest", "train", "start", "trust", "roast",
    "strap", "crust", "store", "street", "stir", "stone", "sport", "strike",
    "straw", "strong", "risky", "treat", "resist", "stork", "stripe", "stirrup",
    "rattle", "stream", "tiger", "rocket", "rabbit", "rescue", "troop", "trick",
    "tree", "ranch", "track", "trunk", "ruler", "reader", "string", "ring"
]

def sounding_out_game():
    st.header("Game 3: Sounding Out Words")
    st.write(f"Let's practice words with R, S, and T sounds!")
    st.info("Listen to the word, then try saying it!", icon="🗣️")

    if 'current_word' not in st.session_state:
        st.session_state.current_word = random.choice(WORD_LIST_RST)

    def new_word():
        st.session_state.current_word = random.choice(WORD_LIST_RST)
        st.rerun()

    word = st.session_state.current_word
    st.markdown(f"<h1 style='text-align:center'>{word}</h1>", unsafe_allow_html=True)

    col1, col2, col3 = st.columns(3)
    with col1:
        if st.button("🔄 New Word"):
            new_word()
    with col2:
        if st.button("🔊 Hear Word"):
            speak_text(f"The word is {word}")
    with col3:
        st.markdown("**🎤 Say the Word Below**")
        audio_file = st.audio_input("Record yourself saying the word")
        if audio_file:
            st.audio(audio_file)
            result, error = recognize_speech_from_audiofile(audio_file)
            if result:
                st.success(f"You said: {result}")
                speak_text("Nice try!")
            else:
                st.warning(f"Error: {error}")

def main():
    st.sidebar.title(APP_TITLE)
    st.sidebar.write(f"Hi {YOUR_NAME}! Choose a game:")

    game_choice = st.sidebar.radio("Games:", ["Word Reader", "Sounding Out Words"])

    st.sidebar.write("---")
    for status_type, message in initialization_status:
        if status_type == "success":
            st.sidebar.success(message)
        elif status_type == "warning":
            st.sidebar.warning(message)

    if game_choice == "Word Reader":
        word_reader_game()
    elif game_choice == "Sounding Out Words":
        sounding_out_game()

if __name__ == "__main__":
    main()
