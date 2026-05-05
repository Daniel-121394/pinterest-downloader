from flask import Flask, request, jsonify, Response
from flask_cors import CORS
import yt_dlp
import os
import requests

app = Flask(__name__)
CORS(app)

@app.route('/')
def home():
    return "YouTube Downloader API is Online"

@app.route('/download')
def download():
    video_url = request.args.get('url')
    if not video_url:
        return jsonify({"error": "No URL"}), 400

    cookie_path = os.path.join(os.path.dirname(__file__), 'cookies.txt')

    # 2026 High-Security Options
    ydl_opts = {
        'quiet': True,
        'no_warnings': True,
        'format': 'best',
        'cookiefile': cookie_path,
        # Rotate between different clients to find one not blocked
        'client_name': 'web', 
        'client_version': '2.20240101.01.00',
        'impersonate': 'chrome',
        'nocheckcertificate': True,
        'http_headers': {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': '*/*',
            'Accept-Language': 'en-US,en;q=0.9',
        }
    }

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(video_url, download=False)
            return jsonify({
                "video_url": info.get('url'),
                "title": info.get('title'),
                "thumbnail": info.get('thumbnail')
            })
    except Exception as e:
        # Fallback to Android client if Web is blocked
        try:
            ydl_opts['client_name'] = 'android'
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(video_url, download=False)
                return jsonify({
                    "video_url": info.get('url'),
                    "title": info.get('title'),
                    "thumbnail": info.get('thumbnail')
                })
        except:
            return jsonify({"error": "YouTube Security is extremely tight. Wait 5 minutes."}), 500

@app.route('/proxy')
def proxy():
    url = request.args.get('url')
    r = requests.get(url, stream=True)
    return Response(r.iter_content(chunk_size=1024*1024), content_type='video/mp4')

def handler(event, context):
    return app(event, context)
