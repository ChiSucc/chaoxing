from flask import Flask, redirect, request
from flask_cors import CORS
from src.user import User
from src import handler


app = Flask(__name__)


def resp_ok(resp_data):
    resp = {'code': 200, 'data': resp_data}
    return resp


@app.route('/')
def index():
    return redirect('/static/index.html', code=302)


@app.route('/api/get_info', methods=['GET'])
def get_info():
    usernm = request.args.get("usernm")
    passwd = request.args.get("passwd")
    user1 = User(usernm,passwd)
    msg = user1.get_info()
    return resp_ok(msg)


@app.route('/api/get_all_user', methods=['GET'])
def get_all_user():
    ret = handler.get_all_user()
    return resp_ok(ret)


@app.route('/api/refresh_user', methods=['GET'])
def refresh_user():
    usernm = request.args.get("usernm")
    ret = handler.refresh_user(usernm)
    return resp_ok(ret)


@app.route('/api/refresh_course', methods=['GET'])
def refresh_course():
    usernm = request.args.get("usernm")
    ret = handler.refresh_course(usernm)
    return resp_ok(ret)


@app.route('/api/delete_user', methods=['GET'])
def delete_user():
    usernm = request.args.get("usernm")
    ret = handler.delete_user(usernm)
    return resp_ok(ret)


@app.route('/api/delete_course', methods=['GET'])
def delete_course():
    usernm = request.args.get("usernm")
    courseid = request.args.get("courseid")
    ret = handler.delete_course(usernm,courseid)
    return resp_ok(ret)


@app.route('/api/add_course', methods=['GET'])
def delete_course():
    usernm = request.args.get("usernm")
    courseid = request.args.get("courseid")
    ret = handler.add_course(usernm,courseid)
    return resp_ok(ret)



if __name__ == "__main__":
    CORS(app, supports_credentials=True)
    app.run(host='0.0.0.0', port=7777, debug=True)