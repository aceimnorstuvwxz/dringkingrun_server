import tornado.ioloop
import tornado.web
from db import Dmdb
from Crypto.Cipher import AES
import base64
import json
import random
import hashlib
import urllib

MDB = Dmdb()
token_map = {}
random.seed()


class MainHandler(tornado.web.RequestHandler):
    def get(self):
        self.write("hello world")
        
class TRBaseHandler(tornado.web.RequestHandler):
    def tr_read(self):
        b64 = self.get_argument("p", "")
        b64 = urllib.unquote_plus(b64)
        obj = AES.new('01234567890123456789012345678901', AES.MODE_CBC, '0123456789012345')
        enc = base64.decodestring(b64)
        dst = obj.decrypt(enc)
        print "Base read", dst
        return dst
        
    def tr_write(self, data):
        if len(data)%16 != 0 :
            data += (16 - len(data)%16)*' '
        obj = AES.new('01234567890123456789012345678901', AES.MODE_CBC, '0123456789012345')
        enc = obj.encrypt(data)
        b64 = base64.encodestring(enc)
        b64 = urllib.quote_plus(b64)
        self.write(b64)
        print "Base write", data

    def tr_error(self, error_code, error_msg):
        jstr = '''{"err_code":%s,"err_msg":"%s"}''' % (error_code, error_msg)
        self.tr_write(jstr)
        
def trmd5(data):
    m5 = hashlib.md5()
    m5.update(data)
    return m5.hexdigest()

class NewAcctHandler(TRBaseHandler):
    def post(self):
        data = self.tr_read()
        jobj = json.loads(data)
        id_string = jobj["id_string"]
        print "incomming id_string = ", id_string
        if MDB.isIdStringExist(id_string):
            self.tr_error(1, "id_string exists")
            return
        else:
            passinter = id_string
            passinter = passinter + str(random.randint(100,1000))
            pwd = trmd5(passinter)[:16]
            print passinter, pwd

            dict = {}
            dict["id_string"] = id_string
            dict["name"] = id_string
            dict["image"] = ""
            dict["score"] = 0
            dict["gold"] = 0
            dict["config"] = "{}"
            dict["cost_rmb"] = 0
            dict["pass_md5"] = pwd 
            if MDB.insert(dict):
                id = MDB.getByIdstring(id_string)["id"]
                ret = '''{"id":%s, "pwd":"%s", "err_code":0}''' % (id, pwd)
                self.tr_write(ret)
                return
            else:
                self.tr_error(2, "internal error 001")
                return

def genToken():
    raw = "raw"
    for i in xrange(10):
        raw += str(random.randint(100,999))
    token = trmd5(raw)[:32]
    return token

def genInitSN():
    return random.randint(0,999)
    
def genNextSN(old):
    newSn = old+1
    if newSn >= 10000:
        newSn = 0
    return newSn

class LoginHandler(TRBaseHandler):
    def post(self):
        data = self.tr_read()
        jobj = json.loads(data)
        id = jobj["id"]
        pwd = jobj["pwd"]
        record = MDB.getById(id) 
        if record != None and record["pass_md5"] == pwd:
            tk = genToken()
            sn = genInitSN()
            token_map[id] = (tk, sn)
            ret = '''{"tk":"%s", "sn":%s, "err_code":0}''' % (tk, sn)
            self.tr_write(ret)
        else:
            self.tr_error(3, "account error")
        
def checkAuth(id, tk, sn):
    tp = token_map[id]
    tp[1] = genNextSN(tp[1])
    token_map[id] = tp
    #todo check auth
    return True

class GetScoreHandler(TRBaseHandler):
    def post(self):
        try:
            data = self.tr_read()
            jobj = json.loads(data)
            print jobj
            targetId = jobj["target"]
            record = MDB.getById(targetId)
            if record != None:
                targetScore = record["score"]
                ret = '''{"target":%s, "score":%s, "err_code":0}''' % (targetId, targetScore)
                self.tr_write(ret)
            else:
                self.tr_error(4, "get score fail")
        except KeyError:
            self.tr_error(2, "internal error")

class UpdateScoreHandler(TRBaseHandler):
    def post(self):
        data = self.tr_read()
        jobj = json.loads(data)
        '''todo, auth check'''
        newScore = jobj["score"]
        id = jobj["id"]
        record = MDB.getById(id)
        if record != None:
            isNew = record["score"] < newScore
            if isNew:
                record["score"] = newScore
                MDB.update(record)
                isNew = 1
            else:
                isNew = 0
            ret = '''{"is_new":%s, "err_code":0}''' % (isNew)
            self.tr_write(ret)
        else:
            self.tr_error(5, "db has no record of id %s"%id)

class GetImageHandler(TRBaseHandler):
    def post(self):
        #TODO cau
        data = self.tr_read()
        jobj = json.loads(data)
        targetId = jobj["target"]
        record = MDB.getById(targetId)
        if record != None:
            ret = '''{"img":"%s", "err_code":0}''' % (record["image"],)
            self.tr_write(ret)
        else:
            self.tr_error(6, "no id")
        
class UploadImageHandler(TRBaseHandler):
    def post(self):
        #todo cau
        data = self.tr_read()
        jobj = json.loads(data)
        image = jobj["image"]
        id = jobj["id"]
        record = MDB.getById(id)
        record["image"] = image
        MDB.update(record)
        ret = '''{"err_code":0}'''
        self.tr_write(ret)
        
class GetDataHandler(TRBaseHandler):
    def post(self):
        data = self.tr_read()
        jobjs = json.loads(data)
        record = MDB.getById(jobjs["id"])
        record["err_code"] = 0
        del record["pass_md5"]
        ret = json.dumps(record)
        self.tr_write(ret)
        
def recordList2jsonRet(list):
    dpr = []
    for r in list:
        d = {}
        d["id"] = r["id"]
        d["score"] = r["score"]
        d["image"] = r["image"]
        dpr.append(d)
    retd = {}
    retd["err_code"] = 0
    retd["data"] = dpr
    ret = json.dumps(retd)
    return ret    

class GetTop3(TRBaseHandler):
    def post(self):
        data = self.tr_read()
        #cau
        list = MDB.getTopScore3()
        ret = recordList2jsonRet(list)
        self.tr_write(ret)

class GetNear6ByScore(TRBaseHandler):        
    def post(self):
        data = self.tr_read()
        #cau
        jobj = json.loads(data)
        score = jobj["score"]
        list = MDB.getNear6ByScore(score)
        ret = recordList2jsonRet(list)
        self.tr_write(ret)

application = tornado.web.Application([
    (r"/", MainHandler),
    (r"/newAccount", NewAcctHandler),
    (r"/login", LoginHandler),
    (r"/getScore", GetScoreHandler),
    (r"/updateScore", UpdateScoreHandler),
    (r"/getTop3", GetTop3),
    (r"/getNear6", GetNear6ByScore),
    (r"/uploadImage", UploadImageHandler),
    (r"/getData", GetDataHandler),
])


if __name__ == "__main__":
    application.listen(8888)
    tornado.ioloop.IOLoop.current().start()
