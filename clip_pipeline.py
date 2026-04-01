def process_clip(url):
    # Gebruik absolute paden, dit is veel veiliger voor FFmpeg's subtitle filter
    base_dir = os.path.abspath(os.path.dirname(__file__))
    clip_path = os.path.join(base_dir, TEMP_DIR, "clip.mp4")
    audio_path = os.path.join(base_dir, TEMP_DIR, "audio.wav")
    srt_file = os.path.join(base_dir, TEMP_DIR, "audio.srt")

    try:
        # 1. Download clip (met --force-overwrites zodat oude bestanden genegeerd worden)
        subprocess.run(f'yt-dlp --force-overwrites "{url}" -o "{clip_path}"', shell=True, check=True)

        # 2. Extract audio
        subprocess.run(
            f'ffmpeg -y -i "{clip_path}" -ar 16000 -ac 1 -c:a pcm_s16le "{audio_path}"',
            shell=True, check=True
        )

        # 3. Whisper transcript + SRT
        result = model.transcribe(audio_path, language="nl")
        segments_to_srt(result["segments"], srt_file)

        # 4. Convert to vertical video
        timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
        output_file = os.path.join(base_dir, OUTPUT_DIR, f"clip_{timestamp}.mp4")

        # Voor het subtitels filter in ffmpeg moeten paden goed geformatteerd zijn
        # We vervangen eventuele backslashes en escapen de dubbele punt voor de zekerheid
        srt_escaped = srt_file.replace('\\', '/').replace(':', '\\:')

        subprocess.run(f'''
        ffmpeg -y -i "{clip_path}" \
        -filter_complex "
        [0:v]crop=610:320:1480:40,scale=1080:720[fc];
        [0:v]crop=1000:1000:0:40,scale=1080:1200[game];
        [fc][game]vstack=inputs=2[base];
        [base]subtitles='{srt_escaped}':force_style='Fontsize=14,Outline=2,Shadow=1,Alignment=2,MarginV=120'[v]
        " -map "[v]" -map 0:a? -c:v libx264 -c:a aac -b:a 192k "{output_file}"
        ''', shell=True, check=True)

        return output_file

    finally:
        # Cleanup: Dit blok wordt ALTIJD uitgevoerd, zelfs als er een error optreedt in de try-sectie!
        for temp_file in [clip_path, audio_path, srt_file]:
            if os.path.exists(temp_file):
                os.remove(temp_file)
