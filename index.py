from flask import Flask, request, jsonify, Response
from flask_cors import CORS
import yt_dlp
import requests
import os

app = Flask(__name__)
CORS(app)

@app.route('/download')
def download():
    url = request.args.get('url')
    ydl_opts = {
        'quiet': True,
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
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/proxy')
def proxy():
    # This route takes the video link and FORCES the browser to download it
    video_url = request.args.get('url')
    r = requests.get(video_url, stream=True)
    headers = {
        'Content-Disposition': 'attachment; filename="pin-video.mp4"',
        'Content-Type': 'video/mp4'
    }
    return Response(r.iter_content(chunk_size=1024*1024), headers=headers)

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 5000)))
