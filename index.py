from flask import Flask, request, jsonify
from flask_cors import CORS
from duckduckgo_search import DDGS
import requests
import re

app = Flask(__name__)
CORS(app)

# API KEYS
SERPER_KEY = "b3a0b26a1540f36fa12be26d049867fadf5c3161"
TAVILY_KEY = "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"

@app.route('/check', methods=['POST'])
def check_plagiarism():
    data = request.get_json()
    full_text = data.get('text', '')
    
    # Split into sentences for line-by-line checking
    sentences = re.split(r'(?<=[.!?]) +', full_text)
    analysis = []

    with DDGS() as ddgs:
        for sentence in sentences[:15]:
            sentence = sentence.strip()
            # Skip very short lines that trigger false positives
            if len(sentence.split()) < 5:
                analysis.append({"sentence": sentence, "plagiarized": False})
                continue

            is_plagiarized = False
            # CRITICAL: Wrap the sentence in double quotes for an exact search
            exact_query = f'"{sentence}"'

            # 1. Try DuckDuckGo
            try:
                if list(ddgs.text(exact_query, max_results=1)):
                    is_plagiarized = True
            except: pass

            # 2. Try Serper (Google) if DDG finds nothing
            if not is_plagiarized and SERPER_KEY:
                try:
                    res = requests.post("https://google.serper.dev/search", 
                                        json={"q": exact_query}, 
                                        headers={'X-API-KEY': SERPER_KEY}).json()
                    if res.get('organic'): is_plagiarized = True
                except: pass

            # 3. Try Tavily
            if not is_plagiarized and TAVILY_KEY:
                try:
                    res = requests.post("https://api.tavily.com/search", 
                                        json={"api_key": TAVILY_KEY, "query": exact_query}).json()
                    if res.get('results'): is_plagiarized = True
                except: pass

            analysis.append({
                "sentence": sentence,
                "plagiarized": is_plagiarized
            })

    return jsonify({"analysis": analysis})
