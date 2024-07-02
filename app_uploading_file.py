from flask import Flask, render_template, jsonify, request, send_file
from pymongo import MongoClient
from bson import ObjectId
import gridfs
import datetime
import io

app = Flask(__name__)

client = MongoClient("localhost", 27017)  # mongoDB는 27017 포트로 돌아갑니다.
db = client.dbjungle  # 'dbjungle'라는 이름의 db를 만들거나 사용합니다.
fs = gridfs.GridFS(db)


@app.route("/")
def home():
    return render_template("writing_button.html")


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
        "title": title,
        "learned": learned,
        "code": code,
        "created_at": datetime.datetime.utcnow(),
    }

    # 3. mongoDB에 데이터를 넣기
    db.posts.insert_one(post)

    return jsonify({"result": "success"})


# post의 이미지를 불러올 때 img src="http://127.0.0.1:5000/img/{$figure_id}">
# 형식으로 하시면 됩니다.
# 서버로 하는 경우는, 주소를 서버로.


@app.route("/img/<figure_id>")
def send_image(figure_id):
    # row = db.posts.find(ObjectId("6683ab97caca1a79eaba33ba"))
    # print(row)
    # print(figure_id)
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
    except gridfs.NoFile:
        return jsonify({"error": "File not found"}), 404


if __name__ == "__main__":
    app.run("0.0.0.0", port=5000, debug=True)
