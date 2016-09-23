#!/usr/bin/env python
#coding:utf-8
# 2016-09-23 first edition

import os

def isNum(s):
    if s.isdigit():
        return True
    else:
        return False


if __name__ == "__main__":
    for i in os.listdir('/proc'):
        if isNum(i):
            print i,


