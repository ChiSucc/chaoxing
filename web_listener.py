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
    user = User(usernm,passwd)
    msg = user.get_info()
    return resp_ok(msg)


@app.route('/api/get_all_user', methods=['GET'])
def get_all_user():
    ret = handler.get_all_user()
    return resp_ok(ret)


if __name__ == "__main__":
    CORS(app, supports_credentials=True)
    app.run(host='0.0.0.0', port=7777, debug=True)