#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# @Date    : 2019-12-04 11:22:43
# @Author  : wumingsheng (wu_mingsheng@126.com)
# @Link    : link
# @Version : 1.0.0

import os


def git_commit():
    print(" ======= 提交代码到github ==== ")
    message = input("请输入提交信息: ")
    os.system("git add .")
    os.system("git commit -m %s" % message)
    return os.system("git push")

print("gitbook build ... , please waiting...")
os.system("gitbook build ./ ./docs --clean")
print("gitbook build to docs dir finished !")

FLAG = input("是否同步文件到git远程仓库(y/n)? ")

if FLAG == "y":
    code = git_commit()
    print("返回code: ", code)
