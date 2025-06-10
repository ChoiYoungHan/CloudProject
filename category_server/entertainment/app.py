from flask import Flask, render_template, jsonify
from flask_cors import CORS
import boto3
from boto3.dynamodb.conditions import Key, Attr
from datetime import datetime, timedelta, timezone
from urllib.parse import unquote

app = Flask(
    __name__,
    static_folder="static",
    static_url_path="/category/entertainment/static",
    template_folder="templates"
)
CORS(app)

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
            return render_template("detail.html", article=item)
    return "해당 뉴스 없음", 404

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
