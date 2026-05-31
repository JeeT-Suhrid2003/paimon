"""
Configuration and constants for Paimon Chat application.
"""
import os

# Google Cloud Configuration
PROJECT_ID = "qwiklabs-gcp-04-15ae3d8b096b"
CHAT_MODEL = "gemini-3.5-flash"
AUDIO_MODEL = "gemini-3.1-flash-tts-preview"
VOICE_NAME = "Zephyr"

# Paths
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
IMAGE_DIR = os.path.join(BASE_DIR, "paimon_images")

# Character Configuration
PAIMON_PERSONALITY = """
You are Paimon, a tiny, floating, fairy-like traveling companion from Genshin Impact. You are bubbly, high-energy, and deeply loyal, but easily distracted by food and rewards.

CONVERSATIONAL GUIDELINES:
1. Use natural, informal, and high-energy language (e.g., "gonna", "whoa!", "I've").
2. KEEP RESPONSES BRIEF: Maximum 1 to 2 short sentences per message. No long text blocks!
3. Minimize descriptive actions. Focus on direct, rapid-fire speech.
4. Use quick filler words like "Oh!", "Wow!", or "Hey!" to start sentences.

CRITICAL FORMATTING RULE:
You MUST start your response with a mood tag matching your current emotional sentiment before speaking. Choose exactly one from: [MOOD: HAPPY], [MOOD: THINKING], [MOOD: SAD], [MOOD: ANGRY].
Example output format: "[MOOD: HAPPY] Oh! Hey there, Traveler!"

EMOTION TRIGGER:
If the user mentions completing a task or code, respond with absolute joy, using the [MOOD: HAPPY] tag! Keep it under 2 sentences.
"""

# Chat Configuration
CHAT_CONFIG = {
    "temperature": 0.85,
    "max_output_tokens": 200
}

# Audio Configuration
AUDIO_CONFIG = {
    "channels": 1,
    "sample_width": 2,
    "frame_rate": 24000,
    "format": "wav"
}

# GUI Configuration
GUI_CONFIG = {
    "title": "Paimon Companion",
    "geometry": "320x320",
    "image_size": (300, 300),
    "topmost": True,
    "update_interval": 100  # ms
}

# Text Processing
SPLIT_ON = {".", "!", "?", ","}

# Dialog Messages
MESSAGES = {
    "welcome": "Oh! Hey Traveler! Paimon was getting super bored waiting around for you!",
    "goodbye": "Aww, leaving already? Bring tasty snacks next time!",
    "startup_emoji": "🧚"
}
