import io
import os
import wave
import winsound
import threading
import tempfile
from google import genai
from google.genai import types

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

def play_paimon_audio(text_content):
    """Generates audio, writes to temp file, plays async from disk."""
    try:
        response = audio_client.models.generate_content(
            model="gemini-3.1-flash-tts-preview",
            contents=text_content,
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

        # Write to a named temp file (delete=False so winsound can read it)
        tmp = tempfile.NamedTemporaryFile(suffix=".wav", delete=False)
        with wave.open(tmp.name, "wb") as wf:
            wf.setnchannels(1)
            wf.setsampwidth(2)
            wf.setframerate(24000)
            wf.writeframes(audio_bytes)

        # Clean up old temp files before playing new one
        with _temp_lock:
            for old_file in _temp_files[:]:
                try:
                    os.remove(old_file)
                    _temp_files.remove(old_file)
                except OSError:
                    pass  # Still playing, skip
            _temp_files.append(tmp.name)

        # SND_ASYNC + SND_FILENAME works reliably on all Windows versions
        winsound.PlaySound(tmp.name, winsound.SND_FILENAME | winsound.SND_ASYNC)

    except Exception as e:
        print(f"\n[Audio Error: {e}]")


def play_async(text):
    """Fire-and-forget TTS in background thread."""
    threading.Thread(target=play_paimon_audio, args=(text,), daemon=True).start()


def start_adventure():
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

            if not first_chunk_spoken and any(p in buffer for p in [".", "!", "?"]):
                play_async(buffer.strip())
                first_chunk_spoken = True
                buffer = ""

        print()

        remainder = buffer.strip()
        if remainder:
            play_async(remainder)


if __name__ == "__main__":
    start_adventure()