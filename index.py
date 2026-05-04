from flask import Flask, request, jsonify, Response
from flask_cors import CORS
import yt_dlp
import requests
import re

app = Flask(__name__)
CORS(app)

def get_fallback_link(url):
    """If yt-dlp fails, this tries to find the video URL in the page source."""
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'}
    try:
        response = requests.get(url, headers=headers, timeout=10)
        # Search for common video patterns in Pinterest's JSON data
        match = re.search(r'"url":"(https://v1\.pinimg\.com/videos/.*?\.mp4)"', response.text)
        if match:
            return match.group(1).replace('\\u002F', '/')
    except:
        return None
    return None

@app.route('/download')
def download():
    url = request.args.get('url')
    if not url:
        return jsonify({"error": "No URL provided"}), 400
    
    # Try the standard method first
    ydl_opts = {
        'quiet': True,
        'no_warnings': True,
        'user_agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    }
    
    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=False)
            return jsonify({
                "video_url": info.get('url'),
                "title": info.get('title', 'Pinterest Video'),
                "thumbnail": info.get('thumbnail')
            })
    except:
        # If standard method fails, use the fallback
        video_url = get_fallback_link(url)
        if video_url:
            return jsonify({
                "video_url": video_url,
                "title": "Pinterest Video (Fallback)",
                "thumbnail": ""
            })
        return jsonify({"error": "Pinterest security is currently blocking this server IP."}), 500

@app.route('/proxy')
def proxy():
    video_url = request.args.get('url')
    r = requests.get(video_url, stream=True)
    headers = {
        'Content-Disposition': 'attachment; filename="video.mp4"',
        'Content-Type': 'video/mp4'
    }
    return Response(r.iter_content(chunk_size=1024), headers=headers)
