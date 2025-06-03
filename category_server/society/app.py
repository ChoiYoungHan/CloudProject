from flask import Flask, jsonify
from flask_cors import CORS
import boto3
from boto3.dynamodb.conditions import Key
from datetime import datetime, timezone
from urllib.parse import unquote


app = Flask(__name__)
CORS(app)

# 테스트를 위한 주석 추가
# DynamoDB 연결
dynamodb = boto3.resource('dynamodb', region_name='us-west-2')
table = dynamodb.Table('NewsArticles')

@app.route("/category/society")
def category_entertainment():
    response = table.query(
        KeyConditionExpression=Key('category').eq('사회'),
        ScanIndexForward=False,
        Limit=20
    )
    items = response.get("Items", [])
    return jsonify(items)

@app.route('/category/society/<timestamp>/<title>')
def get_society_news_detail(timestamp, title):
    title = unquote(title)

    response = table.query(
        KeyConditionExpression=Key('category').eq('사회') & Key('timestamp').eq(timestamp)
    )
    items = response.get('Items', [])
    for item in items:
        if item['title'] == title:
            return jsonify(item)
    return jsonify({'error': '해당 뉴스 없음'}), 404

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)