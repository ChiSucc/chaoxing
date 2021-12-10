import os.path

import requests
import requests.utils
from base64 import b64encode
from bs4 import BeautifulSoup
import json
import time
import src.path as path
import src.log as log
import re

def get_userinfo(session):
    url = 'http://i.mooc.chaoxing.com'
    resp = session.get(url)
    soup = BeautifulSoup(resp.text,'lxml')
    name = soup.find_all("p",attrs={"class":"personalName"})[0].text
    school = soup.title.string.replace("\t","").replace(" ","").replace('\n',"")
    return name, school


class User:
    def __init__(self, usernm, passwd):
        self.usernm = str(usernm)
        self.passwd = str(passwd)
        self.logger = log.Logger("logs/{}.txt".format(usernm))

    def __del__(self):
        pass

    def login(self,further=False):
        s = requests.session()
        s.headers['User-Agent'] = 'Dalvik/2.1.0 (Linux; U; Android 5.1.1; SM-G9350 Build/LMY48Z) com.chaoxing.mobile/ChaoXingStudy_3_5.21_android_phone_206_1 (SM-G9350; Android 5.1.1; zh_CN)_19698145335.21'
        s.headers['X-Requested-With'] = 'XMLHttpRequest'
        url = 'https://passport2-api.chaoxing.com/fanyalogin'
        data = {
            'fid': '-1',
            'uname': str(self.usernm),
            'password': b64encode(self.passwd.encode('utf8')),
            'refer': 'http%3A%2F%2Fi.mooc.chaoxing.com',
            't': 'true',
            'forbidotherlogin': '0',
        }
        self.logger.info("正在尝试登录账号: {}".format(self.usernm))
        resp = s.post(url, data=data)
        try:
            if resp.status_code == 200 and resp.json().get('status'):
                user = {}
                self.logger.info("登录成功，账户: {}验证完毕".format(self.usernm))
                self.name, self.school = get_userinfo(s)
                self.tsp = time.strftime("%Y%m%d %H:%M:%S", time.localtime(time.time()))
                cookie = requests.utils.dict_from_cookiejar(resp.cookies)
                self.cookies = cookie
                user['usernm'] = self.usernm
                user['passwd'] = self.passwd
                user['userid'] = cookie['_uid']
                user['fid'] = cookie['fid']
                user['name'] = self.name
                user['school'] = self.school
                user['tsp'] = self.tsp
                self.logger.debug("正在写入本地文件")
                path.check_file('saves/{}/userinfo.json'.format(self.usernm))
                with open('saves/{}/userinfo.json'.format(self.usernm), 'w') as f:
                    json.dump(user, f)
                with open('saves/{}/cookies.json'.format(self.usernm), 'w') as f:
                    json.dump(cookie, f)
                self.logger.debug("本地文件写入成功")
                if further:
                    self.logger.debug("返回session模式")
                    return {'code': 1, 'session': s}
                else:
                    self.logger.debug("仅返回状态码模式")
                    return {'code': 1}
            else:
                self.logger.error("登录失败，账户: {}账号或密码不正确".format(self.usernm))
                return {'code': -1}
        except json.decoder.JSONDecodeError as e:
            self.logger.debug(resp.text)
            self.logger.critical("登录失败，请求获取的结果非JSON，已在日志中输出请求结果")
            self.logger.critical("请查看日志文件")
            return {'code': -2}

    def get_info(self):
        ret = self.login()
        if ret.get('code') == 1:
            return {"code":1, "data":{"usernm": self.usernm,"name": self.name, "school": self.school, "tsp": self.tsp}}
        else:
            return ret

    def get_cookies(self):
        if os.path.exists("saves/{}/cookies.json".format(self.usernm)):
            with open("saves/{}/cookies.json".format(self.usernm), 'r') as f:
                return json.loads(f.read())
        else:
            self.login()
            return self.cookies

    def refresh_course(self):
        courses = []
        cookies = self.get_cookies()
        resp = requests.get("http://mooc1-api.chaoxing.com/mycourse?rss=1&mcode=", headers={
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/96.0.4664.93 Safari/537.36"},
                            cookies=cookies)
        result = resp.json()
        channelList = result['channelList']
        for item in channelList:
            if "state" in item["content"]:
                dic = {}
                dic['id'] = item['content']['course']['data'][0]['id']
                dic['name'] = item['content']['course']['data'][0]['name']
                if item["content"]["state"] == 0:
                    dic['state'] = "开课"
                else:
                    dic['state'] = "结课"
                if os.path.exists("saves/{}/{}".format(self.usernm,item['content']['course']['data'][0]['id'])):
                    dic['exists'] = "存在"
                else:
                    dic['exists'] = "不存在"
                courses.append(dic)
        return courses

    def get_course_online(self, usernm, passwd, courseid):
        course = {}
        chapterids = []
        with open('saves/{}/cookies.json'.format(usernm),'r') as f:
            cookies = json.loads(f.read())

        url = 'http://mooc1-api.chaoxing.com/mycourse?rss=1&mcode='
        resp = requests.get(url, headers={
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/96.0.4664.93 Safari/537.36"},
                            cookies=cookies)
        channelList = resp.json().get("channelList")
        for item in channelList:
            if "state" in item["content"]:
                if str(item['content']['course']['data'][0]['id']) == str(courseid):
                    channelList_json = item
                    break

        course['cpi'] = channelList_json['cpi']
        course['clazzid'] = channelList_json['content']['id']
        course['courseid'] = channelList_json['content']['course']['data'][0]['id']
        course['coursenm'] = channelList_json['content']['course']['data'][0]['name']
        course['teacher'] = channelList_json['content']['course']['data'][0]['teacherfactor']
        with open('saves/{}/cookies.json'.format(usernm),'r') as f:
            cookies = json.loads(f.read())
        url = 'https://mooc1-1.chaoxing.com/visit/stucoursemiddle?courseid=' + str(
            course['courseid']) + '&clazzid=' + str(course['clazzid']) + '&vc=1&cpi=' + str(course['cpi'])

        resp = requests.get(url, headers={
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) "
                          "Chrome/96.0.4664.93 Safari/537.36"},
                            cookies=cookies)
        content = resp.text
        for chapter in re.findall('\?chapterId=(.*?)&', content):
            chapterids.append(str(chapter))
        course['enc'] = re.findall("&clazzid=.*?&enc=(.*?)'", content)[0]
        course_path = 'saves/{}/{}'.format(usernm, course['courseid'])
        path.check_path(course_path)
        with open('{}/courseinfo.json'.format(course_path), 'w') as f:
            json.dump(course, f)
        with open('{}/chapterid.json'.format(course_path), 'w') as f:
            json.dump(chapterids, f)
        return chapterids, course


    def get_course_local(self, usernm, courseid):
        course_path = 'saves/{}/{}'.format(usernm, courseid)
        path.check_path(course_path)
        with open('{}/courseinfo.json'.format(course_path), 'r') as f:
            course = json.loads(f.read())
        with open('{}/chapterid.json'.format(course_path), 'r') as f:
            chapterids = json.loads(f.read())
        return chapterids, course

