import os
import json
import soundfile as sf
import numpy as np

MANIFEST_PATH = r"C:\Users\FX\Projects\SnowflakeBlog\video_ch1_ja\audio\manifest.json"
OUTPUT_WAV = r"C:\Users\FX\Projects\SnowflakeBlog\video_ch1_ja\audio\full_soundtrack.wav"

with open(MANIFEST_PATH, "r", encoding="utf-8") as f:
    manifest = json.load(f)

total_sec = manifest["total_duration"]
sr = 48000
total_samples = int(total_sec * sr)
master_audio = np.zeros((total_samples, 2), dtype=np.float32)

print(f"Creating JA master soundtrack ({total_sec}s / {round(total_sec/60, 2)} min)...")

# 1. Overlay voice clips at their exact start times
for act_id in ["act1", "act2", "act3", "act4", "act5", "act6", "act7"]:
    info = manifest[act_id]
    wav_path = info["wav"]
    start_sec = info["start_time"]
    start_idx = int(start_sec * sr)
    
    data, file_sr = sf.read(wav_path)
    if data.ndim == 1:
        data = np.column_stack((data, data))
        
    end_idx = min(start_idx + len(data), total_samples)
    master_audio[start_idx:end_idx] += data[:end_idx-start_idx] * 0.95
    print(f"  Placed {act_id} at {start_sec}s (length: {len(data)/sr:.2f}s)")

# 2. Fast ambient synth background
t = np.linspace(0, total_sec, total_samples, endpoint=False)
pad = (
    0.025 * np.sin(2 * np.pi * 146.83 * t) +   # D3
    0.020 * np.sin(2 * np.pi * 174.61 * t) +   # F3
    0.020 * np.sin(2 * np.pi * 220.00 * t) +   # A3
    0.015 * np.sin(2 * np.pi * 261.63 * t) +   # C4
    0.015 * np.sin(2 * np.pi * 73.42 * t)      # D2 sub-bass
)
lfo = 0.6 + 0.4 * np.sin(2 * np.pi * (1.0 / 8.0) * t)
bgm = pad * lfo
bgm_stereo = np.column_stack((bgm * 0.9, bgm * 1.0)).astype(np.float32)

# 3. Super-fast envelope ducking via 100ms chunking + linear interp
hop = 4800 # 100ms
num_chunks = int(np.ceil(total_samples / hop))
voice_peaks = np.zeros(num_chunks, dtype=np.float32)
for i in range(num_chunks):
    s = i * hop
    e = min(s + hop, total_samples)
    voice_peaks[i] = np.max(np.abs(master_audio[s:e]))

duck_coarse = 1.0 - np.clip(voice_peaks * 3.0, 0.0, 0.65)
duck_interp = np.interp(np.arange(total_samples), np.arange(num_chunks) * hop, duck_coarse).astype(np.float32)

bgm_ducked = bgm_stereo * duck_interp[:, np.newaxis]
final_mix = master_audio + bgm_ducked

max_peak = np.max(np.abs(final_mix))
if max_peak > 0.95:
    final_mix = final_mix / max_peak * 0.95

sf.write(OUTPUT_WAV, final_mix, sr)
print(f"Master soundtrack generated successfully ({os.path.getsize(OUTPUT_WAV)} bytes)!")
