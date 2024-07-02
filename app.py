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


@app.route("/")
def home():
    return render_template("index.html")

@app.route("/login")
def login():
    return render_template("login.html")


@app.route('/login/register', methods=['POST'])
def insert_user_data():
    # 1. 클라이언트로부터 데이터를 받기
    uid_receive = request.form['user_id']  # 클라이언트로부터 user_id을 받는 부분
    upw_receive = request.form['user_pw']  # 클라이언트로부터 user_pw을 받는 부분

    user_data = {
        'uid' : uid_receive,
        'upw' : upw_receive,
    }

    # 3. mongoDB에 데이터를 넣기
    db.articles.insert_one(user_data)

    return jsonify({'result': 'success'})




if __name__ == "__main__":
    print(sys.executable)
    app.run("0.0.0.0", port=5001, debug=True)
