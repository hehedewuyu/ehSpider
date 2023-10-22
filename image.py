from crawlHamine import crawlHamineImages
from crawlEhentai import crawlEhentaiImages
import tkinter as tk
import sys
import commImage
from commImage import initData

def crawlImage():
    while 1:
        initData()
        name = input("请输入密钥（输入quit退出程序）:")
        if 'quit' == name:
            break
        elif 'init' == name:
            initData()
            continue
        while 1:
            cookie = {}
            if  'ex' == name:

                if -1 == crawlEhentaiImages(commImage.g_cookie2):
                    break
            elif 'h' == name:
                if -1 == crawlHamineImages():#H站爬虫暂不支持显示进度
                    break
            elif 'e' == name:
                if -1 == crawlEhentaiImages(cookie):
                    break
            else:
                break
