from flask import Flask, render_template, jsonify, request, send_from_directory
from flask_cors import CORS
import boto3
from boto3.dynamodb.conditions import Key, Attr
from datetime import datetime, timedelta, timezone
from urllib.parse import unquote
import requests
from prometheus_client import Counter, generate_latest
import os

app = Flask(
    __name__,
    static_folder="static",
    static_url_path="/category/society/static",
    template_folder="templates"
)
CORS(app)

# Prometheus 카운터
category_requests = Counter(
    "category_http_requests_total",
    "Total HTTP requests by category",
    ["category"]
)

DASHBOARD_URL = "http://dashboard-service.default.svc.cluster.local/log"

# 모든 요청 전 트래픽 기록
@app.before_request
def log_traffic():
    path = request.path
    if path.startswith("/category/society") and "static" not in path:
        category_requests.labels(category="society").inc()
        try:
            requests.post(DASHBOARD_URL, json={"category": "사회"})
        except Exception as e:
            print("대시보드로 로그 전송 실패:", e)

# Prometheus 메트릭 엔드포인트
@app.route("/metrics")
def metrics():
    return generate_latest(), 200, {"Content-Type": "text/plain"}

# DynamoDB 연결
dynamodb = boto3.resource('dynamodb', region_name='us-west-2')
table = dynamodb.Table('NewsArticles')

# ✅ HTML 페이지 (SPA 구조)
@app.route("/category/society")
def serve_society_page():
    return render_template("society.html")  # 또는 send_from_directory("static", "society.html")

# ✅ JSON 데이터 API
@app.route("/api/category/society")
def api_category_society():
    now = datetime.now(timezone.utc)
    three_hours_ago = now - timedelta(hours=3)

    # 최근 3시간 내의 화제 뉴스
    hot_news = table.scan(
        FilterExpression=Attr('category').eq('사회') & Attr('timestamp').gt(three_hours_ago.isoformat())
    ).get('Items', [])
    hot_news_sorted = sorted(hot_news, key=lambda x: (-x['count'], x['timestamp']))[:3]

    # 최신 뉴스 (20개)
    latest_news = table.query(
        KeyConditionExpression=Key('category').eq('사회'),
        ScanIndexForward=False,
        Limit=20
    ).get('Items', [])

    return jsonify({
        "hot_news": hot_news_sorted,
        "latest_news": latest_news
    })

# ✅ 뉴스 상세 페이지 (SSR 유지)
@app.route('/category/society/<timestamp>/<title>')
def get_society_news_detail(timestamp, title):
    title = unquote(title)
    response = table.query(
        KeyConditionExpression=Key('category').eq('사회') & Key('timestamp').eq(timestamp)
    )
    items = response.get('Items', [])
    for item in items:
        if item['title'] == title:
            table.update_item(
                Key={'category': '사회', 'timestamp': timestamp},
                UpdateExpression="SET #c = #c + :inc",
                ExpressionAttributeNames={'#c': 'count'},
                ExpressionAttributeValues={':inc': 1}
            )
            item['count'] += 1
            return render_template("detail.html", article=item)
    return "해당 뉴스 없음", 404

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
