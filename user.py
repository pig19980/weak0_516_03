from bson import ObjectId
from pymongo import MongoClient

from flask import Flask, render_template, jsonify, request, redirect,url_for
from flask.json.provider import JSONProvider

import json
import sys

import jwt
import hashlib



app = Flask(__name__)

SECRET_KEY = 'jungle_3' # 토큰을 암호화할 key 세팅

client = MongoClient("localhost", 27017)
db = client.dbjungle



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
def login():
    return render_template("login.html")




# 유저 회원가입
@app.route('/login/register', methods=['POST'])
def insert_user_data():
    # 1. 클라이언트로부터 데이터를 받기
    uid_receive = request.form['regi_id']  # 클라이언트로부터 user_id을 받는 부분
    upw_receive = request.form['regi_pw']  # 클라이언트로부터 user_pw을 받는 부분
    upw2_receive = request.form['regi_pw2']  # 클라이언트로부터 user_pw을 받는 부분

    if upw_receive== upw2_receive:
        print("비번일치")

        user_data = {
        'uid' : uid_receive,
        'upw' : upw_receive,
        }
          
        db.users.insert_one(user_data)
    else:
        print("비번 불일치")

    return jsonify({'result': 'success'})


# 유저 로그인 체크 
@app.route('/login/logincheck', methods=['POST'])
def logincheck():
    # 1. 클라이언트로부터 데이터를 받기
    uid_receive = request.form['user_id']  # 클라이언트로부터 user_id을 받는 부분
    upw_receive = request.form['user_pw']  # 클라이언트로부터 user_pw을 받는 부분

    user_data = {
        'uid' : uid_receive,
        'upw' : upw_receive,
    }


    check = db.users.find_one({'uid':user_data['uid'],'upw':user_data['upw']})

    if check is None:
        # 로그인 실패
        print("로그인 실패")
        return jsonify({'result': 'fail', 'message': 'Invalid credentials'}), 401

    else:  
        # 로그인 성공
        print("로그인 성공")
        # 사용자 정보를 json 형태로 만든다.
        payload = {
            'id': user_data['uid'],
            'pw': user_data['upw'],

        }
        # 토큰을 발급한다.
        token = jwt.encode(payload, SECRET_KEY, algorithm='HS256')


        response = redirect(url_for('index'))
        response.set_cookie('token', token)

        return response


        # return render_template("token.html",token=token)
        # return jsonify({'result': 'success', 'token': token})



@app.route('/select')
def select():
    # MongoDB에서 데이터 모두 보기
    all_users = list(db.users.find({}))

    if all_users==None:
        print("없다")
    else:
        print("있다")

    return jsonify({'result': 'success',"user":all_users})


@app.route('/index')
def index():
	# 발급한 토큰을 쿠키등에 저장해 놓도록 하자
    token = request.cookies.get('token') # 토큰을 저장할때 쓴 키값
    # print(f'token?:{token}')
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=['HS256'])
        return render_template('token.html',token= token,user_id=payload['id'],user_pw=payload['pw'])
   	# token이 만료 되었을때
    except jwt.ExpriedSignatureError:
        return '로그인이 만료되었습니다. 다시 로그인 해주세요'
    # token이 없을때
    except jwt.exceptions.DecodeError:
    	return '로그인 정보가 없습니다.'



if __name__ == "__main__":
    print(sys.executable)
    app.run("0.0.0.0", port=5001, debug=True)
