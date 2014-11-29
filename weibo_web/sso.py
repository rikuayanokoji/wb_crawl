# coding=utf8
import platform
import random
import subprocess
import urllib
import base64
import json
import time
import webbrowser
import requests
import rsa
import binascii
import re


__author__ = "riku"

RE_LOCATION_REPLACE = re.compile(r".*location\.replace\([\"|\'](.+?)[\"|\']\).*")


class LoginError(Exception):
    def __init__(self, code, reason):
        self.code = code
        self.reason = reason

    def __str__(self):
        return "<LoginError(code=%s, reason=%s)>" % (self.code, self.reason)


class WeiboSSO(object):
    def __init__(self, session):
        """
        :type session: requests.Session
        """
        self.session = session
        self.rsa_key = None

    PRELOGIN_CALLBACK = "sinaSSOController.preloginCallBack"
    PRELOGIN_PREFIX = "{callback}(".format(callback=PRELOGIN_CALLBACK)
    PRELOGIN_SUFFIX = ")"
    PRELOGIN_SUFFIX2 = ");"

    def prelogin(self, username):
        url = "http://login.sina.com.cn/sso/prelogin.php?entry=weibo&" \
              "callback={callback}&su={user}&rsakt=mod&checkpin=1&client=ssologin.js(v1.4.18)&_={time}"
        url = url.format(
            callback=WeiboSSO.PRELOGIN_CALLBACK, user=WeiboSSO.encode_username(username), time=1000. * time.time())
        r = self.session.get(url, headers={"Referer": "http://weibo.com/login.php"})
        r = r.text
        if r.startswith(WeiboSSO.PRELOGIN_PREFIX):
            if r.endswith(WeiboSSO.PRELOGIN_SUFFIX):
                r = r[len(WeiboSSO.PRELOGIN_PREFIX):-len(WeiboSSO.PRELOGIN_SUFFIX)]
            elif r.endswith(WeiboSSO.PRELOGIN_SUFFIX2):
                r = r[len(WeiboSSO.PRELOGIN_PREFIX):-len(WeiboSSO.PRELOGIN_SUFFIX2)]
            else:
                raise ValueError()
        _value = {"showpin": 0}
        _value.update(json.loads(r))
        return _value

    def login(self, username, password):
        prelogin = self.prelogin(username)
        self.rsa_key = rsa.PublicKey(int(prelogin["pubkey"], 16), 65537)
        post = {"entry": "weibo", "gateway": 1, "from": "", "savestate": 7, "useticket": 1,
                "pagerefer": "http://d.weibo.com/",
                "pcid": prelogin["pcid"],
                "vsnf": 1,
                "pwencode": "rsa2",
                "service": "miniblog",
                "sr": "1920*1080",
                "encoding": "UTF-8",
                "prelt": 101,
                "url": "http://weibo.com/ajaxlogin.php?framelogin=1&callback=parent.sinaSSOController.feedBackUrlCallBack",
                "returntype": "META"}
        post['servertime'] = prelogin["servertime"]
        post['nonce'] = prelogin["nonce"]
        post['su'] = WeiboSSO.encode_username(username)
        post['sp'] = WeiboSSO.rsa_encrypt_to_hex(self.rsa_key,
                                                 '%s\t%s\n%s' % (
                                                     str(prelogin["servertime"]), str(prelogin["nonce"]), password))
        post['rsakv'] = prelogin["rsakv"]
        if prelogin["showpin"] == 1:
            self.get_login_pincode(prelogin["pcid"])
            post["door"] = raw_input("Captcha: ")
        r = self.session.post("http://login.sina.com.cn/sso/login.php?client=ssologin.js(v1.4.18)", post,
                              headers={"Referer": "http://weibo.com/"})
        r = r._content.decode("gbk")
        if "passport.weibo.com/wbsso/login" in r:
            r = self.session.get(RE_LOCATION_REPLACE.findall(r)[0])
        else:
            params = RE_LOCATION_REPLACE.findall(r)[0].split("?", 1)[1]
            params = dict([param.split("=") for param in params.split("&")])
            raise LoginError(code=params["retcode"], reason=urllib.unquote(params["reason"]).decode("gbk"))

    def get_login_pincode(self, pcid):
        # bilogin.js: Math.floor(Math.random()*1e8)
        r = self.session.get("http://login.sina.com.cn/cgi/pin.php?r={rand}&s=0&p={pcid}".format(
            rand=random.randint(100000000, 1000000000), pcid=pcid))
        if platform.system() == "Darwin":
            with open("tmp.jpeg", "wp") as fp:
                fp.write(r._content)
            subprocess.Popen(["open", "tmp.jpeg"])
        else:
            webbrowser.open("data:image/jpeg;base64,%s" % urllib.quote(base64.encode(r._content)))

    @staticmethod
    def rsa_encrypt_to_hex(key, plain):
        return binascii.b2a_hex(rsa.encrypt(plain, key))

    @staticmethod
    def encode_username(username):
        return base64.b64encode(urllib.quote(username))
