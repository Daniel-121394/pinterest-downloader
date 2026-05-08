from flask import Flask, request, jsonify
from flask_cors import CORS
from duckduckgo_search import DDGS
import requests
import re

app = Flask(__name__)
CORS(app)

# --- YOUR API KEYS ---
SERPER_KEY = "b3a0b26a1540f36fa12be26d049867fadf5c3161"
TAVILY_KEY = "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"
SERP_API_KEY = "c86a424289bd817fab44befd9549e62bfaf1cd09bde4d925610ef50d688f5fa4"

@app.route('/')
def home():
    return "US Digital Guiders - Multi-API Line Checker is ACTIVE"

@app.route('/check', methods=['POST'])
def check_plagiarism():
    data = request.get_json()
    full_text = data.get('text', '')
    
    if not full_text:
        return jsonify({"error": "No text provided"}), 400

    # Step 1: Split text into sentences for line-by-line checking
    sentences = re.split(r'(?<=[.!?]) +', full_text)
    analysis = []

    with DDGS() as ddgs:
        # Check top 15 sentences to prevent timeouts on Vercel
        for sentence in sentences[:15]:
            sentence = sentence.strip()
            if len(sentence.split()) < 5:
                analysis.append({"sentence": sentence, "plagiarized": False, "url": None, "source": "Unique"})
                continue

            match_found = False
            found_url = None
            api_name = ""

            # 1. Search with DuckDuckGo (Free)
            try:
                ddg_res = list(ddgs.text(f'"{sentence}"', max_results=1))
                if ddg_res:
                    match_found, found_url, api_name = True, ddg_res[0]['href'], "DuckDuckGo"
            except: pass

            # 2. Search with Serper (Google Backup)
            if not match_found and SERPER_KEY:
                try:
                    res = requests.post("https://google.serper.dev/search", 
                                        json={"q": f'"{sentence}"'}, 
                                        headers={'X-API-KEY': SERPER_KEY}, timeout=2).json()
                    if res.get('organic'):
                        match_found, found_url, api_name = True, res['organic'][0]['link'], "Serper"
                except: pass

            # 3. Search with Tavily (AI Search Backup)
            if not match_found and TAVILY_KEY:
                try:
                    res = requests.post("https://api.tavily.com/search", 
                                        json={"api_key": TAVILY_KEY, "query": f'"{sentence}"'}).json()
                    if res.get('results'):
                        match_found, found_url, api_name = True, res['results'][0]['url'], "Tavily"
                except: pass

            # 4. Search with SerpApi (Final Resort)
            if not match_found and SERP_API_KEY:
                try:
                    params = {"q": f'"{sentence}"', "api_key": SERP_API_KEY}
                    res = requests.get("https://serpapi.com/search", params=params).json()
                    if res.get('organic_results'):
                        match_found, found_url, api_name = True, res['organic_results'][0]['link'], "SerpApi"
                except: pass

            analysis.append({
                "sentence": sentence,
                "plagiarized": match_found,
                "url": found_url,
                "api": api_name
            })

    return jsonify({"analysis": analysis})

def handler(event, context):
    return app(event, context)
