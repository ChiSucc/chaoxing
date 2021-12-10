import os

import requests
import requests.utils
from base64 import b64encode
from bs4 import BeautifulSoup
import json
import time
import src.path as path
import src.log as log
import src.user

logger = log.Logger("logs/main.txt")

def get_all_user():
    data = []
    path.check_path("saves")
    users = os.listdir("saves")
    for user in users:
        if user[0] != '.':
            dic = {}
            with open("saves/{}/userinfo.json".format(user),'r') as f:
                info = json.loads(f.read())
                dic['name'] = info['name']
                dic['usernm'] = info['usernm']
                dic['school'] = info['school']
                dic['tsp'] = info['tsp']
            with open("saves/{}/cookies.json".format(user),'r') as f:
                cookies = json.loads(f.read())
            resp = requests.get("http://i.mooc.chaoxing.com/",headers={"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/96.0.4664.93 Safari/537.36"}, cookies=cookies)
            if BeautifulSoup(resp.text,"lxml").title.string == "用户登录":
                dic['valid'] = "无效"
            else:
                dic['valid'] = "有效"
            data.append(dic)

    return data


def refresh_user(usernm):
    path.check_path("saves/{}".format(usernm))
    if os.path.exists("saves/{}/userinfo.json".format(usernm)):
        with open("saves/{}/userinfo.json".format(usernm),'r') as f:
            info = json.loads(f.read())
        usernm = info['usernm']
        passwd = info['passwd']
        user = src.user.User(usernm,passwd)
        data = user.get_info()
        return {"code":1,"data":data}
    else:
        return {"code":-2}


def refresh_course(usernm):
    path.check_path("saves/{}".format(usernm))
    if os.path.exists("saves/{}/userinfo.json".format(usernm)):
        with open("saves/{}/userinfo.json".format(usernm),'r') as f:
            info = json.loads(f.read())
        usernm = info['usernm']
        passwd = info['passwd']
        user = src.user.User(usernm, passwd)
        data = user.refresh_course()
        return {"code": 1, "data": data}
    else:
        return {"code": -2}