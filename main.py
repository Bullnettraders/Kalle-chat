from fastapi import FastAPI
from pydantic import BaseModel
import requests
from bs4 import BeautifulSoup
import json
import os

app = FastAPI()
KNOWLEDGE_FILE = "knowledge.json"

class LearnRequest(BaseModel):
    question: str

def load_knowledge():
    if os.path.exists(KNOWLEDGE_FILE):
        with open(KNOWLEDGE_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return {}

def save_knowledge(data):
    with open(KNOWLEDGE_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

def search_web(query):
    search_url = f"https://www.investopedia.com/search?q={query.replace(' ', '+')}"
    response = requests.get(search_url, timeout=10)
    soup = BeautifulSoup(response.text, "html.parser")
    first_result = soup.select_one("a.search-list__link")
    if first_result:
        href = first_result.get("href")
        article = requests.get(href, timeout=10)
        article_soup = BeautifulSoup(article.text, "html.parser")
        paragraphs = article_soup.select("article p")
        content = "\n\n".join(p.get_text() for p in paragraphs[:3])
        return content.strip()
    return "Kein Artikel gefunden."

@app.post("/learn")
async def learn_topic(data: LearnRequest):
    question = data.question.strip().lower()
    knowledge = load_knowledge()

    if question in knowledge:
        return {"status": "already_known", "answer": knowledge[question]}

    answer = search_web(question)
    knowledge[question] = answer
    save_knowledge(knowledge)

    return {"status": "learned", "answer": answer}

@app.get("/lookup")
async def lookup(question: str):
    knowledge = load_knowledge()
    result = knowledge.get(question.strip().lower(), None)
    return {"found": result is not None, "answer": result}
