"""
Chat module for Paimon conversation and response generation.
Handles chat initialization, message streaming, and mood extraction.
"""
import time
from google import genai
from google.genai import types
from config import (
    PROJECT_ID, CHAT_MODEL, PAIMON_PERSONALITY, CHAT_CONFIG, SPLIT_ON, MESSAGES
)
from gui import update_image, quit_app
from audio import play_speech_async, generate_and_play_speech

# Chat client
_chat_client = genai.Client(enterprise=True, project=PROJECT_ID, location="us-central1")


def initialize_chat():
    """Initialize the chat system. Call once at startup."""
    pass  # Chat client is initialized globally


def create_chat_session():
    """Create a new chat session with Paimon."""
    return _chat_client.chats.create(
        model=CHAT_MODEL,
        config=types.GenerateContentConfig(
            system_instruction=PAIMON_PERSONALITY,
            temperature=CHAT_CONFIG["temperature"],
            max_output_tokens=CHAT_CONFIG["max_output_tokens"]
        )
    )


def run_chat_loop(chat_session):
    """
    Main chat loop. Run in a separate thread.
    Handles user input and Paimon responses.
    """
    print(f"{MESSAGES['startup_emoji']} Paimon has floated into the chat! (Type 'exit' to leave)")
    
    # Welcome message
    arrival_text = MESSAGES["welcome"]
    print(f"Paimon: {arrival_text}")
    update_image("happy")
    play_speech_async(arrival_text)
    
    while True:
        user_msg = input("\nYou: ")
        
        if user_msg.lower() == 'exit':
            _handle_exit(chat_session)
            break
        
        if not user_msg.strip():
            continue
        
        _process_paimon_response(chat_session, user_msg)


def _handle_exit(chat_session):
    """Handle exit command gracefully."""
    farewell_text = MESSAGES["goodbye"]
    print(f"Paimon: {farewell_text}")
    update_image("sad")
    generate_and_play_speech(farewell_text)  # Blocking call to finish before exit
    time.sleep(8)  # Wait for audio to finish
    quit_app()


def _process_paimon_response(chat_session, user_msg):
    """Process and display Paimon's response to user message."""
    print("Paimon: ", end="", flush=True)
    update_image("thinking")
    
    buffer = ""
    first_chunk_spoken = False
    detected_mood = "happy"
    
    # Stream response
    for chunk in chat_session.send_message_stream(user_msg):
        token = chunk.text or ""
        buffer += token
        
        # Extract mood tag
        if "[MOOD:" in buffer and "]" in buffer:
            mood_tag = _extract_mood_tag(buffer)
            if mood_tag:
                detected_mood = mood_tag
                update_image(detected_mood)
                buffer = _remove_mood_tag(buffer)
                token = _remove_mood_tag(token)
        
        # Print response
        print(token, end="", flush=True)
        
        # Play first sentence
        if not first_chunk_spoken and any(p in buffer for p in SPLIT_ON):
            trigger_chunk = _extract_first_sentence(buffer)
            if trigger_chunk:
                buffer = buffer[len(trigger_chunk):]
                play_speech_async(trigger_chunk.strip())
                first_chunk_spoken = True
    
    print()
    
    # Play remaining text
    remainder = buffer.strip()
    if remainder:
        play_speech_async(remainder)


def _extract_mood_tag(text):
    """Extract mood tag from text. Returns mood string or None."""
    start_idx = text.find("[MOOD:")
    end_idx = text.find("]", start_idx)
    
    if start_idx != -1 and end_idx != -1:
        mood_tag = text[start_idx:end_idx+1]
        mood = mood_tag.replace("[MOOD:", "").replace("]", "").strip().lower()
        return mood
    
    return None


def _remove_mood_tag(text):
    """Remove mood tag from text."""
    start_idx = text.find("[MOOD:")
    end_idx = text.find("]", start_idx)
    
    if start_idx != -1 and end_idx != -1:
        return text[:start_idx] + text[end_idx+1:]
    
    return text


def _extract_first_sentence(text):
    """Extract first sentence from buffer."""
    for i, char in enumerate(text):
        if char in SPLIT_ON:
            return text[:i+1]
    
    return None
