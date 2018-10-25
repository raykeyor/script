import os
import re
import shutil
import subprocess
import time
import traceback
import configparser


# build the docker images with dockerfile
def built_docker(path, docker_name, tag, docker_file, env):
    args=True
    if os.path.exists(path):
        os.chdir(path)
    else:
        print(path," not exists...")
    
    if 'portscan' in docker_name:
        command_built = 'docker build -t {0}:{1} -f {2} .'.format(
            docker_name, tag, docker_file)
    else:
        command_built = 'docker build -t {0}:{1} -f {2} --build-arg env={3} .'.format(
            docker_name, tag, docker_file, env)

    res = os.system(command_built)
    if res != 0:
        args=False

    return args

# get the docker images from repository
def get_docker_img(command):
    docker_img = []
    child = subprocess.Popen(command, stdout=subprocess.PIPE,shell=True)
    string = child.stdout.read().decode()
    print(string)
    string_1 = string.split("\n")
    for i in string_1:
        string_2 = re.sub(r" {2,}", ',', i)
        if not i:
            continue
        else:
            docker_img.append(string_2)
    return docker_img


# get the image id  which you want to use
def get_docker_id(repo, tag, docker_img, index):
    for i in docker_img:
        if repo == i.split(',')[0] and tag == i.split(',')[1]:
            print("Search completely,the result is : %s" %
                  (i.split(',')[index]))
            return i.split(',')[index]
        else:
            continue
    else:
        print("Search completely,cannot find the result . ")


# get the container id which is alive
def get_container_id(container_list, index):
    container_id_list = []
    if len(container_list) > 1:
        for i in container_list[1:]:
            container_id_list.append(i.split(",")[index])
            print("Search completely,the result is : %s" %
                  (i.split(",")[index]))
        return container_id_list
    else:
        print("Search completely, no container id is alive . ")


# stop and remove all the container id which is alive
def remove_container(list_contain):
    if list_contain is None:
        print('The container is blank . ')
    else:
        if len(list_contain) == 1:
            command = 'docker stop %s' % (list_contain[0])
            command_rm = 'docker rm %s' % (list_contain[0])
        else:
            string = ' '.join(list_contain)
            command = 'docker stop %s' % (string)
            command_rm = 'docker rm %s' % (string)
        os.system(command)
        os.system(command_rm)
 
        print("The container was removed")


# run the docker iamge
def run_docker(docker_name, docker_id,port1= None,port2=None):
    try:
        if 'engine' in docker_name:
            command = 'docker run --name {0} -v /d/Logs/engine:/opt/engine/logs {1}'.format(docker_name,docker_id)
        elif 'portscan' in docker_name:
            command = 'docker run --name {0} -v /d/Logs/portscan:/opt/portscan/logs {1}'.format(docker_name,docker_id)    
        elif 'audit' in docker_name:
            command = 'docker run --name {0} -p 0.0.0.0:{1}:{2} -v /d/Logs/auditplatform:/opt/auditplatform/logs {3}'.format(docker_name,port1,port2,docker_id)
        elif 'backend' in docker_name:
            command = 'docker run --name {0} -p 0.0.0.0:{1}:{2} -v /d/Logs/backend:/opt/backend/logs {3}'.format(docker_name,port1,port2,docker_id)
        elif 'threat' in docker_name:
            command = 'docker run --name {0} -p 0.0.0.0:{1}:{2} -v /d/Logs/threat-analysis:/opt/threat-analysis/logs {3}'.format(docker_name,port1,port2,docker_id)
        elif 'agentapi' in docker_name:
            command = 'docker run --name {0} -p 0.0.0.0:{1}:{2} -v /d/Logs/agent-api:/opt/agent-api/logs {3}'.format(docker_name,port1,port2,docker_id)    
        elif 'webapi' in docker_name:
            command = 'docker run --name {0} -p 0.0.0.0:{1}:{2} -v /d/Logs/web-api:/opt/web-api/logs {3}'.format(docker_name,port1,port2,docker_id)
        else:
            print("The docker name is incorrect , please try again ...")
    except Exception as e:
        print(e)
    else:                                                                                                 
        try:
            os.system(command)
        except Exception as e:
            print(e)



# delete the image which tage is None
def del_tag_None(docker_img):
    for i in docker_img:
        if i.split(',')[1] == '<none>':
            print(i.split(',')[2])
            command = "docker rmi %s" % (i.split(',')[2])
            os.system(command)
        else:
            continue
    print("No Image with tag is None .")


# distribute the docker to aliyun
def dist_aliyun(path, docker_name, tag, docker_file):
    # log in the docker for aliyun
    command_login = "docker login --password=******* --username=******** registry.cn-shanghai.aliyuncs.com"
    os.system(command_login)

    # dist in the local
    os.chdir(path)
    command_dist = "docker build -t {0}:{1} -f {2}  --build-arg env=prod .".format(
        docker_name, tag, docker_file)
    os.system(command_dist)

    # push the docker to aliyun
    command_send = "docker push {0}:{1}".format(docker_name, tag)
    num=os.system(command_send)
    if num !=0:
        print("The processing is end with error ,please check it ....")
    else:
        print("The docker has been sent to aliyun already .")


# This is the entrance function
def run(arg):
    if arg == 0:
        # built the docker
        args = built_docker(path, docker_name, tag, docker_file, env)
        return args


    elif arg == 1:
        # query the latest image for  building
        docker_img = get_docker_img(command_image)
        docker_id = get_docker_id(docker_name, tag, docker_img, 2)

    elif arg == 2:
        # run the docker
        # run_docker(docker_new_name,get_docker_id(docker_name,tag,get_docker_img(command_image),2))
        run_docker(docker_new_name, get_docker_id(
            docker_name, tag, get_docker_img(command_image), 2),port1,port2)

    elif arg == 3:
        # stop and remove container for docker
        stop_id = get_docker_img(stop_ps)
        container_id = get_container_id(stop_id, 0)
        remove_container(container_id)

    elif arg == 4:
        # rm the tag is None
        del_tag_None(get_docker_img(command_image))

    elif arg == 5:
        # distribute the docker to aliyun
        dist_aliyun(path, docker_name, tag, docker_file)

    else:
        print("The args is wrong ,please input the correct one !!!!")


# run the function
def main(num=1):
    while True:
        num=num
        argu = True
        try:
            if type(num) is int:
                num=int(num)
            else:
                print("The type for num is incorrect .")
                break
            if num == 0:
                argu = run(num)
            else:
                run(num)
        except Exception as e:
            print(e)
        finally:
            if argu == True :
                break
            else:
                time.sleep(5)
                pass
        


def getConfig(base_path,config_name, section, option):
    config=configparser.ConfigParser()
    path = os.path.join(base_path,config_name)
    config.read(path)
    return config.get(section, option)
   


if __name__ == '__main__':
    # 参数准备
    base_path =os.path.dirname(os.path.realpath(__file__))
    config_name='config.conf'
    env = getConfig(base_path,config_name,'env','env')
    task = getConfig(base_path,config_name,'task','task')

    if task not in ['backend','engine','audit','portscan','threat-analysis','agent-api','web-api'] :
        print("The process end with error task name ....")
    else:
        # task details:
        folder_name =getConfig(base_path,config_name,task,'folder_name')
        tag = getConfig(base_path,config_name,task,'tag')
        docker_new_name = getConfig(base_path,config_name,task,'docker_new_name')
        docker_name = getConfig(base_path,config_name,task,'docker_name')
        docker_file = getConfig(base_path,config_name,task,'docker_file')
        if task == 'engine' or  task == 'portscan' :
            port1 = port2 =None
        else:  
            port1=int(getConfig(base_path,config_name,task,'port1'))
            port2=int(getConfig(base_path,config_name,task,'port2'))


        # fixed command 
        command_image = "docker images"
        stop_ps = "docker ps -a"
        path = os.path.join(base_path, folder_name)

        # dist type
        args = int(getConfig(base_path,config_name,'aliyuncs','id'))
        name = getConfig(base_path,config_name,'aliyuncs','name')
        if args == 1:
            docker_name = docker_name
        elif args == 2:
            docker_name = 'registry.cn-shanghai.aliyuncs.com/***/{}'.format(name)
        else:
            print("The docker name is wrong ,please input the correct docker name !!!!")


        num = getConfig(base_path,config_name,'typeID','id')
        main(int(num))
