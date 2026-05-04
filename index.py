from flask import Flask, request, jsonify, Response
from flask_cors import CORS
import yt_dlp
import requests
import re
import os

app = Flask(__name__)
CORS(app)

def get_stealth_link(url):
    """Fallback: Scans the raw HTML for the video URL if yt-dlp is blocked."""
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36',
    }
    try:
        response = requests.get(url, headers=headers, timeout=10)
        # Search for the .mp4 link inside Pinterest's background data
        match = re.search(r'"url":"(https://v1\.pinimg\.com/videos/.*?\.mp4)"', response.text)
        if match:
            return match.group(1).replace('\\u002F', '/')
    except:
        return None
    return None

@app.route('/download')
def download():
    url = request.args.get('url')
    if not url: return jsonify({"error": "No URL"}), 400
    
    ydl_opts = {
        'quiet': True,
        'user_agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36',
        'format': 'bestvideo+bestaudio/best',
    }
    
    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=False)
            return jsonify({
                "video_url": info.get('url') or info['formats'][0]['url'],
                "title": info.get('title', 'Pinterest Video'),
                "thumbnail": info.get('thumbnail')
            })
    except:
        # If the main tool fails, use the Stealth Scraper
        fallback = get_stealth_link(url)
        if fallback:
            return jsonify({"video_url": fallback, "title": "Video Found", "thumbnail": ""})
        return jsonify({"error": "Pinterest is currently blocking the server. Please try again later."}), 500

@app.route('/proxy')
def proxy():
    # This route FORCES the download so you don't see the black player screen
    video_url = request.args.get('url')
    r = requests.get(video_url, stream=True)
    headers = {
        'Content-Disposition': 'attachment; filename="pin-video.mp4"',
        'Content-Type': 'video/mp4'
    }
    return Response(r.iter_content(chunk_size=1024*1024), headers=headers)

if __name__ == "__main__":
    app.run()
