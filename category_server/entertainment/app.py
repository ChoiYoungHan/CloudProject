from flask import Flask, render_template, jsonify, request
from flask_cors import CORS
import boto3
from boto3.dynamodb.conditions import Key, Attr
from datetime import datetime, timedelta, timezone
from urllib.parse import unquote
import requests
import time

app = Flask(
    __name__,
    static_folder="static",
    static_url_path="/category/entertainment/static",
    template_folder="templates"
)
CORS(app)

DASHBOARD_URL = "http://dashboard-service.default.svc.cluster.local/log"

@app.before_request
def log_traffic():
    print("🔥 log_traffic() 실행됨:", request.path)  # 추가
    path = request.path
    if path.startswith("/category/entertainment"):
        try:
            print("📤 대시보드 전송 시도")  # 추가
            requests.post(DASHBOARD_URL, json={"category": "연예"})
            print("✅ 대시보드 전송 완료")  # 추가
        except Exception as e:
            print("❌ 대시보드 전송 실패:", e)

dynamodb = boto3.resource('dynamodb', region_name='us-west-2')
table = dynamodb.Table('NewsArticles')

@app.route("/category/entertainment")
def category_entertainment():
    now = datetime.now(timezone.utc)
    three_hours_ago = now - timedelta(hours=3)
    # 최근 3시간 내 + count 높은 순
    hot_news = table.scan(
        FilterExpression=Attr('category').eq('연예') &
                         Attr('timestamp').gt(three_hours_ago.isoformat())
    ).get('Items', [])
    hot_news_sorted = sorted(hot_news, key=lambda x: (-x['count'], x['timestamp']))[:3]
    # 최신 뉴스 (20개, 시간 역순)
    latest_news = table.query(
        KeyConditionExpression=Key('category').eq('연예'),
        ScanIndexForward=False,
        Limit=20
    ).get('Items', [])
    return render_template("category_entertainment.html", hot_news=hot_news_sorted, latest_news=latest_news)

@app.route('/category/entertainment/<timestamp>/<title>')
def get_entertainment_news_detail(timestamp, title):
    title = unquote(title)
    response = table.query(
        KeyConditionExpression=Key('category').eq('연예') & Key('timestamp').eq(timestamp)
    )
    items = response.get('Items', [])
    for item in items:
        if item['title'] == title:
            # count 필드 +1 업데이트
            table.update_item(
                Key={
                    'category': '연예',
                    'timestamp': timestamp
                },
                UpdateExpression="SET #c = #c + :inc",
                ExpressionAttributeNames={
                    '#c': 'count'
                },
                ExpressionAttributeValues={
                    ':inc': 1
                }
            )
            # 업데이트된 결과를 반영하려면 최신 데이터를 다시 조회하거나 기존 item에 count +1 적용
            item['count'] += 1  # UI 출력에 반영용
            return render_template("detail.html", article=item)
    return "해당 뉴스 없음", 404
    
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)