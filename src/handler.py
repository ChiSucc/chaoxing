import os

import requests
import requests.utils
from base64 import b64encode
from bs4 import BeautifulSoup
import json
import time
import src.path as path
import src.log as log


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
                data.append(dic)
    return data