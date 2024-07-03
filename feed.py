from bson import ObjectId
from flask import Flask,  render_template, jsonify, request, redirect,url_for, send_file
import requests

app = Flask(__name__)

from pymongo import MongoClient           # pymongo를 임포트 하기(패키지 인스톨 먼저 해야겠죠?)
client = MongoClient('localhost', 27017)  # mongoDB는 27017 포트로 돌아갑니다.
db = client.dbjungle                # 'jungle'라는 이름의 db를 만듭니다.

import gridfs
import io


fs = gridfs.GridFS(db)

from jinja2 import Template

#timestamp
import datetime 
from datetime import timedelta

# Card에 들어갈 콘텐츠 객체
class todayFeedContent:
    def __init__(self, u_name,figure_id, datetime, likes, title, imageID, learned, code):
        self.userName = u_name
        self.figure_id = figure_id
        #datetime 자체로 넘겨줄수있으면 바꾸기!
        self.year = datetime.year
        self.month = datetime.month
        self.day = datetime.day
        self.time = datetime.time

        self.likes = likes
        self.title = title
        self.imageID = imageID
        self.learned = learned
        self.code = code


#DB에서 오늘 날짜의 CARD 불러오기
todayCardDB = []

now = datetime.datetime.now()
minnow = now.strftime("%Y%m%d00000000")

next_day = now + timedelta(days=1)

maxnow = next_day.strftime("%Y%m%d00000000")

#DB Search
todayCardDB = list(db.posts.find({'created_at': {'$gte': minnow, '$lt': maxnow}}))

for card in todayCardDB:
    print(card["created_at"])
#[todayFeedContent]객체 리스트 생성하기
articledatas = []
for data in todayCardDB:
    dt = todayFeedContent(data["u_name"],data["figure_id"],datetime.datetime.strptime(data['created_at'], "%Y%m%d%H%M%S%f"), data["likes"], data["title"], data["figure_id"], data["learned"],data["code"])
    articledatas.append(dt)


@app.route("/img/<figure_id>")
def send_image(figure_id):
    # row = db.posts.find(ObjectId("6683ab97caca1a79eaba33ba"))
    # print(row)
    # print(figure_id)
    
    try:
        file = fs.get(ObjectId(figure_id))
        # print("file found")
        # print(file)
        print("파일타입")
        print(file.content_type)
        return send_file(
            io.BytesIO(file.read()),
            mimetype=file.content_type,
            
            as_attachment=True,
            download_name=file.filename,
        )
    except gridfs.NoFile:
        ### Default Image ###
        default_image_url = 'https://jungle-compass.krafton.com/pluginfile.php/1/theme_moove/logo/1705035087/jungle_big.png'  # 디폴트 이미지 경로
        default_mime_type = 'image/png'  # 디폴트 이미지의 MIME 타입 (예: JPEG)


        response = requests.get(default_image_url)
        if response.status_code == 200:
            return send_file(
                io.BytesIO(response.content),
                mimetype=default_mime_type,
                as_attachment=True,
                download_name='default_image.png',
            )
        else:
            return jsonify({"error": "Default image not found"}), 404

@app.route("/")
def home():
    return render_template("index.html", articledatas = articledatas)

if __name__ == "__main__":
    app.run("0.0.0.0", port=5001, debug=True)

