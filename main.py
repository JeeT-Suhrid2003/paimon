"""
Main entry point for Paimon Chat application.
Orchestrates initialization and starts the chat experience.
"""
import threading
from gui import init_gui, run_mainloop
from audio import initialize_audio, cleanup_audio_files
from chat import initialize_chat, create_chat_session, run_chat_loop


def main():
    """Initialize all systems and start Paimon chat experience."""
    
    # Initialize subsystems
    initialize_audio()
    initialize_chat()
    init_gui()
    
    # Create chat session
    chat_session = create_chat_session()
    
    # Run chat loop in separate thread
    chat_thread = threading.Thread(
        target=run_chat_loop,
        args=(chat_session,),
        daemon=False
    )
    chat_thread.start()
    
    # Keep main thread running Tkinter event loop
    run_mainloop()
    
    # Cleanup on exit
    cleanup_audio_files()


if __name__ == "__main__":
    # Make sure to run: pip install pillow google-genai
    main()
