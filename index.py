from flask import Flask, request, jsonify, Response
from flask_cors import CORS
import yt_dlp
import requests
import os

app = Flask(__name__)
CORS(app)

@app.route('/download')
def download():
    video_url = request.args.get('url')
    if not video_url:
        return jsonify({"error": "No URL provided"}), 400

    # Advanced 2026 Bypass logic
    ydl_opts = {
        'quiet': True,
        'no_warnings': True,
        'format': 'best',
        # This tells yt-dlp to use the cookies you just saved
        'cookiefile': 'cookies.txt', 
        # Using the iOS client is a "cheat code" to bypass many Vercel IP blocks
        'client_name': 'ios',
        'impersonate': 'chrome',
    }

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(video_url, download=False)
            
            # We prioritize a single file that contains both video and audio
            return jsonify({
                "video_url": info.get('url'),
                "title": info.get('title'),
                "thumbnail": info.get('thumbnail'),
                "duration": info.get('duration_string')
            })
    except Exception as e:
        # If this fails even with cookies, YouTube is challenging the IP
        return jsonify({"error": "YouTube is still blocking. Try redeploying Vercel for a new IP."}), 500

@app.route('/proxy')
def proxy():
    url = request.args.get('url')
    # Use your session headers to stream the file back to the user
    r = requests.get(url, headers={'User-Agent': 'Mozilla/5.0'}, stream=True)
    headers = {
        'Content-Disposition': 'attachment; filename="video.mp4"',
        'Content-Type': 'video/mp4'
    }
    return Response(r.iter_content(chunk_size=1024*1024), headers=headers)

def handler(event, context):
    return app(event, context)
