import queue, json
import sounddevice as sd
from vosk import Model, KaldiRecognizer

import os
print("Looking in:", os.path.abspath("model-en"))
print("Contents:", os.listdir("model-en"))

q = queue.Queue()
model = Model("model-en/vosk-model-small-en-us-0.15")           # path to the unzipped model folder
rec = KaldiRecognizer(model, 16000) # 16 kHz sample rate

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