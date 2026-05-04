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
        # We use a standard user agent and a 'compatibility' format
        'user_agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'referer': 'https://www.pinterest.com/',
        'format': 'bestvideo+bestaudio/best', # Force search for any media
    }
    
    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            # We use extract_info but catch specifically if the format is missing
            info = ydl.extract_info(url, download=False)
            video_url = info.get('url')
            
            if not video_url and 'formats' in info:
                # Look manually through available formats if the main one fails
                video_url = info['formats'][0]['url']

            return jsonify({
                "video_url": video_url,
                "title": info.get('title', 'Pinterest Video')
            })
    except Exception as e:
        return jsonify({"error": "Pinterest is blocking this request. Free servers like Vercel/PythonAnywhere are often flagged by their security."}), 500

if __name__ == "__main__":
    app.run()
