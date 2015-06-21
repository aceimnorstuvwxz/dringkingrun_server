import requests
from Crypto.Cipher import AES
import base64
import urllib
import json
import random

def encrypt(msg):
    if len(msg) % 16 != 0 :
        msg += (16 - len(msg)%16)*' '
    #print len(msg), msg
    obj = AES.new('01234567890123456789012345678901', AES.MODE_CBC, '0123456789012345')
    cipherText = obj.encrypt(msg)
    b64 = base64.encodestring(cipherText)
    print b64
    return b64
    
def decrypt(msg):
    b64 = msg
    ciphertext = base64.decodestring(b64)
    #print len(ciphertext)
    obj = AES.new('01234567890123456789012345678901', AES.MODE_CBC, '0123456789012345')
    return obj.decrypt(ciphertext)
    
    
def tt():
    print encrypt('''{"id_string":"my_id_string2"}''')
    print encrypt('''{"id":3, "pwd":"503511d9d8cd41ea"}''')
    print encrypt('''{"id":1, "target":1, "sn":123, "tk":"tyht565765fghg"}''')
    print encrypt('''{"id":1, "score":6666, "sn":1, "tk":"dsfds" }''')
    print encrypt('''{"id":1, "score":100, "sn":9}''')
    
def checkErrCode(jobj):
    if jobj["err_code"] == 0:
        return True
    else:
        print "Server error %s, msg = %s" %(jobj["err_code"], jobj["err_msg"])
        return False

class Client:
    SERVER_URL = "http://localhost:8888/%s"
    
    def SN(self):
        r = self.sn
        self.sn += 1
        if self.sn >= 10000:
            self.sn = 0
        return r
    
    def newAcct(self, id_string):
        raw = '''{"id_string":"%s"}'''%(id_string,)
        enc = encrypt(raw)
        ret = requests.post(self.SERVER_URL%("newAccount",), {"p":enc})
        text = decrypt(ret.text)
        jobj = json.loads(text)
        if checkErrCode(jobj):
            self.id = jobj["id"]
            self.pwd = jobj["pwd"]
            print "newAcct %s %s" % (self.id, self.pwd)
             
    
    def login(self):
        req = {"id":self.id, "pwd":self.pwd}
        req = json.dumps(req)
        req = encrypt(req)
        ret = requests.post(self.SERVER_URL%("login",), {"p":req})
        ret = decrypt(ret.text)
        jobj = json.loads(ret)
        if checkErrCode(jobj):
            self.sn = jobj["sn"]
            self.tk = jobj["tk"]
            print "login", self.sn, self.tk
            
    def baseReq(self):
        return {"id":self.id, "tk":self.tk, "sn":self.SN()}

    def updateScore(self, newScore):
        req = self.baseReq()
        req["score"] = newScore
        req = encrypt(json.dumps(req))
        ret = requests.post(self.SERVER_URL%("updateScore",), {"p":req})
        jobj = json.loads(decrypt(ret.text))
        if checkErrCode(jobj):
            isNew = jobj["is_new"] == 1
            print "updateScore", isNew
    
    def uploadImage(self, path):
        with open(path, 'rb') as f:
            data = f.read()
        
        data = base64.encodestring(data)
        print data
        data = urllib.quote_plus(data)
        print data
        req = self.baseReq()
        req["image"] = data
        req = encrypt(json.dumps(req))
        ret = requests.post(self.SERVER_URL%("uploadImage",), {"p":req})
        jobj = json.loads(decrypt(ret.text))
        if checkErrCode(jobj):
            print "uploadImage ok"
            
    def getData(self):
        req = self.baseReq()
        req = encrypt(json.dumps(req))
        ret = requests.post(self.SERVER_URL%("getData",), {"p":req})
        jobj = json.loads(decrypt(ret.text))
        if checkErrCode(jobj):
            fn = "dtx/tx_id_" + str(self.id) +".jpg"
            print jobj["image"]
            print urllib.unquote_plus(jobj["image"])
            data = base64.decodestring(urllib.unquote_plus(jobj["image"]))
            with open(fn, 'wr') as f:
                f.write(data)
            print "getData ok"
        
random.seed()
if __name__ == "__main__":
    print encrypt('''{"err_code":1,"err_msg":"id_string exists"}     ''')
    '''
    cl = Client()
    cl.newAcct("gfhghfghjkhhkjn"+str(random.randint(0,99999)))
    cl.login()
    cl.updateScore(random.randint(0, 99999))
    cl.uploadImage("tx/tx1.jpg")
    cl.getData()
    '''