import requests
import requests.utils
from base64 import b64encode
import json
import src.path as path
import src.log as log


class User:
    def __init__(self, usernm, passwd):
        self.usernm = str(usernm)
        self.passwd = str(passwd)
        self.logger = log.Logger("logs/{}.txt".format(usernm))

    def verify(self,further=False):
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
                cookie = requests.utils.dict_from_cookiejar(resp.cookies)
                user['usernm'] = self.usernm
                user['passwd'] = self.passwd
                user['userid'] = cookie['_uid']
                user['fid'] = cookie['fid']
                self.logger.debug("正在写入本地文件")
                path.check_file('saves/{}/userinfo.json'.format(self.usernm))
                with open('saves/{}/userinfo.json'.format(self.usernm), 'w') as f:
                    json.dump(user, f)
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
    def login(self):
        ret = self.verify(further=True)
        if ret.get('code') == 1:
            s = ret.get('session')

        else:
            return ret

