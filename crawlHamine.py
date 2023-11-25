import requests
import re
import threading
import time
import random
import os
import commImage
from commImage import downloadImage


def downloadHaminePicture(url, path, imgName):
    imgId = re.compile('(?<=<img id="current-page-image" src=").+?\.(jpg|png|jpeg|tif|webp|gif|bmp|eps|pcx|tga|svg|psd)', re.DOTALL)
    timeWait = random.randint(1, 3)
    time.sleep(timeWait)
    for times in range(6):
        try:
            response = requests.get(url, timeout=15, headers = commImage.g_headers)
            text = response.text
        except:
            continue
        else:
            it = re.search(imgId, text).group()
            downloadImage(it, path, imgName,0)
            break


def getHaminePicture(text, path):
    threadList = []

    picture = re.compile('<div class="comics-panel-margin comics-panel-margin-top comics-panel-padding comics-thumbnail-wrapper comic-rows-wrapper" style="position: relative;">.+?</div>', re.DOTALL)
    pictureText =re.search(picture, text).group()
    pictureLink = re.compile('(?<=<a href=").+?(?=")', re.DOTALL)
    allPictureLink = re.findall(pictureLink,pictureText)
    cnt = 0
    for pictureLink in allPictureLink:
        threadName = 'downloadThread' + str(cnt)
        thread = threading.Thread(name=threadName, target=downloadHaminePicture, args=(pictureLink, path, cnt))
        threadList.append(thread)
        cnt += 1

    for tmpThread in threadList:
        while True:
            if threading.active_count() >= 20:
                time.sleep(3)
            else:
                break
        tmpThread.start()

def getHamineDownloadPath(text, downloadPath):
    bookName = re.compile('(?<=<h4 class="title comics-metadata-margin-top").+?(?=</h4>)', re.DOTALL)
    try:
        print('本子名称为:<' + re.search(bookName, text).group() + '>')

    except:
        print('未获取到对应本子名称')
    tmpDir = downloadPath[0] + input('请输入创建的文件夹（输入quit返回上一步）:')
    if 'quit' == tmpDir:
        return -1
    print(tmpDir)
    for cnt in range(3):
        try:
            os.mkdir(tmpDir)
        except:
            if cnt == 3:
                return -1
            tmpDir = downloadPath[0] + input('地址\"' + tmpDir + '\"错误，请输入新目录:')
            continue
        else:
            break
    downloadPath[0] = tmpDir + '\\'

def crawlHamineImages():
    searchUrl = input("请输入要下载的漫画（输入quit返回上一步）:")
    downloadPath = [commImage.g_imageRoot]

    if 'quit' == searchUrl:
        return -1

    response = requests.get(searchUrl, timeout=40, headers=commImage.g_headers)

    if -1 == getHamineDownloadPath(response.text, downloadPath):
        return -1

    getHaminePicture(response.text, downloadPath[0])

    while True:
        time.sleep(1)
        if(1 == threading.active_count()):
            if 0 != len(commImage.g_reCheckDownload):
                for item in commImage.g_reCheckDownload:
                    downloadImage(commImage.g_reCheckDownload[item], downloadPath[0], item)

                commImage.g_reCheckDownload.clear()

            break








