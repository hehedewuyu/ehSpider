import sys
from PyQt5.QtWidgets import QApplication, QWidget, QLabel, QLineEdit, QPushButton, QVBoxLayout, QHBoxLayout, QProgressBar, QTextEdit, QFileDialog, QTextBrowser
from PyQt5.QtGui import QTextCharFormat, QColor, QDesktopServices
from PyQt5.QtCore import QObject, pyqtSignal, QTimer, QUrl, Qt
from _overlapped import NULL
import threading
import commImage
import re
import requests
import concurrent.futures
import os

g_imageType = [".jpg", ".png",".jpeg",".tif",".gif",".bmp",".eps",".pcx",".tga",".svg",".psd"]

class ehSpiderSignal(QObject):
    logSignal = pyqtSignal(int, str)
    updateBarSignal = pyqtSignal(int)


class ehSpiderMenu(QWidget):
    def __init__(self):
        super().__init__()

        self.init_ui()

    def init_ui(self):
        self.setWindowFlag(Qt.WindowStaysOnTopHint, True)

        # 创建控件
        urlLabel = QLabel("URL:")
        self.urlLineEdit = QLineEdit()

        pathLabel = QLabel("下载地址:")
        self.pathLineEdit = QLineEdit()
        self.pathLineEdit.setText(commImage.g_imageRoot)
        
        browseButton = QPushButton("浏览")

        addButton = QPushButton("加入队列")

        self.downloadProgressBar = QProgressBar()
        self.downloadProgressBar.setMaximum(100)
        self.downloadProgressBar.setValue(0)

        logLabel = QLabel("日志:")
        self.logTextBrowser = QTextBrowser()
        self.logTextBrowser.setOpenExternalLinks(True)
        # 连接链接点击事件到槽方法
        self.logTextBrowser.anchorClicked.connect(self.openUrlInBrowser)
        # 获取文档对象并设置样式
        textDocument = self.logTextBrowser.document()
        textDocument.setDefaultStyleSheet('a { color: red; }')

        # 设置布局
        layout = QVBoxLayout()

        urlLayout = QHBoxLayout()
        urlLayout.addWidget(urlLabel)
        urlLayout.addWidget(self.urlLineEdit)

        downloadLayout = QHBoxLayout()
        downloadLayout.addWidget(pathLabel)
        downloadLayout.addWidget(self.pathLineEdit)
        downloadLayout.addWidget(browseButton)

        layout.addLayout(urlLayout)
        layout.addLayout(downloadLayout)
        layout.addWidget(addButton)
        layout.addWidget(self.downloadProgressBar)
        layout.addWidget(logLabel)
        layout.addWidget(self.logTextBrowser)

        self.setLayout(layout)

        # 连接按钮点击事件
        browseButton.clicked.connect(self.browseButtonClicked)
        addButton.clicked.connect(self.addButtonClicked)

        # 设置窗口属性
        self.setWindowTitle('ehSpider')
        self.setGeometry(1000, 200, 700, 500)

        self.guiSignal = ehSpiderSignal()
        self.guiSignal.logSignal.connect(self.printLog)
        self.guiSignal.updateBarSignal.connect(self.updateBar)

        self.threadTimer = QTimer(self)
        self.threadTimer.timeout.connect(self.startDownloadThread)
        self.threadTimer.start(1000)  # 每秒触发一次

        self.pageNum = 0
        self.downloadNum = 0
        self.downloadUrl = []
        self.downloadPath = []
        self.downloadThread = NULL
        self.reDownloadUrl = {}

    def openUrlInBrowser(self, url):
        # 打开默认浏览器
        QDesktopServices.openUrl(QUrl(url.toString()))

    def browseButtonClicked(self):
        options = QFileDialog.Options()
        options |= QFileDialog.ShowDirsOnly | QFileDialog.DontUseNativeDialog

        folder_path = QFileDialog.getExistingDirectory(self, "选择文件夹", "E:\\搜索\\yellow\\新本子", options=options)

        if folder_path:
            self.pathLineEdit.setText(folder_path + '/')

        pass

    def sendUpdateBarMsg(self):
        if 0 == self.pageNum:
            self.guiSignal.updateBarSignal.emit(0)
            return
        self.guiSignal.updateBarSignal.emit(int((self.downloadNum / self.pageNum) * 100))

    def sendLogMsg(self, _logLevel, log):
        self.guiSignal.logSignal.emit(_logLevel, log)

    def updateBar(self, process):
        self.downloadProgressBar.setValue(process)

    def printLog(self, _logLevel, log):
        # 获取当前文本的光标
        cursor = self.logTextBrowser.textCursor()

        # 设置文本格式
        textErrorFormat = QTextCharFormat()
        textErrorFormat.setForeground(QColor("red"))  # 设置文本颜色红色
        

        # 设置文本格式
        textDebugFormat = QTextCharFormat()
        textDebugFormat.setForeground(QColor("blue"))  # 设置文本颜色蓝色

        if commImage.logLevel.DEBUG == _logLevel:
            # 设置光标的文本格式
            cursor.setCharFormat(textDebugFormat)
            # 设置文本
            cursor.insertText('[DEBUG]: '+ log + '\n')
        elif commImage.logLevel.ERROR == _logLevel:
            # 设置光标的文本格式
            cursor.setCharFormat(textErrorFormat)
            # 设置文本
            cursor.insertText('[ERROR]: '+ log + '\n')
        elif commImage.logLevel.URLERROR == _logLevel:
            self.logTextBrowser.insertHtml(log)

        else:
            # 设置光标的文本格式
            cursor.setCharFormat(textErrorFormat)
            # 设置文本
            cursor.insertText('[UNKNOWED]: '+ log + '\n')
        cursor.movePosition(cursor.End)
        self.logTextBrowser.setTextCursor(cursor)
        pass

    def findPictureType(self, image):
            for type in g_imageType:
                if str(image).endswith(type):
                    return type

            return ""

    def downloadEhentaiPicture(self, url, path, imgName, cookie):
        imgId = re.compile(r'(?<=<img id="img" src=").+?(?=")', re.DOTALL)
        for times in range(6):
            try:
                response = requests.get(url, timeout=15, headers = commImage.g_headers,cookies=cookie)
                text = response.text
            except:
                if times == 5:
                    self.reDownloadUrl[str(imgName)] = url
                    return
                continue
            else:
                try:
                    it = re.search(imgId, text).group()
                    imageType = self.findPictureType(it)
                    if "" == imageType:
                        self.reDownloadUrl[str(imgName)] = url
                        return
                    if False == commImage.downloadImageByMenu(it, path, imgName, cookie, imageType):
                        self.reDownloadUrl[str(imgName)] = url
                        return
                    
                    self.downloadNum += 1
                    self.sendUpdateBarMsg()
                    return
                except:
                    self.reDownloadUrl[str(imgName)] = url
                    return 




    def getEhentaiPicture(self, text, path, dex, cookie):
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
                futureResultList.append(executor.submit(self.downloadEhentaiPicture, tmpLink, path, cnt, cookie))
                cnt += 1
        finally:
            # 在使用完毕后显式地关闭线程池
            executor.shutdown()


    def findEhentaiTextPageNum(self, text):
        pageNumPattern = re.compile('(?<=<td class="gdt1">Length:</td><td class="gdt2">).+?(?= pages</td>)')
        try:
            self.pageNum = int(re.search(pageNumPattern, text).group())
        except:
            self.pageNum = 0
            return -1
        
    #创建文件夹子函数
    def createPath(self, createDir):
        try:
            if True == os.path.exists(createDir):
                os.rmdir(createDir)
            os.mkdir(createDir)
        except:
            return False
        

    def startCrawlImage(self, url, dlPath, cookie):
        if False == self.createPath(dlPath):
            self.sendLogMsg(commImage.logLevel.ERROR, "下载目录错误!")
            return
        dlPath += '/'
        responseList = []
        cookie1 = {'nw': '1'}
        self.downloadNum = 0
        self.pageNum = 0
        self.sendUpdateBarMsg()
        try:
            responseList.clear()
            response = requests.get(url, timeout=20, headers=commImage.g_headers, cookies=cookie)
            responseList.append(response.text)

        except:
            self.sendLogMsg(commImage.logLevel.ERROR, 'URL获取HTML失败，请检查网络连接')

        else:
            self.findEhentaiTextPageNum(responseList[0])

            dex = self.pageNum // 40
            if 0 != self.pageNum % 40:
                dex += 1
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
                                self.sendLogMsg(commImage.logLevel.ERROR, '错误的URL: ' + str(i))
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
                                self.sendLogMsg(commImage.logLevel.ERROR, '错误的URL: ' + str(i))
                                return
                            continue
                        else:
                            break
                i += 1
            dex = 0
            self.sendLogMsg(commImage.logLevel.DEBUG, dlPath + " 开始爬取！")
            for responseText in responseList:
                self.getEhentaiPicture(responseText, dlPath, dex, cookie)
                dex += 1
                
            if 0 != len(self.reDownloadUrl):
                for item in self.reDownloadUrl:
                    self.sendLogMsg(commImage.logLevel.ERROR, "错误的URL:")
                    self.sendLogMsg(commImage.logLevel.URLERROR, f'错误的URL:<font color="red"><a href="{self.reDownloadUrl[item]}">{self.reDownloadUrl[item]}</a></font>')
                    self.sendLogMsg(commImage.logLevel.ERROR, dlPath + ' 第' +str(item) + '张图片爬取失败, 在第' + str((int(item) // 40) + 1) + '页')
                self.reDownloadUrl.clear()
            self.sendLogMsg(commImage.logLevel.DEBUG, dlPath + " 爬取完成！")

    def startDownloadThread(self):
        if self.downloadThread and self.downloadThread.is_alive():
            return
        
        if len(self.downloadUrl) and len(self.downloadPath):
            # 创建线程
            self.downloadThread = threading.Thread(target=self.startCrawlImage, args=(self.downloadUrl[0],self.downloadPath[0],commImage.g_cookie2))
            self.downloadUrl.pop(0)
            self.downloadPath.pop(0)
            self.downloadThread.start()

    def addButtonClicked(self):
        url = self.urlLineEdit.text()
        path = self.pathLineEdit.text()

        if "" == url:
            self.sendLogMsg(commImage.logLevel.ERROR, "请输入URL")
            return 
        if "" == path:
            self.sendLogMsg(commImage.logLevel.ERROR, "请选择文件存储位置")
            return 

        self.downloadUrl.append(url)
        self.downloadPath.append(path)
        self.urlLineEdit.clear()
        self.pathLineEdit.setText(commImage.g_imageRoot)
        self.sendLogMsg(commImage.logLevel.DEBUG, path + " 加入队列成功！")
        pass


def showMenu():
    commImage.initData()
    app = QApplication(sys.argv)
    window = ehSpiderMenu()
    window.show()
    sys.exit(app.exec_())