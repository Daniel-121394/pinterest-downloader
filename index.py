from flask import Flask, request, jsonify
from flask_cors import CORS
from duckduckgo_search import DDGS
import requests
from tavily import TavilyClient
from serpapi import GoogleSearch

app = Flask(__name__)
CORS(app)

# --- YOUR KEYS (Hardcoded for convenience) ---
SERPER_KEY = "b3a0b26a1540f36fa12be26d049867fadf5c3161"
TAVILY_KEY = "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"
SERP_API_KEY = "c86a424289bd817fab44befd9549e62bfaf1cd09bde4d925610ef50d688f5fa4"

@app.route('/')
def home():
    return "US Digital Guiders - Plagiarism Super-Checker is ACTIVE"

@app.route('/check', methods=['POST'])
def check_plagiarism():
    data = request.get_json()
    text = data.get('text', '')
    
    if not text:
        return jsonify({"error": "No text provided"}), 400

    results = []

    # --- STEP 1: DUCKDUCKGO (100% FREE) ---
    try:
        with DDGS() as ddgs:
            # Quotes around {text} forces an exact phrase match
            ddg_matches = list(ddgs.text(f'"{text}"', max_results=2))
            for r in ddg_matches:
                results.append({"source": "DuckDuckGo", "url": r['href'], "title": r['title']})
    except Exception as e:
        print(f"DDG Error: {e}")

    # --- STEP 2: SERPER.DEV (BACKUP 1) ---
    if not results and SERPER_KEY:
        try:
            headers = {'X-API-KEY': SERPER_KEY, 'Content-Type': 'application/json'}
            res = requests.post("https://google.serper.dev/search", 
                                json={"q": f'"{text}"'}, headers=headers, timeout=5).json()
            for r in res.get('organic', [])[:2]:
                results.append({"source": "Google (Serper)", "url": r['link'], "title": r['title']})
        except:
            pass

    # --- STEP 3: TAVILY AI (BACKUP 2) ---
    if not results and TAVILY_KEY:
        try:
            tavily = TavilyClient(api_key=TAVILY_KEY)
            t_res = tavily.search(query=text, search_depth="basic")
            for r in t_res.get('results', [])[:2]:
                results.append({"source": "Tavily AI", "url": r['url'], "title": r['title']})
        except:
            pass

    # --- STEP 4: SERPAPI (FINAL BACKUP) ---
    if not results and SERP_API_KEY:
        try:
            search = GoogleSearch({"q": f'"{text}"', "api_key": SERP_API_KEY})
            serp_res = search.get_dict()
            for r in serp_res.get('organic_results', [])[:2]:
                results.append({"source": "Google (SerpApi)", "url": r['link'], "title": r['title']})
        except:
            pass

    return jsonify({
        "is_unique": len(results) == 0,
        "matches": results,
        "total_matches": len(results),
        "status": "Plagiarized" if results else "Original"
    })

# Required for Vercel
def handler(event, context):
    return app(event, context)
