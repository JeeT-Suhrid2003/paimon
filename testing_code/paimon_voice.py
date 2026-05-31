from google import genai
from google.genai import types
import wave

client = genai.Client(enterprise=True, project="qwiklabs-gcp-02-559ed30b256b")

# Generate text and convert it to audio simultaneously
response = client.models.generate_content(
    model="gemini-3.1-flash-tts-preview",
    # You can literally use natural language to tell it HOW to speak!
    contents="Say enthusiastically and bubbly: Oh wow! Pipa is finally talking with real audio! Let's go find some snacks!",
    config=types.GenerateContentConfig(
        response_modalities=["AUDIO"],
        speech_config=types.SpeechConfig(
            voice_config=types.VoiceConfig(
                # Prebuilt voice profiles (e.g., 'Kore', 'Puck')
                prebuilt_voice_config=types.PrebuiltVoiceConfig(voice_name="Puck")
            )
        )
    )
)

# Extract the raw audio bytes from the response
audio_bytes = response.candidates[0].content.parts[0].inline_data.data

# Save it as a playable .wav file on your machine
with wave.open("pipa_voice1.wav", "wb") as wf:
    wf.setnchannels(1)
    wf.setsampwidth(2)
    wf.setframerate(24000)
    wf.writeframes(audio_bytes)

print("🧚 Pipa spoke! Check your directory for pipa_voice.wav")