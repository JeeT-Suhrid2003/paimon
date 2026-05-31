# Paimon Chat

A modular Paimon companion application using Gemini AI, Tkinter GUI, and TTS audio playback.

## Project Structure

- `main.py` - App entry point and orchestration
- `config.py` - Configuration, constants, and personality settings
- `gui.py` - Tkinter window and mood image display
- `audio.py` - Text-to-speech generation and audio playback
- `chat.py` - Conversation loop, streaming responses, and mood handling
- `paimon_images/` - Mood image assets used by the GUI
- `ARCHITECTURE.md` - Developer guide for extending the app

## Requirements

- Python 3.10+
- `pillow`
- `google-genai`

Install dependencies with:

```bash
pip install pillow google-genai
```

## Setup

1. Place your mood images inside `paimon_images/`.
2. Required image names:
   - `happy.png`
   - `thinking.png`
   - `sad.png`
   - `angry.png`
3. Verify your `PROJECT_ID` in `config.py`.

## Run

```bash
python main.py
```

## Usage

- Type messages into the console.
- Paimon will respond with text, voice, and mood images.
- Type `exit` to end the chat.

## Notes

- The GUI runs on the main thread and receives updates from the chat thread safely.
- The application uses a modular design so new features can be added in separate files.
- For architecture details, see `ARCHITECTURE.md`.
