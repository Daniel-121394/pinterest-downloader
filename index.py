from flask import Flask, request, jsonify, Response
from flask_cors import CORS
import yt_dlp
import requests

app = Flask(__name__)
CORS(app)

@app.route('/download')
def download():
    video_url = request.args.get('url')
    if not video_url:
        return jsonify({"error": "Missing URL"}), 400

    # 2026 Best Practices for YouTube: Chrome Impersonation
    ydl_opts = {
        'quiet': True,
        'no_warnings': True,
        'format': 'bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best',
        'impersonate': 'chrome', # Requires curl-cffi in requirements.txt
    }

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(video_url, download=False)
            
            # YouTube often separates Video and Audio. 
            # This selects the best direct link available.
            return jsonify({
                "video_url": info.get('url'),
                "title": info.get('title'),
                "thumbnail": info.get('thumbnail'),
                "duration": info.get('duration_string')
            })
    except Exception as e:
        # Check Vercel logs if you see this error
        return jsonify({"error": f"YouTube blocked the request: {str(e)}"}), 500

@app.route('/proxy')
def proxy():
    url = request.args.get('url')
    # Use a generic User-Agent to stream the file
    r = requests.get(url, headers={'User-Agent': 'Mozilla/5.0'}, stream=True)
    return Response(r.iter_content(chunk_size=1024*1024), content_type='video/mp4')

def handler(event, context):
    return app(event, context)
