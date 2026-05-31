"""
GUI management module for Paimon's display and mood expressions.
Handles Tkinter window, image updates, and thread-safe UI operations.
"""
import os
import tkinter as tk
from queue import Queue
from PIL import Image, ImageTk
from config import IMAGE_DIR, GUI_CONFIG

# Thread-safe queue for GUI updates from worker threads
_gui_queue = Queue()

# Global GUI elements
_root = None
_image_label = None
_current_photo = None  # Keep reference to prevent garbage collection


def init_gui():
    """Initialize the floating Paimon companion window."""
    global _root, _image_label
    
    _root = tk.Tk()
    _root.title(GUI_CONFIG["title"])
    _root.geometry(GUI_CONFIG["geometry"])
    _root.attributes("-topmost", GUI_CONFIG["topmost"])
    
    _image_label = tk.Label(_root)
    _image_label.pack(pady=10)
    
    # Load initial image
    update_image("happy")
    
    # Start processing queued updates
    _process_queue_updates()


def queue_image_update(mood):
    """
    Thread-safe method to queue an image update.
    Call this from worker threads.
    """
    _gui_queue.put(('image', mood))


def update_image(mood):
    """Public API to update image (queues the update safely)."""
    queue_image_update(mood)


def _process_queue_updates():
    """Process all queued GUI updates. Called periodically from main thread."""
    while True:
        try:
            msg_type, data = _gui_queue.get(block=False)
            if msg_type == 'image':
                _apply_image_update(data)
        except:
            break
    
    if _root:
        _root.after(GUI_CONFIG["update_interval"], _process_queue_updates)


def _apply_image_update(mood):
    """Apply image update (main thread only). Called via _process_queue_updates."""
    global _image_label, _current_photo
    
    if _root is None or _image_label is None:
        return
    
    # Validate image directory exists
    if not os.path.exists(IMAGE_DIR):
        print(f"[Warning] Image directory not found: {IMAGE_DIR}")
        return
    
    # Build image path with fallback
    mood_filename = f"{mood.lower().strip()}.png"
    image_path = os.path.join(IMAGE_DIR, mood_filename)
    
    if not os.path.exists(image_path):
        image_path = os.path.join(IMAGE_DIR, "happy.png")
    
    if not os.path.exists(image_path):
        print(f"[Warning] No images found in {IMAGE_DIR}")
        return
    
    try:
        img = Image.open(image_path)
        img = img.resize(GUI_CONFIG["image_size"], Image.Resampling.LANCZOS)
        _current_photo = ImageTk.PhotoImage(img)
        
        _image_label.config(image=_current_photo)
    except Exception as e:
        print(f"[Error loading image {image_path}]: {e}")


def get_root():
    """Get the root Tkinter window."""
    return _root


def run_mainloop():
    """Start the Tkinter event loop (call from main thread only)."""
    if _root:
        _root.mainloop()


def quit_app():
    """Safely quit the application."""
    if _root:
        _root.quit()
