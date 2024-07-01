from bson import ObjectId
from pymongo import MongoClient

from flask import Flask, render_template, jsonify, request
from flask.json.provider import JSONProvider

import json
import sys


app = Flask(__name__)

client = MongoClient("localhost", 27017)
db = client.dbjungle


#####################################################################################
# 이 부분은 코드를 건드리지 말고 그냥 두세요. 코드를 이해하지 못해도 상관없는 부분입니다.
#
# ObjectId 타입으로 되어있는 _id 필드는 Flask 의 jsonify 호출시 문제가 된다.
# 이를 처리하기 위해서 기본 JsonEncoder 가 아닌 custom encoder 를 사용한다.
# Custom encoder 는 다른 부분은 모두 기본 encoder 에 동작을 위임하고 ObjectId 타입만 직접 처리한다.
class CustomJSONEncoder(json.JSONEncoder):
    def default(self, o):
        if isinstance(o, ObjectId):
            return str(o)
        return json.JSONEncoder.default(self, o)


class CustomJSONProvider(JSONProvider):
    def dumps(self, obj, **kwargs):
        return json.dumps(obj, **kwargs, cls=CustomJSONEncoder)

    def loads(self, s, **kwargs):
        return json.loads(s, **kwargs)


# 위에 정의되 custom encoder 를 사용하게끔 설정한다.
app.json = CustomJSONProvider(app)

# 여기까지 이해 못해도 그냥 넘어갈 코드입니다.
# #####################################################################################


#####
# 아래의 각각의 @app.route 은 RESTful API 하나에 대응됩니다.
# @app.route() 의 첫번째 인자는 API 경로,
# 생략 가능한 두번째 인자는 해당 경로에 적용 가능한 HTTP method 목록을 의미합니다.


# API #1: HTML 틀(template) 전달
#         틀 안에 데이터를 채워 넣어야 하는데 이는 아래 이어지는 /api/list 를 통해 이루어집니다.
@app.route("/")
def home():
    return render_template("index.html")


# API #2: 휴지통에 버려지지 않은 영화 목록을 반환합니다.
@app.route("/api/list", methods=["GET"])
def show_movies():
    # client 에서 요청한 정렬 방식이 있는지를 확인합니다. 없다면 기본으로 좋아요 순으로 정렬합니다.
    sortMode = request.args.get("sortMode", "likes")

    # 1. db에서 trashed 가 False인 movies 목록을 검색합니다. 주어진 정렬 방식으로 정렬합니다.
    # 참고) find({},{}), sort()를 활용하면 됨.
    #      개봉일 순서 정렬처럼 여러 기준으로 순서대로 정렬해야되는 경우 sort([('A', 1), ('B', 1)]) 처럼 줄 수 있음.
    #    TODO: 다음 코드에서 likes로 정렬이 정상동작하도록 직접 수정해보세요!!!
    if sortMode == "likes":
        movies = list(db.movies.find({"trashed": False}, {}))
    else:
        return jsonify({"result": "failure"})

    # 2. 성공하면 success 메시지와 함께 movies_list 목록을 클라이언트에 전달합니다.
    return jsonify({"result": "success", "movies_list": movies})


# API #3: 영화에 좋아요 숫자를 하나 올립니다.
@app.route("/api/like", methods=["POST"])
def like_movie():
    # 1. movies 목록에서 find_one으로 영화 하나를 찾습니다.
    #    TODO: 영화 하나만 찾도록 다음 코드를 직접 수정해보세요!!!
    movie = db.movies.find_one({})

    # 2. movie의 like 에 1을 더해준 new_like 변수를 만듭니다.
    new_likes = movie["likes"] + 1

    # 3. movies 목록에서 id 가 매칭되는 영화의 like 를 new_like로 변경합니다.
    #    참고: '$set' 활용하기!
    #    TODO: 영화 하나의 likes값이 변경되도록 다음 코드를 직접 수정해보세요!!!
    result = db.movies.update_one({}, {"$set": {"likes": new_likes}})

    # 4. 하나의 영화만 영향을 받아야 하므로 result.updated_count 가 1이면  result = success 를 보냄
    if result.modified_count == 1:
        return jsonify({"result": "success"})
    else:
        return jsonify({"result": "failure"})


if __name__ == "__main__":
    print(sys.executable)
    app.run("0.0.0.0", port=5000, debug=True)
