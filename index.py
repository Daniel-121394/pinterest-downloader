from flask import Flask, request, jsonify, Response
from flask_cors import CORS
import yt_dlp
import requests
import os

app = Flask(__name__)
CORS(app)

# Use a session to maintain a consistent 'human' connection profile
session = requests.Session()
session.headers.update({
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8',
    'Accept-Language': 'en-US,en;q=0.5',
    'DNT': '1',
})

@app.route('/download')
def download():
    url = request.args.get('url')
    if not url:
        return jsonify({"error": "No URL provided"}), 400
    
    ydl_opts = {
        'quiet': True,
        'no_warnings': True,
        'user_agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36',
        'referer': 'https://www.pinterest.com/',
    }
    
    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=False)
            return jsonify({
                "video_url": info.get('url'),
                "title": info.get('title', 'Pinterest Video'),
                "thumbnail": info.get('thumbnail', '')
            })
    except Exception:
        return jsonify({"error": "Pinterest is currently blocking the server's IP. Please try again in 5 minutes."}), 500

@app.route('/proxy')
def proxy():
    video_url = request.args.get('url')
    if not video_url: return "Missing URL", 400
    
    # This streams the video through the server to bypass browser blocks
    r = session.get(video_url, stream=True)
    headers = {
        'Content-Disposition': 'attachment; filename="video.mp4"',
        'Content-Type': 'video/mp4'
    }
    return Response(r.iter_content(chunk_size=1024*1024), headers=headers)

if __name__ == "__main__":
    app.run()
