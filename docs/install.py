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

def gitbook_build():
    print("gitbook build ... , please waiting...")
    os.system("gitbook build ./ ./docs --clean")
    print("gitbook build to docs dir finished !")


gitbook_build()

FLAG = input("是否同步文件到git远程仓库(y/n)? ")

if FLAG == "y": 
    CODE = git_commit()
    if CODE == 0:
        print("success -- ", "提交成功")
    else:
        print("error -- 提交失败, ", "返回code: ", CODE)
