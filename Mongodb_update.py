import pymongo
from pymongo import MongoClient
import os

class MongoDB(object):

    def __init__(self, MONGO):
        self.MONGODB = MONGO

    def __enter__(self):
        self.client = MongoClient(
            'mongodb://{}:{}@{}/{}'.format(self.MONGODB['user'],
                                           self.MONGODB['passwd'],
                                           self.MONGODB['host'],
                                           self.MONGODB['dbname']),
            connect=False)
        return self.client[self.MONGODB['dbname']]

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.client.close()


class TestingConfig:
    MONGODB = {
        "user": "CloudOptimus_QA",
        "passwd": "nkiDy8fm7X7N",
        "host": "192.168.118.108:27017",
        "dbname": "CloudOptimus_QA"
    }
    MYSQL = {
        "user": "CloudOptimus_QA",
        "passwd": "Hc62@df26d",
        "host": "192.168.118.150:3306",
        "dbname": "CloudOptimus_QA"
    }

class Modify:

    def __init__(self,MONGO):
        with MongoDB(MONGO) as db:
            self.db=db

    def remove_collections(self):
        for i in self.db.list_collections():
            if i['name'] in ('GPL', 'agent', 'cfg', 'system.indexes'):
                continue
            else:
                self.db.get_collection(i['name']).remove()
                print('{} collection is removed already ...'.format(i['name']))

    def query_data(self,collection,head='_id'):
        list_collection = [i['name'] for i in self.db.list_collections()]
        file_set=set()
        if len(list_collection)==0:
            print("The collection is null .")
        elif collection not in list_collection :
            print('The collection not exists . ')
        else:
            with open('%s.csv'%collection,'w',encoding='utf-8') as f:
                for i in self.db.get_collection(collection).find().sort([(head,pymongo.ASCENDING)]):#{'token':'c95508d4bec46b267e5b8c2dd59a6424'}
                    if collection in ("fileupload",'webshell'):
                        file_set.add(i['file'])
                    f.write(''.join((str(i),'\n')))

        print(len(file_set))

    def query_count(self):
        for i in self.db.list_collections():
            print(i['name'],self.db.get_collection(i['name']).find().count())


    def token_distri(self,token):
        with open('%s.csv' % token, 'w', encoding='utf-8') as f:
            for i in self.db.list_collections():
                for j in self.db.get_collection(i['name']).find({'token':token}):
                    f.write(''.join((str(i),'\t',str(j),'\n')))


class Score:

    def __init__(self,num,depth):
        self.a = 1
        self.b = 1
        self.num = num
        self.depth = depth

    def depth_score(self):
        if type(self.num) is not int or type(self.depth) is not int:
            print("The data form input is not int type ....")
        else:
            if self.depth == 0:
                return 100
            elif self.depth == 1:
                return 100- self.num*self.a
            else:
                for i in range(2,self.depth+1):
                    self.a = self.a/2
                    self.b=self.b +self.a
                return 100 - self.num*self.b


if __name__ == '__main__':
    cfg = TestingConfig()
    mongo = Modify(cfg.MONGODB)
    mongo.remove_collections()
    mongo.query_data("webshell",'file')
    mongo.query_count()
    score = Score(20,38)
    print(score.depth_score())
    token='5ae22e9b70c2c321569a84bf30f53e9a'
    mongo.token_distri(token)




