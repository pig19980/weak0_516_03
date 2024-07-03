from flask import Flask, render_template

app = Flask(__name__)

from pymongo import MongoClient           # pymongo를 임포트 하기(패키지 인스톨 먼저 해야겠죠?)
client = MongoClient('localhost', 27017)  # mongoDB는 27017 포트로 돌아갑니다.
db = client.jungleTest                    # 'jungle'라는 이름의 db를 만듭니다.

from jinja2 import Template

#timestamp
import datetime 
from datetime import timedelta

# Card에 들어갈 콘텐츠 객체
class todayFeedContent:
    def __init__(self, u_name, datetime, likes, title, image, contents):
        self.userName = u_name
        self.year = datetime.year
        self.month = datetime.month
        self.day = datetime.day
        self.likes = likes
        self.title = title
        self.image = image
        self.contents = contents

# DB에서 오늘 날짜의 CARD 불러오기
todayCardDB = []

now = datetime.datetime.now()
minnow = now.strftime("%Y%m%d00000000")

next_day = now + timedelta(days=1)

maxnow = next_day.strftime("%Y%m%d00000000")

#DB Search
todayCardDB = list(db.posts.find({'created_at': {'$gte': minnow, '$lt': maxnow}}))


#[todayFeedContent]객체 리스트 생성하기
userdata = []
for data in todayCardDB:
    dt = todayFeedContent(data["u_name"],datetime.datetime.strptime(data['created_at'], "%Y%m%d%H%M%S%f"), 0, data["title"], None, data["learned"])
    userdata.append(dt)


@app.route("/")
def home():
    return render_template("index.html", user = userdata)

if __name__ == "__main__":
    app.run("0.0.0.0", port=5001, debug=True)

