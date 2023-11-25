import threading
import requests
from _overlapped import NULL

g_headers = {
    'User-Agent' : 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
    'Upgrade-Insecure-Requests': '1'
}

g_imageRoot = ''
g_reCheckDownload = {}
g_pageNum = [0]

g_cookie2 = NULL
g_bar = NULL

def downloadImage(url, path, imgName, cookie, type):
    for i in range(6):
        try:
            response = requests.get(url, timeout=15, headers=g_headers,cookies=cookie)
        except:

            if i == 5:

                g_reCheckDownload[str(imgName)] = url
            continue
        else:
            if 0 == type:
                f = open(path + str(imgName) + ".jpg", 'wb')
            else:
                f = open(path + str(imgName) + ".gif", 'wb')
            f.write(response.content)
            f.close()
            g_bar.update(1)
            break

def initData():
    with open('./config/initCfg.txt', 'r' ,encoding='utf-8') as f:
        for line in f.readlines():
            if -1 != line.find('root'):
                rootIndex = line.index(':')
                global g_imageRoot
                g_imageRoot = line[rootIndex + 1:].strip()
            elif -1 != line.find('cookie'):
                cookieIndex = line.index(':')
                cookieInput = line[cookieIndex + 1:].strip()
                global  g_cookie2
                g_cookie2 = dict(map(lambda x: x.split('='), cookieInput.split(";")))




