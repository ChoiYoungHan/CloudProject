from flask import Flask, render_template, redirect, jsonify
import boto3
from boto3.dynamodb.conditions import Key
from datetime import datetime, timedelta, timezone
from urllib.parse import unquote
from operator import itemgetter

app = Flask(__name__)

dynamodb = boto3.resource("dynamodb", region_name="us-west-2")
news_table = dynamodb.Table("NewsArticles")
trend_table = dynamodb.Table("trend_top6")

@app.route("/")
def index():
    return redirect("/all")

@app.route("/all")
def show_all():
    # 전체 뉴스 스캔
    response = news_table.scan()
    all_news = response.get("Items", [])
    all_news.sort(key=itemgetter("timestamp"), reverse=True)

    # 카테고리별 뉴스 필터링
    def filter_category(cat):
        return [item for item in all_news if item["category"] == cat][:4]

    # 최근 6시간 내 trend_top6에서 rank 1~3 키워드 추출
    now = datetime.now(timezone.utc)
    three_hours_ago = now - timedelta(hours=6)

    trend_keywords = set()
    trend_items = trend_table.scan().get("Items", [])
    print("[DEBUG] trend_table에서 가져온 항목 수:", len(trend_items))
    print("[DEBUG] trend_table 샘플:", trend_items[:1])
    for item in trend_items:
        try:
            ts = datetime.fromisoformat(item["timestamp"])
            if ts.tzinfo is None:
                ts = ts.replace(tzinfo=timezone.utc)
        except Exception as e:
            print("[ERROR] trend item 예외 발생:", item)
            print("         예외:", e)
            continue
    
    print("[DEBUG] 추출된 트렌드 키워드:", trend_keywords)

    # 키워드 포함된 뉴스 필터링
    news_hot = []
    for news in all_news:
        for kw in trend_keywords:
            if kw in news.get("title", "") or kw in news.get("content", ""):
                news_hot.append(news)
                break

    # count 기준 정렬 후 상위 4개
    news_hot = sorted(news_hot, key=lambda x: -int(x.get("count", 0)))[:4]
    print("[DEBUG] 핫 뉴스:", news_hot)

    return render_template("index.html",
                           news_hot=news_hot,
                           news_politics=filter_category("정치"),
                           news_society=filter_category("사회"),
                           news_entertainment=filter_category("연예"),
                           active_category="전체")

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
