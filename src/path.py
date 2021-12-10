# -*- coding:utf-8 -*-
from os.path import exists, join, isfile
from os import mkdir, listdir, remove, rmdir



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
        if isfile(file_data):  # os.path.isfile判断是否为文件,如果是文件,就删除.如果是文件夹.递归给del_file.
            remove(file_data)
        else:
            delete_path(file_data)
    rmdir(path)