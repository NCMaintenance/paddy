# kids_games.py - v4.1
# A collection of simple games for kids built with Streamlit.
# Games: Word Reader, Number/Color Guesser (Speech Input), Sounding Out Words

import streamlit as st
import random
import os
import streamlit.components.v1 as components
from pydub import AudioSegment
from pydub.playback import play
import os

# Optional: set path if ffmpeg isn't auto-detected
AudioSegment.converter = "/usr/bin/ffmpeg"  # Typical path on Streamlit Cloud

# --- Configuration ---
APP_TITLE = "Patrick's Fun Games!"
YOUR_NAME = "Patrick"
CHEER_SOUND_FILENAME = "cheer.wav"

st.set_page_config(page_title=APP_TITLE, layout="wide", initial_sidebar_state="expanded")

initialization_status = []

TTS_ENABLED = False
tts_engine = None
try:
    import pyttsx3
    tts_engine = pyttsx3.init()
    TTS_ENABLED = True
    initialization_status.append(("success", "✅ Text-to-Speech Ready"))
except Exception as e:
    initialization_status.append(("warning", f"⚠️ TTS Error: {e}"))

SPEECH_REC_ENABLED = False
recognizer = None
try:
    import speech_recognition as sr
    recognizer = sr.Recognizer()
    SPEECH_REC_ENABLED = True
    initialization_status.append(("success", "✅ Speech Recognition Ready"))
except Exception as e:
    initialization_status.append(("warning", f"⚠️ Speech Recognition Error: {e}"))

PYAUDIO_ENABLED = False
try:
    import pyaudio
    p = pyaudio.PyAudio()
    try:
        stream = p.open(format=pyaudio.paInt16, channels=1, rate=16000, input=True, frames_per_buffer=1024)
        stream.stop_stream()
        stream.close()
        PYAUDIO_ENABLED = True
        initialization_status.append(("success", "✅ Microphone Access Ready"))
    finally:
        p.terminate()
except Exception as e:
    initialization_status.append(("warning", f"⚠️ PyAudio Error: {e}"))

sound_file_path = os.path.join(os.path.dirname(__file__), CHEER_SOUND_FILENAME)
CHEER_SOUND_EXISTS = os.path.exists(sound_file_path)
if CHEER_SOUND_EXISTS:
    initialization_status.append(("success", f"✅ Cheer Sound Found"))
else:
    initialization_status.append(("warning", f"⚠️ Cheer Sound Not Found"))

def speak_text(text):
    if TTS_ENABLED and tts_engine and text:
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

def recognize_speech_from_mic(r):
    try:
        with sr.Microphone() as source:
            r.adjust_for_ambient_noise(source, duration=1)
            speak_text(f"Listening, {YOUR_NAME}!")
            st.info(f"Listening, {YOUR_NAME}...", icon="👂")
            audio = r.listen(source, timeout=5, phrase_time_limit=5)
            return r.recognize_google(audio).lower(), None
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
        if st.button("🎤 Say the Word"):
            spoken, error = recognize_speech_from_mic(recognizer)
            if spoken:
                st.success(f"You said: {spoken}")
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
