import requests
import re
import time
from tqdm import tqdm
import os
import commImage
from commImage import downloadImage
from bs4 import BeautifulSoup
import concurrent.futures

def downloadEhentaiPicture(url, path, imgName, cookie):
    jpgImgId = re.compile('(?<=<img id="img" src=").+?\.(jpg)', re.DOTALL)
    gifImgId = re.compile('(?<=<img id="img" src=").+?\.(gif)', re.DOTALL)
    pngImgId = re.compile('(?<=<img id="img" src=").+?\.(png)', re.DOTALL)
    for times in range(6):
        try:
            response = requests.get(url, timeout=15, headers = commImage.g_headers,cookies=cookie)
            text = response.text
        except:
            continue
        else:
            try:
                it = re.search(jpgImgId, text).group()
                downloadImage(it, path, imgName, cookie, 0)
                break
            except:
                try:
                    it = re.search(gifImgId, text).group()
                    downloadImage(it, path, imgName, cookie, 1)
                    break
                except:
                    commImage.g_reCheckDownload[str(imgName)] = url
                    break




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

def getEhentaiDownloadPath(downloadPath):
    tmpDir = input('请输入创建的文件夹（输入quit返回上一步）:')
    if 'quit' == tmpDir:
        return -1
    tmpDir = commImage.g_imageRoot + tmpDir
    print(tmpDir)
    for cnt in range(3):
        try:
            if True == os.path.exists(tmpDir):
                os.rmdir(tmpDir)
            os.mkdir(tmpDir)
        except:
            if cnt == 3:
                return -1
            tmpDir = commImage.g_imageRoot + input('地址\"' + tmpDir + '\"错误，请输入新目录:')
            if commImage.g_imageRoot + 'quit' == tmpDir:
                return -1
            continue
        else:
            break
    downloadPath.append(tmpDir + '\\')

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
    
    '''response = requests.get(searchUrl[0], timeout=20, headers=commImage.g_headers, cookies=cookie)
    soup = BeautifulSoup(response.text, 'lxml')
    list = soup.find_all(class_ ="gdtm")
    print(list)'''

    while True:
        url = input("请输入要下载的漫画（输入quit退出）:")
        if 'quit' == url:
            exit()
        if '' == url:
            break
        if -1 == getEhentaiDownloadPath(downloadPath):
            continue
        searchUrl.append(url)

    for i in range(len(searchUrl)):
        startCrawlImage(searchUrl[i], downloadPath[i], cookie)


