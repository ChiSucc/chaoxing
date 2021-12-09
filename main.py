import requests
from base64 import b64encode
import json

import src.log as log


class User:
    def __init__(self, usernm, passwd):
        self.usernm = str(usernm)
        self.passwd = str(passwd)
        self.logger = log.Logger("logs/{}.txt".format(usernm))

    def verify(self):
        url = 'https://passport2-api.chaoxing.com/fanyalogin'
        headers = {
            'User-Agent': 'Dalvik/2.1.0 (Linux; U; Android 5.1.1; SM-G9350 Build/LMY48Z) com.chaoxing.mobile/ChaoXingStudy_3_5.21_android_phone_206_1 (SM-G9350; Android 5.1.1; zh_CN)_19698145335.21',
            'X-Requested-With': 'XMLHttpRequest'
        }
        data = {
            'fid': '-1',
            'uname': str(self.usernm),
            'password': b64encode(self.passwd.encode('utf8')),
            'refer': 'http%3A%2F%2Fi.mooc.chaoxing.com',
            't': 'true',
            'forbidotherlogin': '0',
        }
        self.logger.info("正在尝试登录账号: {}".format(self.usernm))
        resp = requests.post(url, data=data)
        try:
            if resp.status_code == 200 and resp.json().get('status') == True:
                self.logger.info("登录成功，账户: {}验证完毕".format(self.usernm))
                return {'code':'1'}
            else:
                self.logger.error("登录失败，账户: {}账号或密码不正确".format(self.usernm))
                return {'code':'-1'}
        except json.decoder.JSONDecodeError as e:
            self.logger.debug(resp.text)
            self.logger.critical("登录失败，请求获取的结果非JSON，已在日志中输出请求结果")
            self.logger.critical("请查看日志文件")
            return {'code':'-2'}

    def get_info(self):
        pass

        # if resp.status_code == 200:
        #     if resp.json()['status']:
        #         console.log("[yellow]登录成功[/yellow]")
        #         pathCheck.check_file('saves/{}/userinfo.json'.format(usernm))
        #         cookie = requests.utils.dict_from_cookiejar(resp.cookies)
        #         user['usernm'] = usernm
        #         user['passwd'] = passwd
        #         user['userid'] = cookie['_uid']
        #         user['fid'] = cookie['fid']
        #         console.log("正在[red]本地[/red]保存账户信息")
        #         with open('saves/{}/userinfo.json'.format(usernm), 'w') as f:
        #             json.dump(user, f)
        #         console.log("[yellow]账户信息[/yellow]保存成功")
        #     else:
        #         console.input("[red]登录失败[/red],请检查你的[red]账号密码[/red]是否正确,按回车键退出")
        #         # print('登录失败，请检查你的账号密码,按回车键退出')
        #         exit()
        # else:
        #     console.log("登录失败，登录返回状态码[red]{}[/red]".format(resp.status_code))
        #     console.log("返回内容：\n")
        #     console.log(resp.text)
        #     console.input("请在仓库Issue页面提出反馈，按回车键退出")
        #     exit()
        # return session
