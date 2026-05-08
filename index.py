from flask import Flask, request, jsonify
from flask_cors import CORS
from duckduckgo_search import DDGS
import requests
import re

app = Flask(__name__)
CORS(app)

# YOUR 3 API KEYS
SERPER_KEY = "b3a0b26a1540f36fa12be26d049867fadf5c3161"
TAVILY_KEY = "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"
SERP_API_KEY = "c86a424289bd817fab44befd9549e62bfaf1cd09bde4d925610ef50d688f5fa4"

@app.route('/check', methods=['POST'])
def check_plagiarism():
    data = request.get_json()
    full_text = data.get('text', '')
    
    # Split into sentences (Precision Check)
    sentences = re.split(r'(?<=[.!?]) +', full_text)
    analysis = []

    with DDGS() as ddgs:
        for sentence in sentences[:15]:
            sentence = sentence.strip()
            # Ignore short phrases that are naturally common
            if len(sentence.split()) < 6:
                analysis.append({"sentence": sentence, "plagiarized": False})
                continue

            is_plagiarized = False
            # Wrap in double quotes for EXACT matching
            query = f'"{sentence}"'

            # 1. Check DuckDuckGo (Free)
            try:
                if list(ddgs.text(query, max_results=1)): is_plagiarized = True
            except: pass

            # 2. Check Serper (Google)
            if not is_plagiarized and SERPER_KEY:
                try:
                    res = requests.post("https://google.serper.dev/search", 
                                        json={"q": query}, 
                                        headers={'X-API-KEY': SERPER_KEY}, timeout=1).json()
                    if res.get('organic'): is_plagiarized = True
                except: pass

            # 3. Check Tavily (AI Search)
            if not is_plagiarized and TAVILY_KEY:
                try:
                    res = requests.post("https://api.tavily.com/search", 
                                        json={"api_key": TAVILY_KEY, "query": query}).json()
                    if res.get('results'): is_plagiarized = True
                except: pass

            analysis.append({
                "sentence": sentence,
                "plagiarized": is_plagiarized
            })

    return jsonify({"analysis": analysis})
