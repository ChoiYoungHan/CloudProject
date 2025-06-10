from flask import Flask, render_template, redirect, jsonify
import boto3
from boto3.dynamodb.conditions import Key
from operator import itemgetter
import os

app = Flask(__name__)

dynamodb = boto3.resource("dynamodb", region_name="us-west-2")
table = dynamodb.Table("NewsArticles")

@app.route("/")
def index():
    return redirect("/all")

@app.route("/all")
def show_all():
    response = table.scan()
    items = response.get("Items", [])
    items.sort(key=itemgetter("timestamp"), reverse=True)

    def filter_category(cat):
        return [item for item in items if item["category"] == cat][:3]

    return render_template("index.html",
                           news_hot=filter_category("지금 화제"),
                           news_politics=filter_category("정치"),
                           news_society=filter_category("사회"),
                           news_entertainment=filter_category("연예"),
                           active_category="전체")

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
