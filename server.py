import tornado.ioloop
import tornado.web
from db import Dmdb
from Crypto.Cipher import AES
import base64
import json
import random
import hashlib

MDB = Dmdb()
token_map = {}
random.seed()


class MainHandler(tornado.web.RequestHandler):
    def get(self):
        self.write("hello world")
        
class TRBaseHandler(tornado.web.RequestHandler):
    def tr_read(self):
        b64 = self.get_argument("p", "")
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
        self.write(b64)
        print "Base write", data

    def tr_error(self, error_code, error_msg):
        jstr = '''{"err_code":%s,"err_msg":%s}''' % (error_code, error_msg)
        self.tr_write(jstr)
        
def trmd5(data):
    m5 = hashlib.md5()
    m5.update(data)
    return m5.hexdigest()

class NewAcctHandler(TRBaseHandler):
    def get(self):
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
                ret = '''{id":%s, "pwd":"%s", "err_code":0}''' % (id, pwd)
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

def genNextSN():
    return random.randint(0,9999)

class LoginHandler(TRBaseHandler):
    def get(self):
        data = self.tr_read()
        jobj = json.loads(data)
        id = jobj["id"]
        pwd = jobj["pwd"]
        record = MDB.getById(id) 
        if record != None and record["pass_md5"] == pwd:
            tk = genToken()
            sn = genNextSN()
            token_map[id] = (tk, sn)
            ret = '''{"tk":"%s", "sn":%s}''' % (tk, sn)
            self.tr_write(ret)
        else:
            self.tr_error(3, "account error")
        
        
application = tornado.web.Application([
    (r"/", MainHandler),
    (r"/newAccount", NewAcctHandler),
    (r"/login", LoginHandler),
])



if __name__ == "__main__":
    application.listen(8888)
    tornado.ioloop.IOLoop.current().start()
