from flask import Flask, jsonify
from flask_cors import CORS
import boto3
from boto3.dynamodb.conditions import Key
from datetime import datetime, timezone
import time, multiprocessing
from urllib.parse import unquote


app = Flask(__name__)
CORS(app)

# 테스트를 위한 주석 추가
# DynamoDB 연결
dynamodb = boto3.resource('dynamodb', region_name='us-west-2')
table = dynamodb.Table('NewsArticles')

@app.route("/category/politics")
def category_entertainment():
    
    print("정치 카테고리 요청 들어옴")
    
    response = table.query(
        KeyConditionExpression=Key('category').eq('정치'),
        ScanIndexForward=False,
        Limit=20
    )
    items = response.get("Items", [])
    return jsonify(items)

@app.route('/category/politics/<timestamp>/<title>')
def get_politics_news_detail(timestamp, title):
    title = unquote(title)
    
    response = table.query(
        KeyConditionExpression=Key('category').eq('정치') & Key('timestamp').eq(timestamp)
    )
    items = response.get('Items', [])
    for item in items:
        if item['title'] == title:
            return jsonify(item)
    return jsonify({'error': '해당 뉴스 없음'}), 404

@app.route("/cpu-stress")
def cpu_stress():
    import time
    start = time.time()
    x = 0
    while time.time() - start < 30:  # 30초 동안 반복
        x += sum(i * i for i in range(10000))
    return f"완료. 걸린시간: {time.time() - start:.2f}초"


@app.route("/cpu-burn")
def cpu_burn():
    def burn():
        while True:
            x = 0
            for _ in range(1000000):
                x += 1

    for _ in range(multiprocessing.cpu_count()):
        p = multiprocessing.Process(target=burn)
        p.start()
    return "CPU burn started"


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)