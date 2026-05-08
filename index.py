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
SERP_API_KEY = "c86a424289bd817fab44befd9549e62bfaf1cd09bde4d925610ef50d688f5fa4"

def get_site_name(url):
    """Extracts 'wikipedia.org' from a long URL"""
    try:
        domain = urlparse(url).netloc
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

            # 1. DuckDuckGo
            try:
                res = list(ddgs.text(f'"{sentence}"', max_results=1))
                if res: found_url = res[0]['href']
            except: pass

            # 2. Serper
            if not found_url and SERPER_KEY:
                try:
                    res = requests.post("https://google.serper.dev/search", 
                                        json={"q": f'"{sentence}"'}, 
                                        headers={'X-API-KEY': SERPER_KEY}).json()
                    if res.get('organic'): found_url = res['organic'][0]['link']
                except: pass

            # 3. Tavily
            if not found_url and TAVILY_KEY:
                try:
                    res = requests.post("https://api.tavily.com/search", 
                                        json={"api_key": TAVILY_KEY, "query": f'"{sentence}"'}).json()
                    if res.get('results'): found_url = res['results'][0]['url']
                except: pass

            analysis.append({
                "sentence": sentence,
                "plagiarized": True if found_url else False,
                "url": found_url,
                "sitename": get_site_name(found_url) if found_url else None
            })

    return jsonify({"analysis": analysis})

def handler(event, context):
    return app(event, context)
