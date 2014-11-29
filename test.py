#!/bin/usr/env python
# coding=utf-8
__author__ = "riku"

if __name__ == "__main__":
    import weibo_web
    session = weibo_web.Session()
    session.login(raw_input("Username: "), raw_input("Password: "))
    print "Login successfully. Enjoy it ;)"
