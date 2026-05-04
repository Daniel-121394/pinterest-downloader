from flask import Flask, request, jsonify, Response
from flask_cors import CORS
import yt_dlp
import requests

app = Flask(__name__)
CORS(app)

@app.route('/')
def home():
    return "Server is Running"

@app.route('/download')
def download():
    url = request.args.get('url')
    if not url:
        return jsonify({"error": "No URL"}), 400
    
    ydl_opts = {
        'quiet': True,
        'no_warnings': True,
        'format': 'best',
    }
    
    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=False)
            return jsonify({
                "video_url": info.get('url'),
                "title": info.get('title'),
                "thumbnail": info.get('thumbnail')
            })
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/proxy')
def proxy():
    video_url = request.args.get('url')
    r = requests.get(video_url, stream=True)
    return Response(r.iter_content(chunk_size=1024), content_type='video/mp4')

# This is critical for Vercel
def handler(event, context):
    return app(event, context)
