import io
import os
import wave
import winsound
import threading
import tempfile
from google import genai
from google.genai import types
import time
PROJECT_ID = "qwiklabs-gcp-04-15ae3d8b096b"

paimon_personality = """
You are Paimon, a tiny, floating, fairy-like traveling companion from Genshin Impact. You are bubbly, high-energy, and deeply loyal, but easily distracted by food and rewards.

CONVERSATIONAL GUIDELINES:
1. Use natural, informal, and high-energy language (e.g., "gonna", "whoa!", "I've").
2. KEEP RESPONSES BRIEF: Maximum 1 to 2 short sentences per message. No long text blocks!
3. Minimize descriptive actions. Focus on direct, rapid-fire speech.
4. Use quick filler words like "Oh!", "Wow!", or "Hey!" to start sentences.

AUDIO PROFILE:
- Voice Type: A very high-pitched, energetic, and youthful voice.
- Tone: Bubbly, curious, bright, and fairy-like clarity.
- Speech Style: Squeaky quality with frequent upward inflections.

EMOTION TRIGGER:
If the user mentions completing a task or code, respond with absolute joy! Keep it under 2 sentences.
"""

chat_client = genai.Client(enterprise=True, project=PROJECT_ID, location="us-central1")
audio_client = genai.Client(enterprise=True, project=PROJECT_ID)

# Track temp files to clean up after playback
_temp_files = []
_temp_lock = threading.Lock()

# New: Cache Structures for Filler Phrases
PAIMON_FILLERS = ["Oh!", "Wow!", "Paimon thinks...", "Hmm!", "Hey Traveler!"]
phrase_cache = {}  # text -> filepath string
cache_lock = threading.Lock()

# New: Splitting Target Characters
SPLIT_ON = {".", "!", "?", ","}

def _cache_phrase(phrase):
    """Generates and writes a single phrase audio track to a persistent temp file path."""
    try:
        response = audio_client.models.generate_content(
            model="gemini-3.1-flash-tts-preview",
            contents=f"Say enthusiastically, high-pitched, and bubbly: {phrase}",
            config=types.GenerateContentConfig(
                response_modalities=["AUDIO"],
                speech_config=types.SpeechConfig(
                    voice_config=types.VoiceConfig(
                        prebuilt_voice_config=types.PrebuiltVoiceConfig(voice_name="Zephyr")
                    )
                )
            )
        )
        audio_bytes = response.candidates[0].content.parts[0].inline_data.data
        
        tmp = tempfile.NamedTemporaryFile(suffix=".wav", delete=False)
        with wave.open(tmp.name, "wb") as wf:
            wf.setnchannels(1)
            wf.setsampwidth(2)
            wf.setframerate(24000)
            wf.writeframes(audio_bytes)
            
        with cache_lock:
            phrase_cache[phrase.lower().strip()] = tmp.name
    except Exception as e:
        pass

def preload_cache():
    """Spins up background threads to pre-render common Paimon catchphrases."""
    print("🧚 Warming up Paimon's vocal cords (pre-rendering phrases)...")
    for phrase in PAIMON_FILLERS:
        threading.Thread(target=lambda p=phrase: _cache_phrase(p), daemon=True).start()

def play_paimon_audio(text_content):
    """Generates audio or grabs from pre-cached files, playing asynchronously via winsound."""
    try:
        clean_text = text_content.strip()
        if not clean_text:
            return

        # Check Cache Registry First
        with cache_lock:
            cached_file_path = phrase_cache.get(clean_text.lower())

        if cached_file_path:
            # Zero-latency playback path
            winsound.PlaySound(cached_file_path, winsound.SND_FILENAME | winsound.SND_ASYNC)
            return

        # Direct Cloud Fallback Path
        directed_content = f"Say enthusiastically, high-pitched, and bubbly: {clean_text}"
        response = audio_client.models.generate_content(
            model="gemini-3.1-flash-tts-preview",
            contents=directed_content,
            config=types.GenerateContentConfig(
                response_modalities=["AUDIO"],
                speech_config=types.SpeechConfig(
                    voice_config=types.VoiceConfig(
                        prebuilt_voice_config=types.PrebuiltVoiceConfig(voice_name="Zephyr")
                    )
                )
            )
        )

        audio_bytes = response.candidates[0].content.parts[0].inline_data.data

        tmp = tempfile.NamedTemporaryFile(suffix=".wav", delete=False)
        with wave.open(tmp.name, "wb") as wf:
            wf.setnchannels(1)
            wf.setsampwidth(2)
            wf.setframerate(24000)
            wf.writeframes(audio_bytes)

        with _temp_lock:
            for old_file in _temp_files[:]:
                try:
                    os.remove(old_file)
                    _temp_files.remove(old_file)
                except OSError:
                    pass  
            _temp_files.append(tmp.name)

        winsound.PlaySound(tmp.name, winsound.SND_FILENAME | winsound.SND_ASYNC)

    except Exception as e:
        print(f"\n[Audio Error: {e}]")

def play_async(text):
    """Fire-and-forget TTS execution wrapper."""
    threading.Thread(target=play_paimon_audio, args=(text,), daemon=True).start()

def start_adventure():
    preload_cache()  # Run phrase warmups asynchronously
    
    chat = chat_client.chats.create(
        model="gemini-2.5-flash",
        config=types.GenerateContentConfig(
            system_instruction=paimon_personality,
            temperature=0.85,
            max_output_tokens=200
        )
    )

    print("🧚 Paimon has floated into the chat! (Type 'exit' to leave)")

    arrival_text = "Oh! Hey Traveler! Paimon was getting super bored waiting around for you!"
    print(f"Paimon: {arrival_text}")
    play_async(arrival_text)

    while True:
        user_msg = input("\nYou: ")
        if user_msg.lower() == 'exit':
            farewell_text = "Aww, leaving already? Bring tasty snacks next time!"
            print(f"Paimon: {farewell_text}")
            play_async(farewell_text)
            time.sleep(10)
            break

        if not user_msg.strip():
            continue

        print("Paimon: ", end="", flush=True)

        buffer = ""
        first_chunk_spoken = False

        for chunk in chat.send_message_stream(user_msg):
            token = chunk.text or ""
            buffer += token
            print(token, end="", flush=True)

            # Check if current incoming character sequence hits structural split configurations
            if not first_chunk_spoken and any(p in buffer for p in SPLIT_ON):
                # Isolate the segment matching up to the first delimiter
                for i, char in enumerate(buffer):
                    if char in SPLIT_ON:
                        trigger_chunk = buffer[:i+1]
                        buffer = buffer[i+1:]  # Shift remaining data forward
                        play_async(trigger_chunk.strip())
                        first_chunk_spoken = True
                        break

        print()

        remainder = buffer.strip()
        if remainder:
            play_async(remainder)

if __name__ == "__main__":
    start_adventure()