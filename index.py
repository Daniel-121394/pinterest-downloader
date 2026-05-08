from flask import Flask, request, jsonify
from flask_cors import CORS
from duckduckgo_search import DDGS
import requests
import re

app = Flask(__name__)
CORS(app)

# YOUR API KEYS
SERPER_KEY = "b3a0b26a1540f36fa12be26d049867fadf5c3161"
TAVILY_KEY = "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"

@app.route('/')
def home():
    return "US Digital Guiders - Triple API Checker is ACTIVE"

@app.route('/check', methods=['POST'])
def check_plagiarism():
    data = request.get_json()
    full_text = data.get('text', '')
    if not full_text:
        return jsonify({"error": "No text"}), 400

    # Split into sentences
    sentences = re.split(r'(?<=[.!?]) +', full_text)
    analysis = []

    with DDGS() as ddgs:
        for sentence in sentences[:15]:
            sentence = sentence.strip()
            if len(sentence.split()) < 5:
                analysis.append({"sentence": sentence, "plagiarized": False, "url": None})
                continue

            found_url = None
            
            # Try DuckDuckGo first
            try:
                ddg_res = list(ddgs.text(f'"{sentence}"', max_results=1))
                if ddg_res: found_url = ddg_res[0]['href']
            except: pass

            # Try Serper if DDG fails
            if not found_url and SERPER_KEY:
                try:
                    res = requests.post("https://google.serper.dev/search", 
                                        json={"q": f'"{sentence}"'}, 
                                        headers={'X-API-KEY': SERPER_KEY}).json()
                    if res.get('organic'): found_url = res['organic'][0]['link']
                except: pass

            # Try Tavily if others fail
            if not found_url and TAVILY_KEY:
                try:
                    res = requests.post("https://api.tavily.com/search", 
                                        json={"api_key": TAVILY_KEY, "query": f'"{sentence}"'}).json()
                    if res.get('results'): found_url = res['results'][0]['url']
                except: pass

            analysis.append({
                "sentence": sentence, 
                "plagiarized": True if found_url else False, 
                "url": found_url
            })

    return jsonify({"analysis": analysis})

def handler(event, context):
    return app(event, context)
