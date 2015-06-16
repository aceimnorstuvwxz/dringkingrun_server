import tornado.ioloop
import tornado.web
from db import Dmdb

class MainHandler(tornado.web.RequestHandler):
    def get(self):
        self.write("hello world")
        

class NewAcctHandler(tornado.web.RequestHandler):
    def get(self):
        print ("NewAcctHandler")
        self.write("new acct")
        pass
        
        
application = tornado.web.Application([
    (r"/", MainHandler),
    (r"/newAccount", NewAcctHandler),
])

if __name__ == "__main__":
    application.listen(8888)
    tornado.ioloop.IOLoop.current().start()
