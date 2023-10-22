import requests
import re
import os
from tqdm import tqdm
from commVideo import g_imageRoot,g_headers,g_reCheckDownload

def download_from_url(url, dst):
    # 访问url进行下载
    req = requests.get(url, headers=g_headers, stream=True)
    print(len(req.content))
    pbar = tqdm(total=len(req.content) , desc="Processing", unit="page", ncols=150)
    try:
        with(open(dst[0], 'ab')) as f:
            for chunk in req.iter_content(chunk_size=1024):
                if chunk:
                    f.write(chunk)
                    pbar.update(1024)
    except Exception as e:
        print(e)
        return False

    pbar.close()
    return True

def getHamineDownloadPath(downloadPath):
    tmpDir = input('请输入创建的文件夹:')
    if 'quit' == tmpDir:
        return -1
    tmpDir = downloadPath[0] + tmpDir
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
    tmpName = input('请输入文件名称:')
    if 'quit' == tmpName:
        return -1

    downloadPath[0] = tmpDir + '\\' + tmpName + '.mp4'


def crawlHamineVideo():
    searchVideo = input("请输入要下载的里番:")
    downloadPath = [g_imageRoot]

    if 'quit' == searchVideo:
        return -1

    getHamineDownloadPath(downloadPath)
    download_from_url(searchVideo, downloadPath)

