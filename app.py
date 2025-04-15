import os
import json
import io
import stripe
import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd
from flask import Flask, render_template, request, jsonify
from openai import OpenAI
from dotenv import load_dotenv
from googleapiclient.discovery import build

load_dotenv()
app = Flask(__name__)

openai_client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
stripe.api_key = os.getenv("STRIPE_SECRET_KEY")
youtube = build("youtube", "v3", developerKey=os.getenv("YOUTUBE_API_KEY"))

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/analyze")
def analyze():
    clusters = {
        "다양한 장르의 이슈": ["genre:국제", "genre:정치", "genre:정치", "genre:사회", "genre:사회"],
        "Korean Classics": ["korean", "korean clssic", "korean", "korean clssic", "korean"],
        "한국 고전영화": ["한국영화", "영화", "고전영화", "돌팔매질", "뿡밥"],
        "유명 인물들": ["person:곽상은", "person:윤석열", "person:윤갑근", "person:윤석열", "person:지귀연"],
        "HIT 3 Hindi Movie": ["HIT 3 Hindi Trailer", "HIT 3 Trailer Hindi", "Nani HIT 3 Hindi", "HIT 3 Nani Hindi Trailer", "HIT 3 Sailesh Kolanu Hindi"]
    }
    return render_template("analysis.html", clusters=clusters)

@app.route("/graph")
def graph():
    tag_counts = pd.Series({
        "국제": 50,
        "정치": 45,
        "사회": 40,
        "한국영화": 35,
        "곽상은": 30
    })

    sns.set(font="NanumGothic", rc={"axes.unicode_minus": False})
    plt.figure(figsize=(8, 5))
    sns.barplot(x=tag_counts.values, y=tag_counts.index, palette="viridis")
    plt.title("대표 클러스터 해시태그 그래프")
    plt.tight_layout()
    buf = io.BytesIO()
    plt.savefig(buf, format="png")
    buf.seek(0)
    return app.response_class(buf, mimetype="image/png")

@app.route("/chat")
def chat():
    return render_template("chat.html")

@app.route("/get-recommendation", methods=["POST"])
def get_recommendation():
    data = request.get_json()
    user_input = data["message"]

    hashtags = ["정치", "사회", "국제", "곽상은", "윤석열", "HIT 3"]
    context = f"현재 인기 해시태그는 다음과 같아: {', '.join(hashtags)}. 이 데이터를 참고해서 {user_input}에 맞는 유튜브 영상 주제를 추천해줘."

    response = openai_client.chat.completions.create(
        model="gpt-4",
        messages=[{"role": "user", "content": context}],
    )

    reply = response.choices[0].message.content.strip()
    return jsonify({"reply": reply})

@app.route("/payment")
def payment():
    return render_template("payment.html")

@app.route("/create-checkout-session", methods=["POST"])
def create_checkout_session():
    return jsonify({"message": "시스템 준비중입니다."})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
