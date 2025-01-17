from bson import ObjectId
from pymongo import MongoClient
from flask import Flask, render_template, jsonify, request, redirect, url_for, send_file
from flask.json.provider import JSONProvider
import requests
import gridfs
import io
import json
import sys
import jwt
from jinja2 import Template

# timestamp
import datetime
from datetime import timedelta

app = Flask(__name__)
SECRET_KEY = "jungle_3"  # 토큰을 암호화할 key 세팅
# db connection
# client = MongoClient("mongodb://test:test@54.180.237.110/?authSource=admin", 27017)
client = MongoClient('localhost', 27017)
db = client.dbjungle
fs = gridfs.GridFS(db)


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


# 변수 저장 및 읽기를 위한 파일 경로
VARIABLE_FILE_PATH = "variable.json"


def save_variable_to_file(variable):
    with open(VARIABLE_FILE_PATH, "w") as f:
        # datetime 객체를 문자열로 변환하여 저장
        if "currenttime" in variable:
            variable["currenttime"] = variable["currenttime"].strftime(
                "%Y-%m-%dT%H:%M:%S"
            )
        json.dump(variable, f)


def load_variable_from_file():
    try:
        with open(VARIABLE_FILE_PATH, "r") as f:
            variable = json.load(f)
            # 문자열을 datetime 객체로 변환
            if "currenttime" in variable:
                variable["currenttime"] = datetime.datetime.strptime(
                    variable["currenttime"], "%Y-%m-%dT%H:%M:%S"
                )
            return variable
    except FileNotFoundError:
        return {}


# 게시글 업로드
# Card에 들어갈 콘텐츠 객체
class todayFeedContent:
    def __init__(
        self,
        u_name,
        user_id,
        figure_id,
        datetime,
        likes,
        title,
        imageID,
        learned,
        code,
        post_id,
    ):
        self.userName = u_name
        self.user_id = user_id
        self.figure_id = figure_id
        # datetime 자체로 넘겨줄수있으면 바꾸기!
        self.year = datetime.year
        self.month = datetime.month
        self.day = datetime.day
        self.time = datetime.time
        self.likes = likes
        self.title = title
        self.imageID = imageID
        self.learned = learned
        self.code = code
        self.post_id = post_id


def updateFeedContents(now, sorterParam):
    # DB에서 오늘 날짜의 CARD 불러오기
    minnow = now.strftime("%Y%m%d00000000")
    next_day = now + timedelta(days=1)
    maxnow = next_day.strftime("%Y%m%d00000000")

    # DB Search
    todayCardDB = db.posts.find({"created_at": {"$gte": minnow, "$lt": maxnow}})

    if sorterParam == "NEW":
        todayCardDB.sort({"created_at": -1})
    elif sorterParam == "LIKES":
        todayCardDB.sort({"likes": -1})

    todayCardDBLIST = list(todayCardDB)
    # [todayFeedContent]객체 리스트 생성하기
    articledatas = []
    for data in todayCardDBLIST:
        dt = todayFeedContent(
            data["u_name"],
            data["user_id"],
            data["figure_id"],
            datetime.datetime.strptime(data["created_at"], "%Y%m%d%H%M%S%f"),
            data["likes"],
            data["title"],
            data["figure_id"],
            data["learned"],
            data["code"],
            data["_id"],
        )
        articledatas.append(dt)
    return articledatas


# 위에 정의되 custom encoder 를 사용하게끔 설정한다.
app.json = CustomJSONProvider(app)


@app.route("/login")
def login():
    message = request.args.get("message")
    if message is None:
        return render_template("login.html")
    else:
        return render_template("login.html", message=message)


# 유저 회원가입
@app.route("/login/register", methods=["POST"])
def insert_user_data():
    # 1. 클라이언트로부터 데이터를 받기
    uid_receive = request.form["regi_id"]  # 클라이언트로부터 user_id을 받는 부분
    upw_receive = request.form["regi_pw"]  # 클라이언트로부터 user_pw을 받는 부분
    upw2_receive = request.form["regi_pw2"]  # 클라이언트로부터 user_pw을 받는 부분
    uname_receive = request.form["regi_name"]  # 클라이언트로부터 user_pw을 받는 부분
    if db.users.find_one({"user_id": uid_receive}) is None:
        # 중복아이디가 없으면 실행되는 이중 조건
        if upw_receive == upw2_receive:
            print("비번일치")
            user_data = {
                "user_id": uid_receive,
                "user_pw": upw_receive,
                "user_name": uname_receive,
            }
            db.users.insert_one(user_data)
            response = redirect(url_for("login"))
            return response
        else:
            print("비번 불일치")
            return render_template(
                "login.html", message="비밀번호가 일치하지 않습니다. 다시 시도해주세요."
            )
    else:
        return render_template("login.html", message="중복된 아이디 입니다.")


# 유저 로그인 체크
@app.route("/login/logincheck", methods=["POST"])
def logincheck():
    import time
    times = 30 * 60
    # 1. 클라이언트로부터 데이터를 받기
    uid_receive = request.form["user_id"]  # 클라이언트로부터 user_id을 받는 부분
    upw_receive = request.form["user_pw"]  # 클라이언트로부터 user_pw을 받는 부분
    user_data = {
        "user_id": uid_receive,
        "user_pw": upw_receive,
    }
    check = db.users.find_one(
        {"user_id": user_data["user_id"], "user_pw": user_data["user_pw"]}
    )
    if check is None:
        # 로그인 실패
        print("로그인 실패")
        return render_template("login.html", message="가입된 회원이 아닙니다.")
    else:
        # 로그인 성공
        print("로그인 성공")
        # 사용자 정보를 json 형태로 만든다.
        payload = {
            "user_id": user_data["user_id"],
            "user_pw": user_data["user_pw"],
            "user_name": check["user_name"],
            "exp":datetime.datetime.utcnow() + datetime.timedelta(seconds=times), 
            # encoding 후 exp 시간이 지나야 토큰이 만료되는데 지금 이 경우는 encoding 후 바로 redirect를 진행하기 때문에
            # 토큰 만료가 되지 않고 로그인이 된다. 이후 /index를 리로딩할 시 , 토큰 만료 시간을 따지게 된다.
        }
        # 토큰을 발급한다.
        token = jwt.encode(payload, SECRET_KEY, algorithm="HS256")
        # time.sleep(times+1)
        response = redirect(url_for("index"))
        response.set_cookie("token", token)
        return response


@app.route("/index")
def index():
    # 발급한 토큰을 쿠키등에 저장해 놓도록 하자
    token = request.cookies.get("token")  # 토큰을 저장할때 쓴 키값
    # print(f'token?:{token}')
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])

        now = datetime.datetime.now()

        prev_day = now - timedelta(days=1)
        next_day = now + timedelta(days=1)

        return render_template(
            "index.html",
            token=token,
            user_id=payload["user_id"],
            user_pw=payload["user_pw"],
            articledatas=updateFeedContents(now, "NEW"),
            yesterday = prev_day.strftime("%Y-%m-%d"),
            currentdate=now.strftime("%Y-%m-%d"),
            tomorrow = next_day.strftime("%Y-%m-%d"),
            sortparam = "NEW"
        )
    # token이 만료 되었을때
    except jwt.ExpiredSignatureError:
        return "로그인이 만료되었습니다. 다시 로그인 해주세요"
    # token이 없을때
    except jwt.exceptions.DecodeError:
        return "로그인 정보가 없습니다."


# 할 일: uid를 find하고 db에 잘 저장하기
# like초기화
@app.route("/writeArticle", methods=["POST"])
def post_article():
    # 1. 클라이언트로부터 데이터를 받기
    title = request.form["title"]
    learned = request.form["learned"]
    code = request.form["code"]
    if "figure" not in request.files:
        print("no fig")
        figure_id = None
    else:
        print("yes fig")
        figure = request.files["figure"]
        print(figure.filename)
        figure_id = fs.put(
            figure.read(), filename=figure.filename, content_type=figure.content_type
        )
    print(title, learned, code, figure_id)
    post = {
        "figure_id": figure_id,
        "u_name": db.users.find_one({"user_id": request.form["user_id"]})["user_name"],
        "user_id": request.form["user_id"],
        "title": title,
        "likes": 0,
        "learned": learned,
        "code": code,
        "created_at": datetime.datetime.now().strftime("%Y%m%d%H%M%S"),
    }
    print(post)
    # 3. mongoDB에 데이터를 넣기
    db.posts.insert_one(post)
    return jsonify({"result": "success"})


# 할 일: uid를 find하고 db에 잘 저장하기
# like초기화
@app.route("/modifyArticle", methods=["POST"])
def modify_article():
    # 1. 클라이언트로부터 데이터를 받기
    title = request.form["title"]
    learned = request.form["learned"]
    code = request.form["code"]
    post_id = request.form["post_id"]

    # html 변조로 남의 것을 수정한 것이 아닌지 확인 해야함
    user_id = request.form["user_id"]

    print(db.posts.find_one({"_id": ObjectId(post_id)}))
    if db.posts.find_one({"_id": ObjectId(post_id)})["user_id"] != user_id:
        print("not matching")
        print(db.posts.find_one({"_id": ObjectId(post_id)})["user_id"], user_id)
        return jsonify({"result": "fail"})

    db.posts.update_one(
        {"_id": ObjectId(post_id)},
        {"$set": {"title": title, "learned": learned, "code": code}},
    )

    if "figure" in request.files:
        # 이전 figure 삭제
        before_figure_id = db.posts.find_one({"_id": ObjectId(post_id)})["figure_id"]
        ret = fs.delete(ObjectId(before_figure_id))
        print("deleting file ret", ret)

        # 새로운 figure 추가
        print("yes fig")
        figure = request.files["figure"]
        print(figure.filename)
        figure_id = fs.put(
            figure.read(), filename=figure.filename, content_type=figure.content_type
        )
        db.posts.update_one(
            {"_id": ObjectId(post_id)}, {"$set": {"figure_id": figure_id}}
        )
    
    return jsonify({"result": "success"})


# post의 이미지를 불러올 때 img src="http://127.0.0.1:5000/img/{$figure_id}">
# 형식으로 하시면 됩니다.
# 서버로 하는 경우는, 주소를 서버로.
@app.route("/img/<figure_id>")
def send_image(figure_id):
    # row = db.posts.find(ObjectId("6683ab97caca1a79eaba33ba"))
    # print(row)
    # print(figure_id)
    # figure_id가 'null' 문자열이거나 비어 있는 경우 디폴트 이미지 반환
    if figure_id == "null" or figure_id.strip() == "":
        return send_default_image()
    try:
        file = fs.get(ObjectId(figure_id))
        # print("file found")
        # print(file)
        return send_file(
            io.BytesIO(file.read()),
            mimetype=file.content_type,
            as_attachment=True,
            download_name=file.filename,
        )
    except (gridfs.NoFile, Exception) as e:
        return send_default_image()


def send_default_image():
    default_image_url = "https://jungle-compass.krafton.com/pluginfile.php/1/theme_moove/logo/1705035087/jungle_big.png"  # 디폴트 이미지 경로
    response = requests.get(default_image_url)
    if response.status_code == 200:
        default_mime_type = response.headers.get("Content-Type", "image/png")
        return send_file(
            io.BytesIO(response.content),
            mimetype=default_mime_type,
            as_attachment=True,
            download_name="default_image.png",
        )
    else:
        return jsonify({"error": "Default image not found"}), 404


@app.route("/addLikes", methods=["POST"])
def addLikes():

    user_id = request.form["user_id"]
    post_id = request.form["post_id"]
    likes = int(request.form["likesnum"])

    print(f"")
    print(f"user : {user_id} ,  post : {post_id} ,   likes : {likes} , ")

    # post_id 로 게시글 찾아와서 좋아요 업데이트 하기
    # try:
    db.posts.update_one({"_id": ObjectId(post_id)}, {"$set": {"likes": likes}})

    
    return jsonify({"result": "success"})


@app.route("/send_date/<today>/<sortparam>")
def send_date(today,sortparam):
    token = request.cookies.get("token")  # 토큰을 저장할때 쓴 키값

    try:
        now = datetime.datetime.strptime(today, "%Y-%m-%d")

        prev_day = now - timedelta(days=1)
        next_day = now + timedelta(days=1)

        payload = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])

        articledatas = updateFeedContents(now, sortparam)
        return render_template(
            "index.html",
            token=token,
            user_id=payload["user_id"],
            user_pw=payload["user_pw"],
            articledatas=articledatas,
            yesterday = prev_day.strftime("%Y-%m-%d"),
            currentdate=now.strftime("%Y-%m-%d"),
            tomorrow = next_day.strftime("%Y-%m-%d"),
            sortparam = sortparam
        )
    except jwt.ExpiredSignatureError:
        return "로그인이 만료되었습니다. 다시 로그인 해주세요"
    except jwt.exceptions.DecodeError:
        return "로그인 정보가 없습니다."


if __name__ == "__main__":
    print(sys.executable)
    # app.run("0.0.0.0", port=5000, debug=True)
    app.run("0.0.0.0", port=5001, debug=True)
