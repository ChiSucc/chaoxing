import requests
import requests.utils
from bs4 import BeautifulSoup
import json
import time
import logging
import re
from base64 import b64encode
from os import listdir,rmdir, mkdir, remove
from os.path import exists, join, isfile


GENERAL_HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/96.0.4664.93 Safari/537.36"}


def check_path(path):
    """
    遍历检查各个子路径是否存在，不存在即mkdir新建路径
    :param path: 路径
    :return:
    """
    _path = path.split('/')
    if len(_path) == 1:
        # 路径只有一级
        if not exists(path):
            mkdir(path)
    else:
        # 路径有多级
        for i in range(1, len(_path) + 1):
            path_tmp = '/'.join(_path[:i])
            if not exists(path_tmp):
                mkdir(path_tmp)


def check_file(path):
    """
    遍历检查路径下的文件夹和文件是否存在，不存在即新建
    :param path: 路径
    :return:
    """
    _path = path.split('/')
    if len(_path) != 1:
        # 路径有多级
        check_path('/'.join(_path[:-1]))
    with open(path, 'w'):
        pass


def delete_path(path):
    for i in listdir(path):
        file_data = join(path,i)
        if isfile(file_data):
            remove(file_data)
        else:
            delete_path(file_data)
    rmdir(path)


def ret_msg(status, data):
    return {"status":status,"data":data}


def formulate_cookies_from_dict(cookies_raw: dict):
    cookies = ""
    for key in cookies_raw:
        cookies += f"{key}={cookies_raw.get(key)}; "
    return cookies[:-2]




class Logger:
    def __init__(self, path, stream=True, output=True, slevel=logging.INFO, olevel=logging.DEBUG):
        self.logger = logging.getLogger(path)
        self.logger.handlers.clear()
        self.logger.setLevel(logging.DEBUG)
        if stream:
            # 设置CMD日志
            sh = logging.StreamHandler()
            sh.setFormatter(logging.Formatter('[%(asctime)s] [%(levelname)s] %(message)s', '%Y-%m-%d %H:%M:%S'))
            sh.setLevel(slevel)
            self.logger.addHandler(sh)
        if output:
            # 设置文件日志
            fh = logging.FileHandler(path)
            fh.setFormatter(logging.Formatter(
                '[%(asctime)s] [%(levelname)s] [file: %(filename)s] [func: %(funcName)s] [line: %(lineno)d] %(message)s',
                '%Y-%m-%d %H:%M:%S'))
            fh.setLevel(olevel)
            self.logger.addHandler(fh)

    def __del__(self):
        pass

    def debug(self, message):
        self.logger.debug(message)

    def info(self, message):
        self.logger.info(message)

    def warn(self, message):
        self.logger.warning(message)

    def error(self, message):
        self.logger.error(message)

    def critical(self, message):
        self.logger.critical(message)


class User:
    def __init__(self, usernm: str, passwd=""):
        self.logger = Logger("Logs/ClassUser.log")
        check_path(f"Saves/{usernm}")
        self.fid = ""
        self.userid = ""
        if usernm and not passwd:
            self.logger.info("仅用户名模式(User)")
            if exists(f"Saves/{usernm}/secret.cx"):
                with open(f"Saves/{usernm}/secret.cx", "r") as f:
                    self.usernm = usernm
                    self.passwd = json.loads(f.read()).get("passwd")
                    self.logger.info("用户信息设置完毕(User)")
        elif usernm and passwd:
            self.logger.info("用户名且密码模式(User)")
            self.usernm = usernm
            self.passwd = passwd
            self.logger.info("用户信息设置完毕(User)")
        else:
            self.logger.debug("未知模式(User)")

    def login(self):
        """
        登录请求，并保存Cookies内容至本地文件Saves/{usernm}/cookies.cx
        :return: msg{格式化后的Cookies字符串}
        """
        self.logger.info("开始尝试登录")
        login_url = 'https://passport2.chaoxing.com/fanyalogin'
        data = {
            "fid": "-1",
            "uname": self.usernm,
            "password": b64encode(self.passwd.encode("utf-8")).decode("utf-8"),
            "refer": "http%3A%2F%2Fi.mooc.chaoxing.com",
            "t": "true",
            "validate": "",
        }
        # 发送登录请求
        resp = requests.post(login_url, data=data, headers=GENERAL_HEADERS)
        self.logger.debug("请求发送完毕")
        # 判断请求返回正常
        if resp.status_code == 200 and resp.content:
            self.logger.debug("Response接收正常")
            # 判断请求返回是否为JSON格式
            try:
                resp.json()
            except json.decoder.JSONDecodeError:
                self.logger.error("Response内容异常，出现JSONDecodeError错误，请检查您的网络情况。若无法解决，请在GitHub页面提交截图Issue")
                self.logger.error("相关日志:")
                self.logger.error("url=https://passport2.chaoxing.com/fanyalogin")
                self.logger.error(f"data={data}")
                self.logger.error(f"resp={resp.content.decode('utf8')}")
                # 返回错误信息
                return ret_msg("fail","Response出现JSONDecodeError错误，请检查日志")
            result = resp.json()
            self.logger.debug("JSON格式读取正常")
            # 判断返回JSON信息内容
            if not result.get("status") and (("或密码错误" in result.get("msg2")) or ('password is wrong' in result.get("msg2"))):
                self.logger.warn("您的用户名或密码错误")
                self.logger.warn("错误三次将被冻结15分钟")
                return ret_msg("fail","您的用户名或密码错误,错误三次将被冻结15分钟")
            elif not result.get("status") and "已冻结" in result.get("msg2"):
                self.logger.warn("账号因多次输入密码错误，已冻结15分钟")
                return ret_msg("fail","账号因多次输入密码错误，已冻结15分钟")
            elif result.get("status") and "i.mooc.chaoxing.com" in result.get("url"):
                expires = 0
                self.logger.info("登录成功")
                self.logger.debug("正在读取Cookies")
                cookies = resp.cookies
                # 读取Cookies的到期时间(timestamp)
                for cookie in cookies:
                    if cookie.expires:
                        expires = cookie.expires
                        break
                self.logger.info(f"Cookies到期日期为{time.strftime('%Y/%m/%d', time.localtime(expires))}")
                # 获取用户基本信息(id&fid)
                self.userid = requests.utils.dict_from_cookiejar(cookies)['_uid']
                self.fid = requests.utils.dict_from_cookiejar(cookies)['fid']
                raw = {
                    "cookies": requests.utils.dict_from_cookiejar(cookies),
                    "expires": expires,
                }
                # 将dict(Cookies)保存至本地文件Saves/{self.usernm}/cookies.cx
                with open(f"Saves/{self.usernm}/cookies.cx", 'w') as f:
                    json.dump(raw, f)
                # 将dict(info)用户账号密码保存至本地文件Saves/{self.usernm}/secret.cx
                with open(f"Saves/{self.usernm}/secret.cx", 'w') as f:
                    json.dump({"usernm":self.usernm,"passwd":self.passwd},f)
                # 返回格式化后的Cookies数据
                return ret_msg("success",formulate_cookies_from_dict(requests.utils.dict_from_cookiejar(cookies)))
            else:
                # 出现未知的返回码，未来出现BUG后再更新
                self.logger.error("出现未知返回码，正在输出日志")
                self.logger.error(resp.text)
                self.logger.error("若无法解决，请在GitHub页面提交截图Issue")
                return ret_msg("fail","出现未知返回码，请检查日志")

        else:
            self.logger.error("网络连接超时，请检查您的网络连接状况")
            return ret_msg("fail","网络连接超时，请检查您的网络连接状况")

    def load_cookies(self):
        """
        读取用户的Cookies数据(本地|在线)
        :return: msg{格式化后的Cookies字符串}
        """
        self.logger.info("开始尝试获取Cookies")
        # 判断本地是否存在Cookies文件
        if exists(f"Saves/{self.usernm}/cookies.cx"):
            self.logger.debug("本地存在Cookies文件")
            with open(f"Saves/{self.usernm}/cookies.cx",'r') as f:
                raw = json.loads(f.read())
                limit = int(raw.get("expires")) - int(time.time())
                days = round(limit / 86400, 2)
                self.logger.info(f"本地保存的Cookies还剩余{round(limit/86400, 2)}天")
                # 判断Cookies有效期是否大于1天
                if days < 1:
                    self.logger.info("Cookies已过期，正在尝试重新在线登录读取Cookies")
                    # 调用登录函数
                    ret = self.login()
                    if ret.get("status") == "success":
                        # 返回格式化后的Cookies
                        return ret.get("data")
                    else:
                        return {}
                else:
                    self.logger.info("Cookies有效，正在直接读取本地Cookies")
                    # 获取用户基本信息(id&fid)
                    self.userid = raw.get("cookies")['_uid']
                    self.fid = raw.get("cookies")['fid']
                    # 返回格式化后的Cookies
                    return formulate_cookies_from_dict(raw.get("cookies"))

        else:
            self.logger.info("不存在本地保存的Cookies,正在尝试重新在线登录读取Cookies")
            ret = self.login()
            if ret.get("status") == "success":
                return ret.get("data")
            else:
                return {}

    def get_courses(self, old, raw):
        """
        读取用户的所有课程信息
        :param old: 是否读取本地文件
        :param raw: 是否返回原始数据
        :return: 返回课程信息数据(原始raw|精简not raw)
        """
        courses = []
        # 是否读取本地文件(old=True|False)
        if old:
            self.logger.info("old读取模式(Courses)")
            if exists(f"Saves/{self.usernm}/courses.cx"):
                # 本地是否存在courses.cx课程文件
                with open(f"Saves/{self.usernm}/courses.cx", "r") as f:
                    self.logger.info("Courses文件存在且可用，正在读取")
                    courses_raw = json.loads(f.read())
                    # 是否返回原始数据(raw=True|False)
                    if raw:
                        # 返回原始数据
                        return ret_msg("success", courses_raw)
                    else:
                        # 读取原始数据里的每一个课程字典
                        for item in courses_raw:
                            # 判断课程是否为学习课程(异常课程字典中不存在state键)
                            if "state" in item["content"]:
                                dic = {}
                                dic['id'] = item['content']['course']['data'][0]['id']
                                dic['name'] = item['content']['course']['data'][0]['name']
                                if item["content"]["state"] == 0:
                                    dic['state'] = "开课"
                                else:
                                    dic['state'] = "结课"
                                if exists(f"Saves/{self.usernm}/{item['content']['course']['data'][0]['id']}"):
                                    dic['exists'] = "存在"
                                else:
                                    dic['exists'] = "不存在"
                                courses.append(dic)
                                self.logger.debug(f"课程识别正常:{dic}")
                                # 返回精简数据
                                return ret_msg("success", courses)
            else:
                self.logger.info("Courses文件不存在，正在在线读取")
        else:
            self.logger.info(f"非old读取模式(Courses)")
            self.logger.info("开始在线读取Courses")
        # 调用Cookies函数
        cookies = self.load_cookies()
        # 判断cookies数据是否正常
        if cookies:
            self.logger.info("开始读取用户的所有课程")
            # 发送读取课程信息请求
            resp = requests.get("http://mooc1-api.chaoxing.com/mycourse?rss=1&mcode=", headers={
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/96.0.4664.93 Safari/537.36",
                "cookie": cookies})
            self.logger.debug("Response接收正常")
            # 判断返回值是否为JSON格式
            try:
                resp.json()
            except json.decoder.JSONDecodeError:
                self.logger.error("Response内容异常，出现JSONDecodeError错误，请检查您的网络情况。若无法解决，请在GitHub页面提交截图Issue")
                self.logger.error("相关日志:")
                self.logger.error("url=http://mooc1-api.chaoxing.com/mycourse?rss=1&mcode=")
                self.logger.error(f"resp={resp.content.decode('utf8')}")
                # 返回错误信息
                return ret_msg("fail", "Response出现JSONDecodeError错误，请检查日志")
            self.logger.debug("JSON读取正常")
            channelList = resp.json().get('channelList')
            # 写入本地课程Courses文件
            with open(f"Saves/{self.usernm}/courses.cx", 'w') as f:
                json.dump(channelList, f)
                self.logger.debug(f"写入文件正常:Saves/{self.usernm}/courses.cx")
            # 是否返回原始数据(raw=True|False)
            if raw:
                self.logger.info("在线Courses课程读取完毕")
                return ret_msg("success", channelList)
            else:
                # 读取原始数据里的每一个课程字典
                for item in channelList:
                    # 判断课程是否为学习课程(异常课程字典中不存在state键)
                    if "state" in item["content"]:
                        dic = {}
                        dic['id'] = item['content']['course']['data'][0]['id']
                        dic['name'] = item['content']['course']['data'][0]['name']
                        if item["content"]["state"] == 0:
                            dic['state'] = "开课"
                        else:
                            dic['state'] = "结课"
                        if exists(f"Saves/{self.usernm}/{item['content']['course']['data'][0]['id']}"):
                            dic['exists'] = "存在"
                        else:
                            dic['exists'] = "不存在"
                        courses.append(dic)
                        self.logger.debug(f"课程识别正常:{dic}")
                self.logger.info("在线Courses课程读取完毕")
                return ret_msg("success", courses)
        else:
            self.logger.error("Cookies数据出现异常，请删除本地Saves文件夹后重试")
            return ret_msg("fail", "Cookies数据出现异常，请删除本地Saves文件夹后重试")

    def find_course(self, courseid, course_detail):
        """
        根据提供的courses原始数据搜索courseid得到对应的课程原始信息
        :param courseid: 课程id
        :param course_detail: 所有课程的原始数据
        :return:
        """
        for course in course_detail:
            if "state" in course["content"]:
                if str(course['content']['course']['data'][0]['id']) == str(courseid):
                    self.logger.error("已找到课程")
                    return ret_msg("success", course)
        self.logger.error("未找到相关的课程id，请仔细检查后重试")
        return ret_msg("fail", "未找到相关的课程id，请仔细检查后重试")


class Course:
    def __init__(self, user, courseid, course_detail):
        self.logger = Logger("Logs/ClassCourse.log")
        self.logger.info("正在初始化Course对象")
        self.courseid = courseid
        self.user = user
        self.userid = self.user.userid
        self.course_detail = course_detail
        self.clazzid = course_detail['content']['id']
        self.cpi = course_detail['cpi']
        self.logger.info("初始化完毕")

    def load_chapter_id(self):
        # TODO 正在进行的任务:修改Headers适配接口
        s = requests.session()
        s.headers['User-Agent'] = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/96.0.4664.93 Safari/537.36"
        s.headers['cookie'] = self.user.load_cookies()
        resp = s.get("https://mooc1-1.chaoxing.com/")
        print(resp.text)
        input()
        course_path = 'Saves/{}/{}'.format(self.user.usernm, self.courseid)
        check_path(course_path)
        self.logger.info("正在请求读取课程章节信息")
        url = 'https://mooc1-1.chaoxing.com/visit/stucoursemiddle?courseid=' + str(
            self.courseid) + '&clazzid=' + str(self.clazzid) + '&vc=1&cpi=' + str(self.cpi)
        resp = s.get(url)
        content = resp.text
        print(content)
        input()
        self.chapterids = []
        for chapter in re.findall('\?chapterId=(.*?)&', content):
            self.chapterids.append(str(chapter))
        with open(f"{course_path}/chapterid.cx") as f:
            json.dump(self.chapterids,f)
        self.enc = re.findall("&clazzid=.*?&enc=(.*?)'", content)[0]
        with open(f"{course_path}/course.cx") as f:
            json.dump(self.course_detail,f)



usernm = "12312412"
passwd = "63246234"
courseid = '212372243'

def run():
    user = User(usernm,passwd)
    courses = user.get_courses(old=False, raw=True)
    if courses.get("status") == "success":
        course_detail = user.find_course(courseid, courses.get("data"))
        if course_detail.get("status") == "success":
            course = Course(user, courseid, course_detail.get("data"))
            course.load_chapter_id()


if __name__ == '__main__':
    run()

