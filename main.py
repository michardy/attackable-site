#! venv/bin/python

##Intentionally insecure website
##Please Note:
##    This code should NEVER be used in production.
##    Anyone who uses it in production should be drawn and quarted.  
##    It is intentionally riddled with security problems both indicated and otherwise.

import tornado.ioloop
import tornado.web
import uuid
import hashlib
import urllib.request as request

#Also: Please, NEVER store your data like this.
db = {
        'users':{},
        'posts':[],
        'harden': False
    }

class Login(tornado.web.RequestHandler):
    """Handles login"""
    def get(self):
        """Renders template of login page"""
        cookie = self.get_cookie('sid')
        if not cookie:
            self.set_cookie('sid', str(uuid.uuid1()))
        self.render('login.html')
    def post(self):
        """Processes login requests"""
        db = self.settings['db']
        uname = self.get_argument('username')
        passw = self.get_argument('password')
        if uname in db['users']:
            cookie = self.get_cookie('sid')
            data = b'{"sid":"'+cookie+'", "uid":"'+uname+'", "ak":"LYOEaNy-oOWKK9W8Y-X2YwSdS386qcbNWrA-j2qF3gXzxIQj6d6f6V69U4oU_um-bH7151ofY1CsQKoADM5CyQ=="}'
            with request.urlopen('https://hijackingprevention.com/api/reg_usr', data=data) as r:
                try:
                    auth = (int(r.read()) > 0.5)
                except ValueError:
                    auth = False
            if hashlib.md5(passw.encode('utf-8')).hexdigest() == db['users'][uname]['passwd'] and (not (db['harden']) or auth):
                self.set_cookie('uid', uname+':'+hashlib.md5(uname.encode('utf-8')).hexdigest())#never has there been a worse session cookie ever
            else:
                self.redirect('/demo/login')
        self.redirect("/demo/post")

class Signup(tornado.web.RequestHandler):
    """Handles signup"""
    def get(self):
        """Renders template of signup page"""
        cookie = self.get_cookie('sid')
        if not cookie:
            self.set_cookie('sid', str(uuid.uuid1()))
        self.render('signup.html')
    def post(self):
        """Processes signup requests"""
        db = self.settings['db']
        uname = self.get_argument('username')
        db['users'][uname] = { #another purely ludicrous vulnerability
            'passw': hashlib.md5(self.get_argument('password').encode('utf-8')).hexdigest()
        }
        cookie = self.get_cookie('sid')
        data = b'{"sid":"'+cookie+'", "uid":"'+uname+'", "ak":"LYOEaNy-oOWKK9W8Y-X2YwSdS386qcbNWrA-j2qF3gXzxIQj6d6f6V69U4oU_um-bH7151ofY1CsQKoADM5CyQ=="}'
        with request.urlopen('https://hijackingprevention.com/api/reg_usr', data=data) as r:
            print(r.read())
        self.set_cookie('uid', uname+':'+hashlib.md5(uname.encode('utf-8')).hexdigest())
        self.redirect("/demo/post")

class Post(tornado.web.RequestHandler):
    """Posting"""
    def get(self):
        """Renders posting page template"""
        cookie = self.get_cookie('sid')
        if not cookie:
            self.set_cookie('sid', str(uuid.uuid1()))
        cookie = self.get_cookie('uid').split(':')
        if cookie[1] == hashlib.md5(cookie[0].encode('utf-8')).hexdigest():
            self.render('post.html')
        else:
            self.redirect("/demo/login")
    def post(self):
        """Handles post creation
        There are at least two vulnerabilities in this function.
        Can you catch them all?
        """
        db = self.settings['db']
        cookie = self.get_cookie('uid').split(':')
        sid = self.get_cookie('sid')
        data = b'{"sid":"'+sid+'", "uid":"'+uname+'", "ak":"LYOEaNy-oOWKK9W8Y-X2YwSdS386qcbNWrA-j2qF3gXzxIQj6d6f6V69U4oU_um-bH7151ofY1CsQKoADM5CyQ=="}'
        with request.urlopen('https://hijackingprevention.com/api/reg_usr', data=data) as r:
            try:
                auth = (int(r.read()) > 0.5)
            except ValueError:
                auth = False
        if cookie[1] == hashlib.md5(cookie[0].encode('utf-8')).hexdigest() and (not (db['harden']) or auth):
            post = {
                'title': self.get_argument('title'),
                'body': self.get_argument('body'),
                'poster': cookie[0]
            }
            db['posts'].append(post)
            self.redirect("/demo")
        else:
            self.redirect("/demo/login")

class GetHash(tornado.web.RequestHandler):
    """Handles forgery"""
    def get(self):
        """Renders template of page"""
        cookie = self.get_cookie('sid')
        if not cookie:
            self.set_cookie('sid', str(uuid.uuid1()))
        self.render('forge.html')
    def post(self):
        """Forges session cookies"""
        db = self.settings['db']
        uname = self.get_argument('username')
        self.set_cookie('uid', uname+':'+hashlib.md5(uname.encode('utf-8')).hexdigest())#Yes, this session cookie can be forged
        self.redirect("/demo/post")

class Main(tornado.web.RequestHandler):
    """Handles home page"""
    def get(self):
        """Renders template of home page"""
        cookie = self.get_cookie('sid')
        if not cookie:
            self.set_cookie('sid', str(uuid.uuid1()))
        db = self.settings['db']
        self.render('index.html', queryuser=False, posts=db['posts'])

class User(tornado.web.RequestHandler):
    """Handles home page"""
    def get(self, queryuser):
        """Renders template of home page"""
        cookie = self.get_cookie('sid')
        if not cookie:
            self.set_cookie('sid', str(uuid.uuid1()))
        db = self.settings['db']
        self.render('index.html', queryuser=queryuser, posts=db['posts'])

def makeApp():
    return(tornado.web.Application([
        (r"/demo/post", Post),
        (r"/demo/signup", Signup),
        (r"/demo/login", Login),
        (r"/demo/getHash", GetHash),
        (r"/demo/u/([^/]+)", User),
        (r"/demo/static/(.*)", tornado.web.StaticFileHandler, {'path': 'static/'}),
        (r"/demo/", Main),
        (r"/demo", Main)
    ], db=db, template_path='templates/'))

app = makeApp()
app.listen(8090)
tornado.ioloop.IOLoop.current().start()
