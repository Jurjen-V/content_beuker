import os
import subprocess
from datetime import datetime
import whisper

TEMP_DIR = "temp"
OUTPUT_DIR = "output"
os.makedirs(TEMP_DIR, exist_ok=True)
os.makedirs(OUTPUT_DIR, exist_ok=True)

# Laad Whisper model één keer
model = whisper.load_model("small")  # ggml-small equivalent

def process_clip(url):
    clip_path = os.path.join(TEMP_DIR, "clip.mp4")
    audio_path = os.path.join(TEMP_DIR, "audio.wav")
    
    # Download clip
    subprocess.run(f'yt-dlp "{url}" -o "{clip_path}"', shell=True, check=True)
    
    # Extract audio
    subprocess.run(f'ffmpeg -y -i "{clip_path}" -ar 16000 -ac 1 -c:a pcm_s16le "{audio_path}"',
                   shell=True, check=True)
    
    # Whisper transcript + SRT
    result = model.transcribe(audio_path, language="nl")
    srt_file = audio_path.replace(".wav", ".srt")
    with open(srt_file, "w", encoding="utf-8") as f:
        f.write(result["srt"])
    
    # Convert to vertical
    timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
    output_file = os.path.join(OUTPUT_DIR, f"clip_{timestamp}.mp4")
    
    subprocess.run(f'''
    ffmpeg -y -i "{clip_path}" \
    -filter_complex "
    [0:v]crop=610:320:1480:40,scale=1080:720[fc];
    [0:v]crop=1000:1000:0:40,scale=1080:1200[game];
    [fc][game]vstack=inputs=2[base];
    [base]subtitles={srt_file}:force_style='Fontsize=14,Outline=2,Shadow=1,Alignment=2,MarginV=120'[v]
    " -map "[v]" -map 0:a? -c:v libx264 -c:a aac -b:a 192k "{output_file}"
    ''', shell=True, check=True)
    
    # Cleanup
    os.remove(clip_path)
    os.remove(audio_path)
    os.remove(srt_file)
    
    return output_file
