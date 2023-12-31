import requests
import re
import time
from tqdm import tqdm
import os
import commImage
from commImage import downloadImage
from commImage import initData
import concurrent.futures

g_imageType = [".jpg", ".png",".jpeg",".tif",".gif",".bmp",".eps",".pcx",".tga",".svg",".psd"]

def findPictureType(image):
    for type in g_imageType:
        if str(image).endswith(type):
            return type

    return ""

def downloadEhentaiPicture(url, path, imgName, cookie):
    imgId = re.compile(r'(?<=<img id="img" src=").+?\.(jpg|png|jpeg|tif|webp|gif|bmp|eps|pcx|tga|svg|psd)', re.DOTALL)
    for times in range(6):
        try:
            response = requests.get(url, timeout=15, headers = commImage.g_headers,cookies=cookie)
            text = response.text
        except:
            continue
        else:
            try:
                it = re.search(imgId, text).group()
                imageType = findPictureType(it)
                if "" == imageType:
                    commImage.g_reCheckDownload[str(imgName)] = url
                    break
                if False == downloadImage(it, path, imgName, cookie, imageType):
                    commImage.g_reCheckDownload[str(imgName)] = url
                break
            except:
                if 5 == times:
                    commImage.g_reCheckDownload[str(imgName)] = url
                    break
                continue




def getEhentaiPicture(text, path, dex, cookie):
    futureResultList = []
    picture = re.compile('<div class="gdtm".+?</div>', re.DOTALL)
    allPictureText =re.findall(picture, text)
    pictureLink = re.compile('(?<=<a href=").+?(?=")', re.DOTALL)
    #目前支持jpg、png、jpeg、tif、webp、gif、bmp、eps、pcx、tga、svg、psd

    executor = concurrent.futures.ThreadPoolExecutor(max_workers=20)
    try:
        cnt = dex * 40
        for item in allPictureText:
            tmpLink = re.search(pictureLink, item).group()
            futureResultList.append(executor.submit(downloadEhentaiPicture, tmpLink, path, cnt, cookie))
            cnt += 1
    finally:
        # 在使用完毕后显式地关闭线程池
        executor.shutdown()


def findEhentaiTextPageNum(text, num):
    pageNumPattern = re.compile('(?<=<td class="gdt1">Length:</td><td class="gdt2">).+?(?= pages</td>)')
    try:
        num[0] = int(re.search(pageNumPattern, text).group())
    except:
        num[0] = 1
        return -1
    
#创建文件夹子函数
def createPath(createDir):
    try:
        if True == os.path.exists(createDir):
            os.rmdir(createDir)
        os.mkdir(createDir)
    except:
        return -1

def getEhentaiDownloadPath(downloadPath):
    for cnt in range(3):
        tmpDir = input('第' + str(cnt+1) + '次输入，请输入创建的文件夹（输入quit返回上一步）:')
        if 'quit' == tmpDir:
            return -1
        tmpDir = commImage.g_imageRoot + tmpDir
        
        if -1 == createPath(tmpDir):
            print('地址\"' + tmpDir + '\"错误')
            continue
        else:
            downloadPath.append(tmpDir + '\\')
            break
    

def startCrawlImage(url, dlPath, cookie):
    responseList = []
    cookie1 = {'nw': '1'}
    try:
        responseList.clear()
        response = requests.get(url, timeout=20, headers=commImage.g_headers, cookies=cookie)
        responseList.append(response.text)

    except:
        print('get html fail')

    else:
        findEhentaiTextPageNum(responseList[0], commImage.g_pageNum)

        dex = commImage.g_pageNum[0] // 40
        if 0 != commImage.g_pageNum[0] % 40:
            dex += 1
        commImage.g_bar = tqdm(total=commImage.g_pageNum[0], desc="download", unit="page", ncols=100)
        i = 1
        while i < dex:
            for times in range(6):
                if -1 != url.find('?nw=session'):
                    newSearchUrl = url.replace('?nw=session', '') + '?p=' + str(i)
                    try:
                        response = requests.get(newSearchUrl, timeout=20, headers=commImage.g_headers, cookies=cookie1)
                        responseList.append(response.text)
                    except:
                        if 5 == times:
                            print('url fail ' + str(i))
                            return -1
                        continue
                    else:
                        break
                else:
                    newSearchUrl = url + '?p=' + str(i)
                    try:
                        response = requests.get(newSearchUrl, timeout=20, headers=commImage.g_headers, cookies=cookie)
                        responseList.append(response.text)
                    except:
                        if 5 == times:
                            print('url fail ' + str(i))
                            return -1
                        continue
                    else:
                        break
            i += 1

        dex = 0
        for responseText in responseList:
            getEhentaiPicture(responseText, dlPath, dex, cookie)
            dex += 1
            
        commImage.g_bar.close()
        if 0 != len(commImage.g_reCheckDownload):
            for item in commImage.g_reCheckDownload:
                print("error url " + commImage.g_reCheckDownload[item])
                print(str(item) + 'fail, page in ' + str((int(item) // 40) + 1))
            commImage.g_reCheckDownload.clear()


def crawlEhentaiImages(cookie):
    searchUrl = []
    downloadPath = []


    while True:
        url = input("请输入要下载的漫画（输入quit退出）:")
        if 'init' == url:
            initData()
        elif 'quit' == url:
            exit()
        elif '' == url:
            break
        if -1 == getEhentaiDownloadPath(downloadPath):
            continue
        searchUrl.append(url)

    for i in range(len(searchUrl)):
        startCrawlImage(searchUrl[i], downloadPath[i], cookie)


