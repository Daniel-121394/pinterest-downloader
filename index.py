from flask import Flask, request, jsonify
from flask_cors import CORS
import yt_dlp

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
        # This tells the server to act like a real Chrome browser
        'impersonate': 'chrome', 
        'header': [
            'Accept: text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8',
            'Accept-Language: en-US,en;q=0.5',
        ],
    }
    
    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=False)
            video_url = info.get('url') or info['formats'][0]['url']

            return jsonify({
                "video_url": video_url,
                "title": info.get('title', 'Pinterest Video'),
                "thumbnail": info.get('thumbnail', '')
            })
    except Exception as e:
        # Detailed error for debugging
        return jsonify({"error": "Pinterest is still blocking. Try a different link or wait 5 mins."}), 500

if __name__ == "__main__":
    app.run()
