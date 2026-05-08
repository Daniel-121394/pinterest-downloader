from flask import Flask, request, jsonify
from flask_cors import CORS
from duckduckgo_search import DDGS
import requests
import re
from urllib.parse import urlparse

app = Flask(__name__)
CORS(app)

# --- YOUR 3 API KEYS ---
SERPER_KEY = "b3a0b26a1540f36fa12be26d049867fadf5c3161"
TAVILY_KEY = "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"
SERP_API_KEY = "c86a424289bd817fab44befd9549e62bfaf1cd09bde4d925610ef50d688f5fa4"

def get_site_name(url):
    """Extracts the clean site name from a URL"""
    try:
        domain = urlparse(url).netloc.lower()
        return domain.replace('www.', '')
    except:
        return "Unknown Site"

@app.route('/')
def home():
    return "US Digital Guiders - Triple API Checker is ACTIVE"

@app.route('/check', methods=['POST'])
def check_plagiarism():
    data = request.get_json()
    full_text = data.get('text', '')
    if not full_text:
        return jsonify({"error": "No text"}), 400

    # Split text into sentences
    sentences = re.split(r'(?<=[.!?]) +', full_text)
    analysis = []

    with DDGS() as ddgs:
        for sentence in sentences[:15]: # Checking top 15 lines
            sentence = sentence.strip()
            if len(sentence.split()) < 5: continue

            found_url = None
            site_name = None

            # 1. Try DuckDuckGo
            try:
                res = list(ddgs.text(f'"{sentence}"', max_results=1))
                if res: 
                    found_url = res[0]['href']
                    site_name = get_site_name(found_url)
            except: pass

            # 2. Try Serper (Google)
            if not found_url and SERPER_KEY:
                try:
                    res = requests.post("https://google.serper.dev/search", 
                                        json={"q": f'"{sentence}"'}, 
                                        headers={'X-API-KEY': SERPER_KEY}).json()
                    if res.get('organic'): 
                        found_url = res['organic'][0]['link']
                        site_name = get_site_name(found_url)
                except: pass

            # 3. Try Tavily
            if not found_url and TAVILY_KEY:
                try:
                    res = requests.post("https://api.tavily.com/search", 
                                        json={"api_key": TAVILY_KEY, "query": f'"{sentence}"'}).json()
                    if res.get('results'): 
                        found_url = res['results'][0]['url']
                        site_name = get_site_name(found_url)
                except: pass
            
            # 4. Try SerpApi (Third API)
            if not found_url and SERP_API_KEY:
                try:
                    params = {"q": f'"{sentence}"', "api_key": SERP_API_KEY}
                    res = requests.get("https://serpapi.com/search", params=params).json()
                    if res.get('organic_results'):
                        found_url = res['organic_results'][0]['link']
                        site_name = get_site_name(found_url)
                except: pass

            analysis.append({
                "sentence": sentence,
                "plagiarized": True if found_url else False,
                "url": found_url,
                "site": site_name
            })

    return jsonify({"analysis": analysis})

def handler(event, context):
    return app(event, context)
