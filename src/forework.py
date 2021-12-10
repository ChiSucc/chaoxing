import json
import re
import requests
from os.path import exists

import requests.utils

headers = {
    'User-Agent':'Dalvik/2.1.0 (Linux; U; Android 5.1.1; SM-G9350 Build/LMY48Z) com.chaoxing.mobile/ChaoXingStudy_3_5.21_android_phone_206_1 (SM-G9350; Android 5.1.1; zh_CN)_1969814533'
}


def find_objectives(usernm, chapterids, course_id, cookies):
    """
    在用户选择的课程中获取所有的任务点
    :param usernm: 用户名
    :param chapterids: 章节编号
    :param course_id: 课程编号
    :param session: requests.session()
    :return:
    """
    jobs = {}
    for lesson_id in chapterids:
        url = 'http://mooc1-api.chaoxing.com/gas/knowledge?id=' + str(lesson_id) + '&courseid=' + str(
            course_id) + '&fields=begintime,clickcount,createtime,description,indexorder,jobUnfinishedCount,jobcount,' \
                         'jobfinishcount,label,lastmodifytime,layer,listPosition,name,openlock,parentnodeid,status,' \
                         'id,card.fields(cardIndex,cardorder,description,knowledgeTitile,knowledgeid,theme,title,' \
                         'id).contentcard(all)&view=json '
        resp = requests.get(url,headers=headers,cookies=cookies)
        try:
            content = str(json.loads(resp.text)['data'][0]['card']['data']).replace('&quot;', '')
            result = re.findall('[{,]objectid:(.*?)[},].*?[{,]_jobid:(.*?)[},]', content)
            jobs[lesson_id] = result
        except Exception as e:
            pass
    course_path = 'saves/{}/{}'.format(usernm, course_id)
    with open('{}/jobsinfo.json'.format(course_path), 'w') as f:
        json.dump(jobs, f)
    return jobs


def detect_job_type(jobs, usernm, course_id, cookies):
    """
    识别任务点的类型(mp4/ppt)
    :param jobs: 任务点信息
    :param usernm: 用户名
    :param course_id: 课程编号
    :return:
    """
    mp4 = {}
    ppt = {}
    for chapter in jobs:
        for item in jobs[chapter]:
            url = 'https://mooc1-api.chaoxing.com/ananas/status/' + item[0]
            header = {
                'Host': 'mooc1-api.chaoxing.com',
                'Connection': 'keep-alive',
                'User-Agent': 'Dalvik/2.1.0 (Linux; U; Android 5.1.1; SM-G9350 Build/LMY48Z) '
                              'com.chaoxing.mobile/ChaoXingStudy_3_5.21_android_phone_206_1 (SM-G9350; Android 5.1.1; '
                              'zh_CN)_19698145335.21',
                'Accept': '*/*',
                'Accept-Encoding': 'gzip, deflate',
                'Accept-Language': 'zh-CN,en-US;q=0.8',
            }
            resp = requests.get(url, headers=header, cookies=cookies)
            result = resp.json()
            rtn = job_type(chapter, item, result)
            if rtn['type'] == 'mp4':
                mp4[item[0]] = rtn['detail']
            elif rtn['type'] == 'ppt':
                ppt[item[0]] = rtn['detail']
            else:
                pass
    # console.log('共加载任务点[yellow]{}[/yellow]个'.format(len(mp4) + len(ppt)))
    course_path = 'saves/{}/{}'.format(usernm, course_id)
    with open('{}/mp4info.json'.format(course_path), 'w') as f:
        json.dump(mp4, f)
    with open('{}/pptinfo.json'.format(course_path), 'w') as f:
        json.dump(ppt, f)
    return mp4, ppt


def job_type(chapter, item, content):
    """
    获取任务点信息
    :param chapter: 章节编号
    :param item: 任务点名
    :param content: 任务点信息
    :return:
    """
    try:
        filename = content['filename']
        if 'mp4' in filename:
            object_mp4 = []
            object_mp4.append(content['filename'])
            object_mp4.append(content['dtoken'])
            object_mp4.append(content['duration'])
            object_mp4.append(content['crc'])
            object_mp4.append(content['key'])
            object_mp4.append(item)
            object_mp4.append(chapter)
            # mp4[item[0]] = object_mp4
            return {'type': 'mp4', 'detail': object_mp4}
        elif 'ppt' in filename:
            object_ppt = []
            object_ppt.append(content['crc'])
            object_ppt.append(content['key'])
            object_ppt.append(content['filename'])
            object_ppt.append(content['pagenum'])
            object_ppt.append(item)
            object_ppt.append(chapter)
            # ppt[item[0]] = object_ppt
            return {'type': 'ppt', 'detail': object_ppt}
        else:
            return {'type': 'none'}
    except Exception as e:
        return {'type': 'none'}

def get_openc(usernm, course, cookies):
    """
    获取超星的openc加密密文
    :param usernm: 用户名
    :param course: 课程信息
    :param session: requests.session()
    :return:
    """
    url = 'https://mooc1-1.chaoxing.com/visit/stucoursemiddle?courseid={}&clazzid={}&vc=1&cpi={}'.format(
        course['courseid'], course['clazzid'], course['cpi'])
    resp = requests.get(url,headers=headers,cookies=cookies)
    try:
        course['openc'] = re.findall("openc : '(.*?)'", resp.text)[0]
    except Exception:
        course['openc'] = re.findall('&openc=(.*?)"', resp.text)[0]
    course_path = 'saves/{}/{}'.format(usernm, course['courseid'])
    with open('{}/courseinfo.json'.format(course_path), 'w') as f:
        json.dump(course, f)
    return course