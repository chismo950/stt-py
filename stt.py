import queue, json
import sounddevice as sd
from vosk import Model, KaldiRecognizer
import curses
import os
import numpy as np
import sys
import select

show_visualization = False  # Set to False to hide audio level brackets

def select_device():
    devices = sd.query_devices()
    input_devices = [i for i, d in enumerate(devices) if d['max_input_channels'] > 0]
    
    if not input_devices:
        print("No input devices found!")
        sys.exit(1)
    
    options = [f"{i}: {devices[i]['name']}" for i in input_devices]
    current = 0
    
    def draw_menu(stdscr):
        nonlocal current
        curses.curs_set(0)
        stdscr.keypad(True)
        while True:
            stdscr.clear()
            stdscr.addstr(0, 0, "Select microphone device:")
            for idx, opt in enumerate(options):
                prefix = "▶" if idx == current else " "
                stdscr.addstr(idx+2, 0, f"{prefix} {opt}")
            key = stdscr.getch()
            if key == curses.KEY_UP:
                current = (current - 1) % len(options)
            elif key == curses.KEY_DOWN:
                current = (current + 1) % len(options)
            elif key in (curses.KEY_ENTER, 10, 13):
                return input_devices[current]
    return curses.wrapper(draw_menu)

def select_language():
    options = ["en-US", "en-IN"]
    current = 0
    def draw_menu(stdscr):
        nonlocal current
        curses.curs_set(0)
        stdscr.keypad(True)
        while True:
            stdscr.clear()
            for idx, opt in enumerate(options):
                prefix = "▶" if idx == current else " "
                stdscr.addstr(idx, 0, f"{prefix} {opt}")
            key = stdscr.getch()
            if key == curses.KEY_UP:
                current = (current - 1) % len(options)
            elif key == curses.KEY_DOWN:
                current = (current + 1) % len(options)
            elif key in (curses.KEY_ENTER, 10, 13):
                return options[current]
    return curses.wrapper(draw_menu)

def select_model_size():
    options = ["Small (Fast, less accurate)", "Large (Slower, more accurate)"]
    current = 0
    def draw_menu(stdscr):
        nonlocal current
        curses.curs_set(0)
        stdscr.keypad(True)
        while True:
            stdscr.clear()
            stdscr.addstr(0, 0, "Select model size:")
            for idx, opt in enumerate(options):
                prefix = "▶" if idx == current else " "
                stdscr.addstr(idx+2, 0, f"{prefix} {opt}")
            key = stdscr.getch()
            if key == curses.KEY_UP:
                current = (current - 1) % len(options)
            elif key == curses.KEY_DOWN:
                current = (current + 1) % len(options)
            elif key in (curses.KEY_ENTER, 10, 13):
                return current
    return curses.wrapper(draw_menu)

# Select input device
device = select_device()

# Prompt user for language selection via arrow keys
lang = select_language()

# Select model size
model_size = select_model_size()

# Set model directory based on selections
if lang == "en-US":
    if model_size == 0:  # Small
        model_dir = "model-en/vosk-model-small-en-us-0.15"
    else:  # Large
        model_dir = "model-en/vosk-model-en-us-0.22"
else:  # en-IN
    if model_size == 0:  # Small
        model_dir = "model-en/vosk-model-small-en-in-0.4"
    else:  # Large
        model_dir = "model-en/vosk-model-en-in-0.5"

# make path absolute and verify existence
model_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), model_dir))
if not os.path.isdir(model_dir):
    print(f"Model folder '{model_dir}' not found.")
    print("Please download the model from https://alphacephei.com/vosk/models")
    exit(1)

model = Model(model_dir)
rec = KaldiRecognizer(model, 16000)

# initialize queue for audio callback
q = queue.Queue()

# Audio gain control - can be adjusted at runtime
audio_gain = 1.5  # Default gain multiplier

def add_to_recent(text, max_recent=5):
    """Track recent final results to avoid duplicates"""
    if not hasattr(add_to_recent, "recent"):
        add_to_recent.recent = []
    if text in add_to_recent.recent:
        return False
    add_to_recent.recent.append(text)
    if len(add_to_recent.recent) > max_recent:
        add_to_recent.recent.pop(0)
    return True

def show_audio_level(level):
    """Show a simple visualization of audio level"""
    if not show_visualization:
        return ""
    bars = int(level * 50)
    return "[" + "█" * min(bars, 50) + " " * (50 - min(bars, 50)) + "]"

def callback(indata, frames, time, status):
    global audio_gain
    if status:
        print(status, file=sys.stderr)
    
    # Apply gain and normalization
    audio_data = np.frombuffer(bytes(indata), dtype=np.int16).copy()
    
    # Calculate current audio level (for visualization)
    max_level = np.max(np.abs(audio_data)) / 32768.0
    
    # Apply gain adjustment
    audio_data = audio_data * audio_gain
    
    # Clip to prevent overflow
    audio_data = np.clip(audio_data, -32768, 32767).astype(np.int16)
    
    q.put((bytes(audio_data), max_level))

print("Starting speech recognition with gain =", audio_gain)
print("Press + to increase gain, - to decrease gain, Ctrl+C to exit")

with sd.RawInputStream(samplerate=16000, blocksize=4000, dtype='int16',
                      channels=1, callback=callback, device=device):
    print("▶ Listening (Ctrl+C to stop)…")
    try:
        # Track the most recent partial result to avoid duplicates
        current_partial = ""
        
        while True:
            data, level = q.get()
            level_bar = show_audio_level(level)
            
            # Handle key presses for gain adjustment
            if sys.stdin in select.select([sys.stdin], [], [], 0)[0]:
                key = sys.stdin.read(1)
                if key == '+' and audio_gain < 5.0:
                    audio_gain += 0.1
                    print(f"\rGain adjusted to: {audio_gain:.1f}")
                elif key == '-' and audio_gain > 0.1:
                    audio_gain -= 0.1
                    print(f"\rGain adjusted to: {audio_gain:.1f}")
            
            if rec.AcceptWaveform(data):
                result = json.loads(rec.Result())
                text = result["text"]
                
                # Only show final results if they're not empty and not a duplicate
                if text and add_to_recent(text):
                    print(f"\n{level_bar}{text}")
                    current_partial = ""  # Reset the current partial after a final result
            else:
                partial = json.loads(rec.PartialResult())["partial"]
                # Only show meaningful partial results that are different from what we're showing
                if partial and len(partial) > 3 and partial != current_partial:
                    print(f"\r{level_bar}…{partial}", end="", flush=True)
                    current_partial = partial
    except KeyboardInterrupt:
        print("\nStopped")