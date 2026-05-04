from flask import Flask, request, jsonify, Response
from flask_cors import CORS
import yt_dlp
import requests
import re
import os

app = Flask(__name__)
CORS(app)

def get_video_fallback(url):
    """If the main tool is blocked, this scans the page source for the raw .mp4 link."""
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36',
        'Accept-Language': 'en-US,en;q=0.9',
    }
    try:
        response = requests.get(url, headers=headers, timeout=10)
        # Search for the video URL pattern in Pinterest's internal JSON
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
        'no_warnings': True,
        'user_agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36',
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
        # If blocked, try the Stealth Scraper
        fallback = get_video_fallback(url)
        if fallback:
            return jsonify({"video_url": fallback, "title": "Video Found (Stealth)", "thumbnail": ""})
        return jsonify({"error": "Pinterest is heavily blocking this server IP right now."}), 500

@app.route('/proxy')
def proxy():
    video_url = request.args.get('url')
    r = requests.get(video_url, stream=True)
    headers = {
        'Content-Disposition': 'attachment; filename="video.mp4"',
        'Content-Type': 'video/mp4'
    }
    return Response(r.iter_content(chunk_size=1024*1024), headers=headers)

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 5000)))
