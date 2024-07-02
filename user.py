from bson import ObjectId
from pymongo import MongoClient

from flask import Flask, render_template, jsonify, request, redirect,url_for
from flask.json.provider import JSONProvider

import json
import sys

import jwt




app = Flask(__name__)

SECRET_KEY = 'jungle_3' # 토큰을 암호화할 key 세팅


# db connection
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





@app.route("/login")
def login():
    message = request.args.get('message')
    if message is None:
        return render_template("login.html")
    else:
        return render_template("login.html", message=message)
    



# 유저 회원가입
@app.route('/login/register', methods=['POST'])
def insert_user_data():
    # 1. 클라이언트로부터 데이터를 받기
    uid_receive = request.form['regi_id']  # 클라이언트로부터 user_id을 받는 부분
    upw_receive = request.form['regi_pw']  # 클라이언트로부터 user_pw을 받는 부분
    upw2_receive = request.form['regi_pw2']  # 클라이언트로부터 user_pw을 받는 부분
    uname_receive = request.form['regi_name']  # 클라이언트로부터 user_pw을 받는 부분

    if db.users.find_one({'user_id':uid_receive}) is None:
        # 중복아이디가 없으면 실행되는 이중 조건
        if upw_receive == upw2_receive:
            print("비번일치")

            user_data = {
            'user_id' : uid_receive,
            'user_pw' : upw_receive,
            'user_name' : uname_receive
            }

            db.users.insert_one(user_data)
            response = redirect(url_for('login'))
            return response
        else:
            print("비번 불일치")
            return render_template("login.html", message="비밀번호가 일치하지 않습니다. 다시 시도해주세요.")
    else:
        return render_template("login.html", message="중복된 아이디 입니다.")



# 유저 로그인 체크 
@app.route('/login/logincheck', methods=['POST'])
def logincheck():
    # 1. 클라이언트로부터 데이터를 받기
    uid_receive = request.form['user_id']  # 클라이언트로부터 user_id을 받는 부분
    upw_receive = request.form['user_pw']  # 클라이언트로부터 user_pw을 받는 부분

    user_data = {
        'user_id' : uid_receive,
        'user_pw' : upw_receive,
    }


    check = db.users.find_one({'user_id':user_data['user_id'],'user_pw':user_data['user_pw']})

    if check is None:
        # 로그인 실패
        print("로그인 실패")
        return jsonify({'result': 'fail', 'message': 'Invalid credentials'}), 401

    else:  
        # 로그인 성공
        print("로그인 성공")
        # 사용자 정보를 json 형태로 만든다.
        payload = {
            'user_id': user_data['user_id'],
            'user_pw': user_data['user_pw'],
        }
        # 토큰을 발급한다.
        token = jwt.encode(payload, SECRET_KEY, algorithm='HS256')


        response = redirect(url_for('index'))
        response.set_cookie('token', token)

        return response






@app.route('/index')
def index():
	# 발급한 토큰을 쿠키등에 저장해 놓도록 하자
    token = request.cookies.get('token') # 토큰을 저장할때 쓴 키값
    # print(f'token?:{token}')
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=['HS256'])
        return render_template('token.html',token= token,user_id=payload['user_id'],user_pw=payload['user_pw'])
   	# token이 만료 되었을때
    except jwt.ExpriedSignatureError:
        return '로그인이 만료되었습니다. 다시 로그인 해주세요'
    # token이 없을때
    except jwt.exceptions.DecodeError:
    	return '로그인 정보가 없습니다.'



if __name__ == "__main__":
    print(sys.executable)
    app.run("0.0.0.0", port=5001, debug=True)
