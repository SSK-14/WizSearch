import io
import streamlit as st
from streamlit_mic_recorder import mic_recorder
import replicate

def transcribe_audio(audio_bio, max_retries=1):
    for _ in range(max_retries):
        try:
            response = replicate.run(
                "openai/whisper:4d50797290df275329f202e48c76360b3f22b08d28c196cbc54600319435f8d2",
                input={
                    "audio": audio_bio,
                    "model": "large",
                }
            )
            return response["transcription"]
        except Exception as e:
            print(str(e))  
    return None

def stt(key="speech-to-text"):
    if '_last_speech_to_text_transcript_id' not in st.session_state:
        st.session_state._last_speech_to_text_transcript_id = 0
    
    if '_last_speech_to_text_transcript' not in st.session_state:
        st.session_state._last_speech_to_text_transcript = None
    
    if key and key + '_output' not in st.session_state:
        st.session_state[key + '_output'] = None

    col1, col2, col3 = st.columns(3)
    with col2:
        audio = mic_recorder(
            start_prompt="🎙️ Ask Your Question",
            stop_prompt="🚫 Stop recording",
            just_once=False,
            format="webm", 
            key=key
        )

    if audio is None:
        output = None
    else:
        id = audio['id']
        if id > st.session_state._last_speech_to_text_transcript_id:
            st.session_state._last_speech_to_text_transcript_id = id
            audio_bio = io.BytesIO(audio['bytes'])
            audio_bio.name = 'audio.webm'
            output = transcribe_audio(audio_bio)
            st.session_state._last_speech_to_text_transcript = output
        else:
            output = None

    if key:
        st.session_state[key + '_output'] = output
        
    return output

