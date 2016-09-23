#!/usr/bin/env python
#coding:utf-8
# 2016-09023

import os
import sys

def print_files(path):
    lsdir = os.listdir(path)
    dirs = [i for i in lsdir if os.path.isdir(os.path.join(path,i))]
    files = [i for i in lsdir if os.path.isfile(os.path.join(path,i))]
    if files:
        for i in files:
            print os.path.join(path, i)
    if dirs:
        for d in dirs:
            print_files(os.path.join(path, d))
if __name__ == "__main__":
    try:
        list_file = sys.argv[1]
    except IndexError:
        print "useage: python %s dir" %__file__
        sys.exit()
    print_files(sys.argv[1])



