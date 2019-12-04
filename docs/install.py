#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# @Date    : 2019-12-04 11:22:43
# @Author  : wumingsheng (wu_mingsheng@126.com)
# @Link    : link
# @Version : 1.0.0

import os

MESSAGE = input("请输入提交信息: ")

os.system("gitbook build ./ ./docs --clean")
os.system("git add .")
os.system("git commit -m %s" % MESSAGE)
os.system("git push")
