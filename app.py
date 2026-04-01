from flask import Flask, render_template, request, redirect, url_for, send_file
import os
from datetime import datetime
from clip_pipeline import process_clip

app = Flask(__name__)
OUTPUT_DIR = "output"

# Sla verwerkte clips op
processed_clips = []

@app.route("/", methods=["GET", "POST"])
def index():
    global processed_clips
    message = ""
    if request.method == "POST":
        url = request.form.get("url")
        if url:
            try:
                output_file = process_clip(url)
                processed_clips.append(output_file)
                message = f"✅ Clip verwerkt en opgeslagen: {os.path.basename(output_file)}"
            except Exception as e:
                message = f"❌ Fout bij verwerken: {e}"
    return render_template("index.html", message=message, clips=processed_clips)

@app.route("/download/<filename>")
def download_clip(filename):
    path = os.path.join(OUTPUT_DIR, filename)
    return send_file(path, as_attachment=True)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)