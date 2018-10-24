# !usr/bin/env python3.6  
# -*- coding: utf-8 -*-
# Author:lei.tang

import datetime
import logging
import shutil
import os
import paramiko
import pysftp
from git import *

logging.basicConfig(filename='upload.log', level=logging.INFO, filemode='a',
                    format='%(asctime)s - %(filename)s[line:%(lineno)d] - %(levelname)s: %(message)s')


def update(origin_path):

    try:
        global data
        dir = os.chdir(os.path.join(origin_path, 'CloudOptimus'))
        data = Git().execute("git pull")
    except Exception as e:
        os.chdir(origin_path)
        data = Git().execute("git clone http://git.tongfudun.com/jie.shen/CloudOptimus.git")
    finally:
        print(data)


def backup(origin_path, target_path):
    shutil.rmtree(target_path)
    shutil.copytree(origin_path, target_path, ignore=shutil.ignore_patterns('*.git*'))


def repalce_file(target_path):
    for file in os.listdir(target_path):
        file = os.path.join(target_path, file)
        if os.path.isdir(file):
            change_file = "change_env.py"
            config_file = "config.py"
            src_change = os.path.join(os.path.dirname(target_path), change_file)
            dst_change = os.path.join(file, change_file)
            # src_config=os.path.join(os.path.dirname(target_path),config_file)
            dst_config = os.path.join(file, "app", config_file)
            if os.path.exists(dst_config):
                # os.remove(dst_config)
                shutil.copy(src_change, dst_change)
            #     shutil.copy(src_config, dst_config)


class Remote_Put:

    def __init__(self, hostname, username, password, port, local_dir, remote_dir, path, command):
        self.hostname = hostname
        self.username = username
        self.password = password
        self.port = port
        self.local_dir = local_dir
        self.remote_dir = remote_dir
        self.list_dir = []
        self.list_file = []
        self.list_unknown = []
        self.dir_list = []
        self.path = path
        self.command = command

    def treedir(self, dir):
        self.list_dir.append(dir)

    def treefile(self, file):
        self.list_file.append(file)

    def treeunknown(self, arg):
        self.list_unknown.append(arg)

    def upload(self):
        try:
            t = paramiko.Transport((self.hostname, self.port))
            t.connect(username=self.username, password=self.password)
            sftp = paramiko.SFTPClient.from_transport(t)
            print('upload file start %s ' % datetime.datetime.now())
            cnopts = pysftp.CnOpts()
            cnopts.hostkeys = None
            sftpp = pysftp.Connection(self.hostname, username=self.username, password=self.password, port=self.port,
                                      cnopts=cnopts)
            # 操作目标目录,判断目录是否已存在
            if sftpp.exists(self.remote_dir):
                sftpp.walktree(self.remote_dir, self.treefile, self.treedir, self.treeunknown)
                # 先删除已存在的文件,后删除存在的文件夹
                if self.list_file != []:
                    for i in self.list_file:
                        sftpp.remove(i)
                # 先删除子文件夹后删除主文件夹
                if self.list_dir != []:
                    for i in self.list_dir:
                        if sftpp.listdir_attr(i) != []:
                            self.dir_list.insert(-1, i)
                        else:
                            self.dir_list.insert(0, i)
                    for i in self.dir_list:
                        sftpp.rmdir(i)
            else:
                pass
            # 遍历本地文件,然后上传到远程server
            for root, dirs, files in os.walk(self.local_dir):
                for filespath in files:
                    local_file = os.path.join(root, filespath)
                    logging.info(','.join(('11', '[%s][%s][%s][%s]' % (root, filespath, local_file, self.local_dir))))
                    remote_file = local_file.replace(self.local_dir, self.remote_dir).replace("\\", "/")
                    try:
                        sftp.put(local_file, remote_file)
                    except Exception as e:
                        logging.info(os.path.split(remote_file)[0])
                        if not sftpp.exists(os.path.split(remote_file)[0]):
                            sftp.mkdir(os.path.split(remote_file)[0])
                        sftp.put(local_file, remote_file)
                    logging.info("66 upload %s to remote %s" % (local_file, remote_file))
            print('77,upload file success %s ' % datetime.datetime.now())
            sftpp.close()
            t.close()
        except Exception as e:
            print(88, e)

    def execute(self):
        client = paramiko.SSHClient()
        client.set_missing_host_key_policy(paramiko.AutoAddPolicy())  # 设置自动添加和保存目标ssh服务器的ssh密钥
        client.connect(self.hostname, self.port, username=self.username, password=self.password)  # 连接

        stdin, stdout, stderr = client.exec_command(self.command)
        for i in stdout.readlines():
            print(i.rstrip('\n'))
        for i in stderr.readlines():
            print(i.rstrip("\n"))
        client.close()


if __name__ == '__main__':
    origin_path = r"E:\github"
    target_path = r"E:\CloudOptimus_backup\CloudOptimus"
    # hostname=''
    # username='root'
    # password=''                                                                                                                                                                                              io'
    port = 22
    local_dir = r'E:\CloudOptimus_backup\CloudOptimus\agent-api'  # 本地需要上传的文件所处的目录
    remote_dir = '/root/nginx/agent-api_1.0/agent-api_1.0/'  # linux下目录
    path = ''
    command = "python3.6 /root/nginx/dist.py"
    update(origin_path)
    # time.sleep(1)
    # backup(origin_path,target_path)
    # time.sleep(1)
    # repalce_file(target_path)
    # remote=Remote(hostname,username,password,port,local_dir,remote_dir,path,command)
    # remote.upload()
    # remote.execute()
