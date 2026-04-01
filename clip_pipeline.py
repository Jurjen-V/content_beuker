import os
import subprocess
from datetime import datetime

TEMP_DIR = "temp"
OUTPUT_DIR = "output"
WHISPER = "/usr/local/bin/whisper-cli"
MODEL_PATH = os.path.expanduser("~/models/ggml-small.bin")  # ~ correct expanden

os.makedirs(TEMP_DIR, exist_ok=True)
os.makedirs(OUTPUT_DIR, exist_ok=True)

def process_clip(url):
    """Download clip, extract audio, generate subtitles, convert to vertical video."""
    timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
    clip_path = os.path.join(TEMP_DIR, f"clip_{timestamp}.mp4")
    audio_path = os.path.join(TEMP_DIR, f"audio_{timestamp}.wav")

    try:
        # Download clip
        subprocess.run(f'yt-dlp "{url}" -o "{clip_path}"', shell=True, check=True)

        # Extract audio
        subprocess.run(f'ffmpeg -y -i "{clip_path}" -ar 16000 -ac 1 -c:a pcm_s16le "{audio_path}"',
                       shell=True, check=True)

        # Whisper subtitles
        subprocess.run(f'{WHISPER} -m "{MODEL_PATH}" -f "{audio_path}" -l nl -osrt',
                       shell=True, check=True)

        srt_file = audio_path.replace(".wav", ".srt")

        # Vertical crop: automatisch gecentreerd
        output_file = os.path.join(OUTPUT_DIR, f"clip_{timestamp}.mp4")
        subprocess.run(f'''
        ffmpeg -y -i "{clip_path}" \
        -filter_complex "
        [0:v]crop=610:320:((in_w-610)/2):40,scale=1080:720[fc];
        [0:v]crop=1000:1000:(in_w-1000)/2:(in_h-1000)/2,scale=1080:1200[game];
        [fc][game]vstack=inputs=2[base];
        [base]subtitles={srt_file}:force_style='Fontsize=14,Outline=2,Shadow=1,Alignment=2,MarginV=120'[v]
        " -map "[v]" -map 0:a? -c:v libx264 -c:a aac -b:a 192k "{output_file}"
        ''', shell=True, check=True)

        return output_file

    finally:
        # Verwijder tijdelijke bestanden
        for f in [clip_path, audio_path, srt_file]:
            if os.path.exists(f):
                os.remove(f)