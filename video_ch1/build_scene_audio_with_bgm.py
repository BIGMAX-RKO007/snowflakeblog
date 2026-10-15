import os
import json
import soundfile as sf
import numpy as np

AUDIO_DIR = r"C:\Users\FX\Projects\SnowflakeBlog\video_ch1\audio"
MANIFEST_PATH = os.path.join(AUDIO_DIR, "manifest.json")

with open(MANIFEST_PATH, "r", encoding="utf-8") as f:
    manifest = json.load(f)

sr = 48000

# Base chord frequencies for ambient synth (Mitsui Fintech theme)
chords = [
    [146.83, 174.61, 220.00, 261.63], # Dm7
    [130.81, 164.81, 196.00, 246.94], # Cmaj7
    [116.54, 146.83, 174.61, 220.00], # Bbmaj7
    [130.81, 164.81, 196.00, 261.63]  # C
]

for act_id in ["act1", "act2", "act3", "act4", "act5", "act6", "act7"]:
    info = manifest[act_id]
    wav_path = os.path.join(AUDIO_DIR, f"{act_id}.wav")
    total_sec = info["duration"] # allocated slot duration
    raw_sec = info["raw_duration"]
    
    print(f"Processing {act_id} (slot duration: {total_sec}s, raw voice: {raw_sec}s)...")
    voice_data, file_sr = sf.read(wav_path)
    if voice_data.ndim == 1:
        voice_data = np.column_stack((voice_data, voice_data))
        
    total_samples = int(total_sec * sr)
    final_voice = np.zeros((total_samples, 2), dtype=np.float32)
    
    # Normalize voice to 0.88 peak
    v_peak = np.max(np.abs(voice_data))
    if v_peak > 0:
        voice_normalized = voice_data / v_peak * 0.88
    else:
        voice_normalized = voice_data
        
    voice_len = min(len(voice_normalized), total_samples)
    final_voice[:voice_len] = voice_normalized[:voice_len]
    
    # 2. Synthesize ambient tech background music matching total_sec
    t = np.linspace(0, total_sec, total_samples, endpoint=False)
    bgm_left = np.zeros(total_samples, dtype=np.float32)
    bgm_right = np.zeros(total_samples, dtype=np.float32)
    
    chord_len_sec = 6.0
    num_chords = int(np.ceil(total_sec / chord_len_sec))
    for i in range(num_chords):
        c_freqs = chords[i % len(chords)]
        s_idx = int(i * chord_len_sec * sr)
        e_idx = min(total_samples, int((i + 1) * chord_len_sec * sr))
        if s_idx >= total_samples:
            break
        c_samples = e_idx - s_idx
        ct = np.linspace(0, c_samples / sr, c_samples, endpoint=False)
        
        env = np.ones(c_samples, dtype=np.float32)
        fade_len = int(min(c_samples / 4, 1.0 * sr))
        if fade_len > 0:
            env[:fade_len] = np.linspace(0, 1, fade_len)
            env[-fade_len:] = np.linspace(1, 0, fade_len)
            
        c_wave = np.zeros(c_samples, dtype=np.float32)
        for freq in c_freqs:
            c_wave += 0.035 * np.sin(2 * np.pi * freq * ct)
            c_wave += 0.015 * np.sin(2 * np.pi * (freq * 2.005) * ct) # subtle detune
            
        bgm_left[s_idx:e_idx] += c_wave * env * 0.95
        bgm_right[s_idx:e_idx] += c_wave * env * 1.05
        
    # Gentle tech pulse
    pulse = (np.sin(2 * np.pi * 3.0 * t) ** 16) * 0.012 * np.sin(2 * np.pi * 880 * t)
    bgm_left += pulse.astype(np.float32)
    bgm_right += pulse.astype(np.float32)
    
    # 3. Sidechain ducking: duck BGM when voice is active
    hop = 4800 # 100ms
    num_chunks = int(np.ceil(total_samples / hop))
    v_peaks = np.zeros(num_chunks, dtype=np.float32)
    for i in range(num_chunks):
        s = i * hop
        e = min(s + hop, total_samples)
        v_peaks[i] = np.max(np.abs(final_voice[s:e]))
        
    duck_coarse = 1.0 - np.clip(v_peaks * 2.8, 0.0, 0.70)
    duck_smooth = np.interp(np.arange(total_samples), np.arange(num_chunks) * hop, duck_coarse).astype(np.float32)
    
    bgm_stereo = np.column_stack((bgm_left * duck_smooth, bgm_right * duck_smooth))
    
    # 4. Master mix
    mix = final_voice + bgm_stereo
    
    # Fade in & out
    fade_in = int(0.5 * sr)
    fade_out = int(1.2 * sr)
    mix[:fade_in] *= np.linspace(0, 1, fade_in)[:, np.newaxis]
    mix[-fade_out:] *= np.linspace(1, 0, fade_out)[:, np.newaxis]
    
    m_peak = np.max(np.abs(mix))
    if m_peak > 0.95:
        mix = mix / m_peak * 0.95
        
    # Save as 16-bit PCM for fast streaming & decoding
    sf.write(wav_path, mix, sr, subtype='PCM_16')
    file_size_mb = os.path.getsize(wav_path) / (1024 * 1024)
    print(f"  -> Generated {act_id}.wav ({total_sec}s, {file_size_mb:.2f}MB, 16-bit PCM, peak: {np.max(np.abs(mix)):.2f})")

print("\nAll 7 Act audio soundtracks built with BGM, normalization, and sidechain ducking!")
