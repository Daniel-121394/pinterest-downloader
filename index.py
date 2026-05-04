from flask import Flask, request, jsonify, Response
from flask_cors import CORS
import yt_dlp
import requests
import os

app = Flask(__name__)
CORS(app)

@app.route('/')
def home():
    return "Pinterest Downloader API is Active"

@app.route('/download')
def download():
    url = request.args.get('url')
    if not url:
        return jsonify({"error": "No URL provided"}), 400
    
    ydl_opts = {
        'quiet': True,
        'no_warnings': True,
        'user_agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'referer': 'https://www.pinterest.com/',
    }
    
    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=False)
            return jsonify({
                "video_url": info.get('url'),
                "title": info.get('title', 'Pinterest Video'),
                "thumbnail": info.get('thumbnail')
            })
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# THE KEY FIX: This route forces the download
@app.route('/proxy')
def proxy():
    video_url = request.args.get('url')
    if not video_url:
        return "No URL", 400
    
    # Stream the video from Pinterest through your server
    r = requests.get(video_url, stream=True)
    
    # Set headers to force "Save As" dialog
    headers = {
        'Content-Disposition': 'attachment; filename="pinterest_video.mp4"',
        'Content-Type': 'video/mp4'
    }
    
    return Response(r.iter_content(chunk_size=1024*1024), headers=headers)

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 5000)))
