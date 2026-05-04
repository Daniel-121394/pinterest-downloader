from flask import Flask, request, jsonify
from flask_cors import CORS
import yt_dlp
import os

app = Flask(__name__)
CORS(app)

@app.route('/')
def home():
    return "Pinterest Downloader is Online!"

@app.route('/download')
def download():
    url = request.args.get('url')
    if not url:
        return jsonify({"error": "No URL provided"}), 400
    
    ydl_opts = {
        'quiet': True,
        'no_warnings': True,
        # This helps when the specific Pinterest extractor fails
        'force_generic_extractor': True, 
        'user_agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36',
        'referer': 'https://www.pinterest.com/',
    }
    
    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=False)
            
            # Check multiple locations where the video URL might be hidden
            video_url = info.get('url') or (info.get('entries') and info.get('entries')[0].get('url'))
            
            if not video_url:
                return jsonify({"error": "Could not extract video link. Pinterest might be blocking this specific pin."}), 404

            return jsonify({
                "video_url": video_url,
                "title": info.get('title', 'Pinterest Video')
            })
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 5000)))
