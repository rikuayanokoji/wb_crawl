# coding=utf-8
import requests
import pickle


__author__ = 'riku'


_DEFAULT_USERAGENT = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/37.0.2062.124 Safari/537.36"


class Session(object):
    def __init__(self, useragent=_DEFAULT_USERAGENT):
        self.session = requests.session()

    def login(self, username, password, captcha=None):
        import weibo_web.sso
        weibo_web.sso.WeiboSSO(self.session).login(username, password, captcha)

    def loads(self, dumped):
        self.session.cookies = requests.utils.cookiejar_from_dict(pickle.loads(dumped))

    def dumps(self):
        return pickle.dumps(requests.utils.dict_from_cookiejar(self.session.cookies))

    def requests(self):
        return self.session
