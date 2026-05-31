# Example payload for voice cloning synthesis
import base64

# Base64 encode your reference audio
with open("reference_voice.flac", "rb") as audio_file:
    encoded_audio = base64.b64encode(audio_file.read()).decode("utf-8")

payload = {
    "text": "how is ur day going.",
    "language": "en-us",
    "reference_audio": encoded_audio,
    "reference_language": "en-us"
}

# Send to endpoint
response = endpoint.raw_predict(body=json.dumps(payload).encode("utf-8"))