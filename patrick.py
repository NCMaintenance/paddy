import streamlit as st
import random
import os
from io import BytesIO

APP_TITLE = "Patrick's Speech Games!"
YOUR_NAME = "Patrick"
CHEER_SOUND_FILENAME = "cheer.wav"

st.set_page_config(page_title=APP_TITLE, layout="wide", initial_sidebar_state="expanded")

# TTS setup
TTS_ENABLED = False
tts_engine = None
try:
    import pyttsx3
    tts_engine = pyttsx3.init()
    TTS_ENABLED = True
except Exception:
    pass

sound_file_path = os.path.join(os.path.dirname(__file__), CHEER_SOUND_FILENAME)
CHEER_SOUND_EXISTS = os.path.exists(sound_file_path)

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

# WebM-compatible speech recognizer (no pydub or ffmpeg)
def recognize_speech_from_audio_input():
    import speech_recognition as sr
    import av
    import numpy as np
    import soundfile as sf

    r = sr.Recognizer()

    audio_bytes = st.audio_input("🎤 Record your voice (max 5 seconds):", max_length=5)
    if audio_bytes is None:
        st.info("Please record your voice to continue.")
        return None, "No audio input"

    try:
        container = av.open(BytesIO(audio_bytes))
        audio_stream = container.streams.audio[0]

        frames = []
        for frame in container.decode(audio=0):
            frames.append(frame.to_ndarray())

        audio_array = np.concatenate(frames)
        sample_rate = audio_stream.rate

        wav_io = BytesIO()
        sf.write(wav_io, audio_array, sample_rate, format='WAV')
        wav_io.seek(0)

        with sr.AudioFile(wav_io) as source:
            audio_data = r.record(source)

        text = r.recognize_google(audio_data).lower()
        return text, None
    except sr.UnknownValueError:
        return None, "Could not understand audio"
    except Exception as e:
        return None, f"Recognition error: {e}"

WORD_LIST_RST = [
    "star", "rust", "storm", "rest", "train", "start", "trust", "roast",
    "strap", "crust", "store", "street", "stir", "stone", "sport", "strike",
    "straw", "strong", "risky", "treat", "resist", "stork", "stripe", "stirrup",
    "rattle", "stream", "tiger", "rocket", "rabbit", "rescue", "troop", "trick",
    "tree", "ranch", "track", "trunk", "ruler", "reader", "string", "ring"
]

def sounding_out_game():
    st.header("Sounding Out Words")
    st.write("Let's practice words with R, S, and T sounds!")
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
            spoken, error = recognize_speech_from_audio_input()
            if spoken:
                st.success(f"You said: {spoken}")
                speak_text("Nice try!")
            else:
                st.warning(f"Error: {error}")

def main():
    st.sidebar.title(APP_TITLE)
    st.sidebar.write(f"Hi {YOUR_NAME}! Choose a game:")

    game_choice = st.sidebar.radio("Games:", ["Sounding Out Words"])

    st.sidebar.write("---")
    if TTS_ENABLED:
        st.sidebar.success("✅ Text-to-Speech Ready")
    else:
        st.sidebar.warning("⚠️ TTS Not Available")

    if CHEER_SOUND_EXISTS:
        st.sidebar.success("✅ Cheer Sound Found")
    else:
        st.sidebar.warning("⚠️ Cheer Sound Not Found")

    # Only one game now
    sounding_out_game()

if __name__ == "__main__":
    main()
