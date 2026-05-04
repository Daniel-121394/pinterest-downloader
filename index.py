from flask import Flask, request, jsonify
from flask_cors import CORS  # Allows CodePen to connect
import yt_dlp
import os

app = Flask(__name__)
CORS(app)  # Activates the connection for outside websites

@app.route('/')
def home():
    return "Pinterest Downloader is Online!"

@app.route('/download')
def download():
    url = request.args.get('url')
    if not url:
        return jsonify({"error": "No URL provided"}), 400
    
    # Options to help bypass Pinterest security
    ydl_opts = {
        'format': 'best',
        'quiet': True,
        'user_agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    }
    
    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=False)
            return jsonify({
                "video_url": info.get('url'),
                "title": info.get('title', 'Pinterest Video')
            })
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 5000)))
