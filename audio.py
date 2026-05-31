"""
Audio module for text-to-speech generation and playback.
Handles Paimon's voice synthesis and audio file management.
"""
import os
import wave
import winsound
import threading
import tempfile
from google import genai
from google.genai import types
from config import PROJECT_ID, AUDIO_MODEL, VOICE_NAME, AUDIO_CONFIG

# Audio client for TTS generation
_audio_client = genai.Client(enterprise=True, project=PROJECT_ID)

# Temporary file management
_temp_files = []
_temp_lock = threading.Lock()


def initialize_audio():
    """Initialize audio subsystem. Call once at startup."""
    pass  # Audio client is initialized globally


def generate_and_play_speech(text_content):
    """
    Generate speech from text and play it.
    This is a blocking call - wait for completion before returning.
    """
    try:
        clean_text = text_content.strip()
        if not clean_text:
            return
        
        # Generate audio via Gemini
        directed_content = f"Say enthusiastically, high-pitched, and bubbly: {clean_text}"
        response = _audio_client.models.generate_content(
            model=AUDIO_MODEL,
            contents=directed_content,
            config=types.GenerateContentConfig(
                response_modalities=["AUDIO"],
                speech_config=types.SpeechConfig(
                    voice_config=types.VoiceConfig(
                        prebuilt_voice_config=types.PrebuiltVoiceConfig(voice_name=VOICE_NAME)
                    )
                )
            )
        )
        
        audio_bytes = response.candidates[0].content.parts[0].inline_data.data
        
        # Save to temporary WAV file
        tmp = tempfile.NamedTemporaryFile(suffix=".wav", delete=False)
        with wave.open(tmp.name, "wb") as wf:
            wf.setnchannels(AUDIO_CONFIG["channels"])
            wf.setsampwidth(AUDIO_CONFIG["sample_width"])
            wf.setframerate(AUDIO_CONFIG["frame_rate"])
            wf.writeframes(audio_bytes)
        
        # Manage temp files
        with _temp_lock:
            for old_file in _temp_files[:]:
                try:
                    os.remove(old_file)
                    _temp_files.remove(old_file)
                except OSError:
                    pass
            _temp_files.append(tmp.name)
        
        # Play audio
        winsound.PlaySound(tmp.name, winsound.SND_FILENAME | winsound.SND_ASYNC)
    
    except Exception as e:
        print(f"\n[Audio Error: {e}]")


def play_speech_async(text_content):
    """
    Generate and play speech asynchronously in a background thread.
    Returns immediately while audio plays.
    """
    thread = threading.Thread(
        target=generate_and_play_speech,
        args=(text_content,),
        daemon=True
    )
    thread.start()


def cleanup_audio_files():
    """Clean up all temporary audio files."""
    with _temp_lock:
        for temp_file in _temp_files:
            try:
                os.remove(temp_file)
            except OSError:
                pass
        _temp_files.clear()
