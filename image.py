from crawlHamine import crawlHamineImages
from crawlEhentai import crawlEhentaiImages
import commImage
from commImage import initData


def crawlImage():
    while 1:
        initData()
        while 1:
            cookie = {}
            if  'ex' == commImage.g_type:
                if -1 == crawlEhentaiImages(commImage.g_cookie2):
                    break
            elif 'h' == commImage.g_type:
                if -1 == crawlHamineImages():#H站爬虫暂不支持显示进度
                    break
            elif 'e' == commImage.g_type:
                if -1 == crawlEhentaiImages(cookie):
                    break
            else:
                break
