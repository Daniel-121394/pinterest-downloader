from flask import Flask, request, jsonify, Response
from flask_cors import CORS
import yt_dlp
import requests
import os

app = Flask(__name__)
CORS(app)

@app.route('/')
def home():
    return "YouTube Downloader API is Online"

@app.route('/download')
def download():
    video_url = request.args.get('url')
    if not video_url:
        return jsonify({"error": "No URL provided"}), 400

    # Path to the cookies file you uploaded to GitHub
    cookie_path = os.path.join(os.path.dirname(__file__), 'cookies.txt')

    # Advanced 2026 Bypass Strategy
    ydl_opts = {
        'quiet': True,
        'no_warnings': True,
        'format': 'best',
        'cookiefile': cookie_path, # Loads your Netscape cookies
        'client_name': 'ios',      # Spoofing iOS often bypasses Vercel IP bans
        'impersonate': 'chrome',   # Requires curl-cffi in requirements.txt
    }

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            # This fetches the video data using your cookies
            info = ydl.extract_info(video_url, download=False)
            
            return jsonify({
                "video_url": info.get('url'),
                "title": info.get('title'),
                "thumbnail": info.get('thumbnail'),
                "duration": info.get('duration_string')
            })
    except Exception as e:
        # If this fails, check Vercel logs to see if cookies expired
        return jsonify({"error": f"Security Block: {str(e)}"}), 500

@app.route('/proxy')
def proxy():
    url = request.args.get('url')
    if not url: return "Missing URL", 400
    
    # Streams the file through your server to bypass "Black Screen" player issues
    r = requests.get(url, headers={'User-Agent': 'Mozilla/5.0'}, stream=True)
    headers = {
        'Content-Disposition': 'attachment; filename="video.mp4"',
        'Content-Type': 'video/mp4'
    }
    return Response(r.iter_content(chunk_size=1024*1024), headers=headers)

# Vercel handler
def handler(event, context):
    return app(event, context)

if __name__ == "__main__":
    app.run()
