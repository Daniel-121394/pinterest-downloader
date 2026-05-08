from flask import Flask, request, jsonify
from flask_cors import CORS
from duckduckgo_search import DDGS
import requests
import re
from urllib.parse import urlparse

app = Flask(__name__)
CORS(app)

# API KEYS
SERPER_KEY = "b3a0b26a1540f36fa12be26d049867fadf5c3161"
TAVILY_KEY = "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"

# ADD SITES YOU WANT TO IGNORE HERE
SKIP_SITES = ["indeed.com", "reddit.com", "wikipedia.org", "facebook.com"]

def get_site_name(url):
    try:
        domain = urlparse(url).netloc.lower()
        return domain.replace('www.', '')
    except:
        return "Unknown Site"

@app.route('/check', methods=['POST'])
def check_plagiarism():
    data = request.get_json()
    full_text = data.get('text', '')
    if not full_text:
        return jsonify({"error": "No text"}), 400

    sentences = re.split(r'(?<=[.!?]) +', full_text)
    analysis = []

    with DDGS() as ddgs:
        for sentence in sentences[:15]:
            sentence = sentence.strip()
            if len(sentence.split()) < 5: continue

            found_url = None
            site_name = None

            # Logic: Try DuckDuckGo first, then Serper, then Tavily
            # But SKIP results from the sites in SKIP_SITES
            try:
                res = list(ddgs.text(f'"{sentence}"', max_results=5))
                for r in res:
                    s_name = get_site_name(r['href'])
                    if not any(skip in s_name for skip in SKIP_SITES):
                        found_url = r['href']
                        site_name = s_name
                        break
            except: pass

            if not found_url and SERPER_KEY:
                try:
                    res = requests.post("https://google.serper.dev/search", 
                                        json={"q": f'"{sentence}"'}, 
                                        headers={'X-API-KEY': SERPER_KEY}).json()
                    for r in res.get('organic', []):
                        s_name = get_site_name(r['link'])
                        if not any(skip in s_name for skip in SKIP_SITES):
                            found_url = r['link']
                            site_name = s_name
                            break
                except: pass

            analysis.append({
                "sentence": sentence,
                "plagiarized": True if found_url else False,
                "url": found_url,
                "sitename": site_name
            })

    return jsonify({"analysis": analysis})

def handler(event, context):
    return app(event, context)
