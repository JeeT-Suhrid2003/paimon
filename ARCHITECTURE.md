# Paimon Chat - Modular Architecture

## Project Structure

The codebase is now organized into modular components for easy maintenance and extensibility:

### Core Modules

1. **main.py** - Entry point
   - Orchestrates initialization of all systems
   - Manages threading for GUI and chat
   - Run with: `python main.py`

2. **config.py** - Configuration & Constants
   - All settings, API keys, and constants
   - Character personality and messages
   - Easy to modify behavior without touching code

3. **gui.py** - User Interface
   - Tkinter window management
   - Mood-based image display
   - Thread-safe GUI update queue
   - No other module depends on this, so swap it easily

4. **audio.py** - Text-to-Speech & Playback
   - Gemini audio generation
   - Speech synthesis and playback
   - Temporary file management
   - Independent from other modules

5. **chat.py** - Conversation Logic
   - Chat session management
   - Message streaming and processing
   - Mood extraction from responses
   - Integrates other modules (gui, audio)

## Adding New Features

### Example: Add a new mood (CONFUSED)

1. Add image: `paimon_images/confused.png`
2. Update `config.py` to include new mood in personality if needed
3. That's it! The GUI will auto-detect and use it

### Example: Add logging

1. Create `logger.py`:
```python
import logging

def setup_logger():
    logging.basicConfig(level=logging.INFO)
    return logging.getLogger(__name__)
```

2. Import and use in other modules:
```python
from logger import setup_logger
log = setup_logger()
```

### Example: Add custom voice profiles

1. Extend `config.py` with new voice configs:
```python
VOICE_PROFILES = {
    "default": "Zephyr",
    "playful": "Nova",
    "serious": "Echo"
}
```

2. Modify `audio.py` to support voice parameter:
```python
def generate_and_play_speech(text_content, voice_profile="default"):
    voice_name = VOICE_PROFILES.get(voice_profile, VOICE_PROFILES["default"])
    # ... rest of code
```

### Example: Add Discord/Slack integration

1. Create `integrations/discord_bot.py`:
```python
from chat import create_chat_session, run_chat_loop
# Implement Discord bot logic
```

2. Create alternative `main_discord.py` for Discord mode

This keeps the core clean without affecting the main application.

## Dependency Graph

```
main.py
  ├── gui.py (no dependencies)
  ├── audio.py (no dependencies)
  ├── chat.py
  │   ├── gui.py
  │   ├── audio.py
  │   └── config.py
  ├── config.py
```

Notice: Each module has minimal dependencies, making it easy to:
- Test independently
- Swap implementations
- Reuse in other projects

## Running the App

```bash
python main.py
```

## Best Practices for Extending

1. **Keep modules focused** - Each file handles one concern
2. **Use config.py** - Put settings there, not hardcoded
3. **Minimize cross-module dependencies** - Easier to test and modify
4. **Keep main.py simple** - It's just orchestration
5. **Add docstrings** - Help future developers understand the module

## Quick Checklist for New Features

- [ ] Add any config to `config.py`
- [ ] Determine which module(s) it belongs in
- [ ] Write the feature in that module
- [ ] Update `main.py` if needed for initialization
- [ ] Test independently if possible
- [ ] Update this README with the new feature
