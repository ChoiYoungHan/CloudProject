from flask import Flask, render_template, redirect, jsonify
import boto3
from boto3.dynamodb.conditions import Key
from operator import itemgetter
import os
import time
import logging

app = Flask(__name__)

dynamodb = boto3.resource("dynamodb", region_name="us-west-2")
table = dynamodb.Table("NewsArticles")

logging.basicConfig(filename="app.log", level=logging.INFO)

@app.route("/")
def index():
    return redirect("/all")

@app.route("/all")
def show_all():
    response = table.scan()
    items = response.get("Items", [])
    
    for item in items:
        if 'timestamp' in item:
            item['date'] = item['timestamp'].split("T")[0]
    
    items.sort(key=itemgetter("timestamp"), reverse=True)
    return render_template("index.html", news_list=items, active_category="전체")

@app.route("/api/all")
def api_all():
    response = table.scan()
    items = response.get("Items", [])
    items.sort(key=itemgetter("timestamp"), reverse=True)
    return jsonify(items[:20])

@app.route("/logs")
def show_logs():
    log_path = "app.log"
    if not os.path.exists(log_path):
        return "로그 파일 없음", 404
    with open(log_path, "r") as f:
        return f"<pre>{f.read()}</pre>"

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
