from flask import Flask, request, jsonify
from flask_cors import CORS
import yt_dlp
import os

app = Flask(__name__)
CORS(app)

@app.route('/download')
def download():
    url = request.args.get('url')
    if not url:
        return jsonify({"error": "No URL provided"}), 400
    
    ydl_opts = {
        'quiet': True,
        'no_warnings': True,
        'format': 'best', # Get the most compatible single file
        'user_agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36',
    }
    
    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=False)
            video_url = info.get('url')
            
            if not video_url and 'formats' in info:
                video_url = info['formats'][0]['url']

            return jsonify({
                "video_url": video_url,
                "title": info.get('title', 'Pinterest Video'),
                "thumbnail": info.get('thumbnail', '')
            })
    except Exception as e:
        return jsonify({"error": "Pinterest blocked the fetch. Try a different link."}), 500

if __name__ == "__main__":
    app.run()
