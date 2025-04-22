import queue, json
import sounddevice as sd
from vosk import Model, KaldiRecognizer
import curses
import os

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

# Prompt user for language selection via arrow keys
lang = select_language()
if lang == "en-US":
    model_dir = "model-en/vosk-model-small-en-us-0.15"
else:  # en-IN
    model_dir = "model-en/vosk-model-small-en-in-0.4"

# make path absolute and verify existence
model_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), model_dir))
if not os.path.isdir(model_dir):
    print(f"Model folder '{model_dir}' not found.")
    exit(1)

model = Model(model_dir)           # path to the unzipped model folder
rec = KaldiRecognizer(model, 16000) # 16 kHz sample rate
# initialize queue for audio callback
q = queue.Queue()

def callback(indata, frames, time, status):
    q.put(bytes(indata))

with sd.RawInputStream(samplerate=16000, blocksize=8000, dtype='int16',
                      channels=1, callback=callback):
    print("▶ Listening (Ctrl+C to stop)…")
    while True:
        data = q.get()
        if rec.AcceptWaveform(data):
            text = json.loads(rec.Result())["text"]
            if text:
                print(text)
        else:
            # optional: show partial hypothesis in‑place
            partial = json.loads(rec.PartialResult())["partial"]
            print(f"\r…{partial}", end="", flush=True)