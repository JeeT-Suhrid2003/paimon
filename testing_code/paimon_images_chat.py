import io
import os
import wave
import winsound
import threading
import tempfile
import tkinter as tk
from queue import Queue
from PIL import Image, ImageTk
from google import genai
from google.genai import types
import time
PROJECT_ID = "qwiklabs-gcp-04-15ae3d8b096b"

# Updated System Instructions: We explicitly force Gemini to append a structural mood indicator tag
paimon_personality = """
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

chat_client = genai.Client(enterprise=True, project=PROJECT_ID, location="us-central1")
audio_client = genai.Client(enterprise=True, project=PROJECT_ID)

# Global variables for tracking temp assets and UI elements
_temp_files = []
_temp_lock = threading.Lock()
_gui_queue = Queue()  # Thread-safe queue for GUI updates
SPLIT_ON = {".", "!", "?", ","}

# GUI Control Elements
root = None
image_label = None
IMAGE_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "paimon_images")

def update_ui_image(mood):
    """Queue an image update to be processed safely on the main thread."""
    _gui_queue.put(('image', mood))

def _process_gui_updates():
    """Process queued GUI updates from worker threads. Called periodically by the main thread."""
    while True:
        try:
            msg_type, data = _gui_queue.get(block=False)
            if msg_type == 'image':
                _update_ui_image_unsafe(data)
        except:
            break
    
    if root:
        root.after(100, _process_gui_updates)

def _update_ui_image_unsafe(mood):
    """Actually updates the image. Only called from the main thread via _process_gui_updates."""
    global image_label
    if root is None or image_label is None:
        return
    
    # Ensure IMAGE_DIR exists
    if not os.path.exists(IMAGE_DIR):
        print(f"[Warning] Image directory not found: {IMAGE_DIR}")
        return
        
    mood_filename = f"{mood.lower().strip()}.png"
    image_path = os.path.join(IMAGE_DIR, mood_filename)
    
    # Fallback to happy if a specific expression asset is missing
    if not os.path.exists(image_path):
        image_path = os.path.join(IMAGE_DIR, "happy.png")
        
    if not os.path.exists(image_path):
        print(f"[Warning] No image found in {IMAGE_DIR}")
        return
        
    try:
        # Open, format, and push the asset to the Tkinter canvas wrapper
        img = Image.open(image_path)
        img = img.resize((300, 300), Image.Resampling.LANCZOS)
        photo = ImageTk.PhotoImage(img)
        
        image_label.config(image=photo)
        image_label.image = photo  # Keep reference alive
    except Exception as e:
        print(f"[Error loading image {image_path}]: {e}")

def play_paimon_audio(text_content):
    """Generates speech text and updates audio tracks asynchronously."""
    try:
        clean_text = text_content.strip()
        if not clean_text:
            return

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
    threading.Thread(target=play_paimon_audio, args=(text,), daemon=True).start()

def setup_gui():
    """Initializes a permanent, lightweight floating window to host Paimon's expressions."""
    global root, image_label
    root = tk.Tk()
    root.title("Paimon Companion")
    root.geometry("320x320")
    root.attributes("-topmost", True)  # Keeps her pinned on top of your coding terminal
    
    image_label = tk.Label(root)
    image_label.pack(pady=10)
    
    # Initialize with default resting asset
    _update_ui_image_unsafe("happy")
    
    # Start processing queued GUI updates
    _process_gui_updates()

def _chat_thread():
    """Runs the chat loop in a separate thread while the main thread handles Tkinter."""
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
    update_ui_image("happy")
    play_async(arrival_text)

    while True:
        user_msg = input("\nYou: ")
        if user_msg.lower() == 'exit':
            farewell_text = "Aww, leaving already? Bring tasty snacks next time!"
            print(f"Paimon: {farewell_text}")
            update_ui_image("sad")
            play_paimon_audio(farewell_text)
            time.sleep(8) # Synchronous call to finish line before exiting
            root.quit()
            break

        if not user_msg.strip():
            continue

        print("Paimon: ", end="", flush=True)
        update_ui_image("thinking") # Set placeholder visual state during raw text processing

        buffer = ""
        first_chunk_spoken = False
        detected_mood = "happy"

        for chunk in chat.send_message_stream(user_msg):
            token = chunk.text or ""
            buffer += token
            
            # Intercept and strip out the metadata mood tag to keep the terminal text output clean
            if "[MOOD:" in buffer and "]" in buffer:
                start_idx = buffer.find("[MOOD:")
                end_idx = buffer.find("]")
                mood_tag = buffer[start_idx:end_idx+1]
                detected_mood = mood_tag.replace("[MOOD:", "").replace("]", "").strip().lower()
                
                # Instantly shift the desktop image window to reflect her internal emotion state
                update_ui_image(detected_mood)
                buffer = buffer.replace(mood_tag, "")
                token = token.replace(mood_tag, "")
                
            print(token, end="", flush=True)

            if not first_chunk_spoken and any(p in buffer for p in SPLIT_ON):
                for i, char in enumerate(buffer):
                    if char in SPLIT_ON:
                        trigger_chunk = buffer[:i+1]
                        buffer = buffer[i+1:]
                        play_async(trigger_chunk.strip())
                        first_chunk_spoken = True
                        break

        print()

        remainder = buffer.strip()
        if remainder:
            play_async(remainder)

def start_adventure():
    # Setup visual layout canvas first
    setup_gui()
    
    # Run chat in a separate thread
    chat_thread = threading.Thread(target=_chat_thread, daemon=False)
    chat_thread.start()
    
    # Keep the main thread running the Tkinter loop
    root.mainloop()

if __name__ == "__main__":
    # Make sure you run 'pip install pillow' and 'pip install google-genai'
    start_adventure()