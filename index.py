from flask import Flask, request, jsonify, Response
from flask_cors import CORS
import yt_dlp
import requests

app = Flask(__name__)
CORS(app)

@app.route('/download')
def download():
    url = request.args.get('url')
    
    # These headers make Vercel look like a real Chrome browser
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8',
        'Accept-Language': 'en-US,en;q=0.5',
        'Referer': 'https://www.pinterest.com/',
    }

    ydl_opts = {
        'quiet': True,
        'no_warnings': True,
        'user_agent': headers['User-Agent'],
        'headers': headers
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
        # If it still fails, it's a hard IP block from Pinterest
        return jsonify({"error": "Pinterest is blocking this server IP. Try a different link or redeploy to get a new IP."}), 500

@app.route('/proxy')
def proxy():
    video_url = request.args.get('url')
    # We use the same headers here to stream the video
    r = requests.get(video_url, headers={'User-Agent': 'Mozilla/5.0'}, stream=True)
    return Response(r.iter_content(chunk_size=1024*1024), content_type='video/mp4')
