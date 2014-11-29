#!/bin/usr/env python
# coding=utf-8

__author__ = "riku"

if __name__ == "__main__":
    import weibo_web
    import os
    import json
    session = weibo_web.Session()
    if not os.path.exists("cookies.dat"):
        print "Session dump not found, try login."
        username = raw_input("Username: ")
        password = raw_input("Password: ")
        try:
            session.login(username, password)
            print "Login successfully. Enjoy it ;)"
        except weibo_web.CaptchaRequired as c:
            import base64
            import platform
            import subprocess
            import urllib
            import webbrowser
            if platform.system() == "Darwin":
                with open("tmp.jpeg", "wp") as fp:
                    fp.write(c.captcha._content)
                subprocess.Popen(["open", "tmp.jpeg"])
            else:
                webbrowser.open("data:image/jpeg;base64,%s" % urllib.quote(base64.b64encode(c.captcha._content)))
            session.login(username, password, captcha=raw_input("Captcha: "))
            print "Login successfully. Enjoy it ;)"
            with open("cookies.dat", "w") as fp:
                fp.write(session.dumps())
    else:
        with open("cookies.dat") as fp:
            session.loads(fp.read())
    print "You're login as UID", json.loads(session.requests().get("http://weibo.com/ajaxlogin.php")._content[1:-2])["userinfo"]["uniqueid"]
