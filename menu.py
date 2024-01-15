import sys
from PyQt5.QtWidgets import QApplication, QWidget, QLabel, QLineEdit, QPushButton, QVBoxLayout, QHBoxLayout, QProgressBar, QComboBox, QFileDialog, QTextBrowser
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

class setConfigPage(QWidget):

    closed = pyqtSignal()

    def __init__(self):
        super().__init__()

        self.init_ui()
    def init_ui(self):
        self.setWindowFlag(Qt.WindowStaysOnTopHint, True)

        # 创建控件
        setTypeLabel = QLabel("类型:")
        self.setTypeCombox = QComboBox()
        self.setTypeCombox.addItem('e')
        self.setTypeCombox.addItem('ex')
        self.setTypeCombox.addItem('h')

        setPathLabel = QLabel("根目录:")
        self.setPathLineEdit = QLineEdit()

        setCookieLabel = QLabel("cookie:")
        self.setCookieLineEdit = QLineEdit()

        okButton = QPushButton("确定")

        layout = QVBoxLayout()

        setTypeLayout = QHBoxLayout()
        setTypeLayout.addWidget(setTypeLabel)
        setTypeLayout.addWidget(self.setTypeCombox)

        setPathLayout = QHBoxLayout()
        setPathLayout.addWidget(setPathLabel)
        setPathLayout.addWidget(self.setPathLineEdit)

        setCookieLayout = QHBoxLayout()
        setCookieLayout.addWidget(setCookieLabel)
        setCookieLayout.addWidget(self.setCookieLineEdit)

        layout.addLayout(setTypeLayout)
        layout.addLayout(setPathLayout)
        layout.addLayout(setCookieLayout)
        layout.addWidget(okButton)

        self.setLayout(layout)

        okButton.clicked.connect(self.okButtonClicked)

        self.setWindowTitle('设置')
        self.setGeometry(1100, 300, 400, 300)

        with open('./config/initCfg.txt', 'r' ,encoding='utf-8') as f:
            for line in f.readlines():
                if -1 !=line.find('type'):
                    typeIndex = line.find(':')
                    self.setTypeCombox.setCurrentText(line[typeIndex + 1:].strip())
                elif -1 != line.find('root'):
                    rootIndex = line.index(':')
                    self.setPathLineEdit.setText(line[rootIndex + 1:].strip())
                elif -1 != line.find('cookie'):
                    cookieIndex = line.index(':')
                    self.setCookieLineEdit.setText(line[cookieIndex + 1:].strip())

    def okButtonClicked(self):
        with open('./config/initCfg.txt', 'r' ,encoding='utf-8') as f:
            lines = f.readlines()
        for i, line in enumerate(lines):
            if 'type' in line:
                typeIndex = line.find(':')
                lines[i] = line[:typeIndex + 1] + self.setTypeCombox.currentText() + '\n'
            elif 'root' in line:
                rootIndex = line.index(':')
                lines[i] = line[:rootIndex + 1] + self.setPathLineEdit.text() + '\n'
            elif 'cookie' in line:
                cookieIndex = line.index(':')
                lines[i] = line[:cookieIndex + 1] + self.setCookieLineEdit.text() + '\n'

        with open('./config/initCfg.txt', 'w' ,encoding='utf-8') as f:
            f.writelines(lines)
        
        commImage.initData()
        self.close()
        self.closed.emit()



        

        

        


class ehSpiderMenu(QWidget):
    def __init__(self):
        super().__init__()

        self.init_ui()

    def init_ui(self):
        self.setWindowFlag(Qt.WindowStaysOnTopHint, True)
        self.setConfigPage = setConfigPage()
        self.setConfigPage.closed.connect(self.updateRoot)

        # 创建控件
        urlLabel = QLabel("URL:")
        self.urlLineEdit = QLineEdit()

        setConifgButton = QPushButton("设置")

        pathLabel = QLabel("下载地址:")
        self.pathLineEdit = QLineEdit()
        self.pathLineEdit.setText(commImage.g_imageRoot)
        
        browseButton = QPushButton("浏览")

        addButton = QPushButton("加入队列")

        self.downloadProgressBar = QProgressBar()
        self.downloadProgressBar.setMaximum(100)
        self.downloadProgressBar.setValue(0)

        logLabel = QLabel("日志:")
        redownloadLabel = QLabel("失败地址:")
 
        self.logTextBrowser = QTextBrowser()
        self.logTextBrowser.setOpenExternalLinks(True)
        # 连接链接点击事件到槽方法
        self.logTextBrowser.anchorClicked.connect(self.openUrlInBrowser)
        # 获取文档对象并设置样式
        textDocument = self.logTextBrowser.document()
        textDocument.setDefaultStyleSheet('a { color: red; }')

        self.reDownloadBrowser = QTextBrowser()
        self.reDownloadBrowser.setOpenExternalLinks(True)
        # 连接链接点击事件到槽方法
        self.reDownloadBrowser.anchorClicked.connect(self.openUrlInBrowser)
        # 获取文档对象并设置样式
        textDocument = self.reDownloadBrowser.document()
        textDocument.setDefaultStyleSheet('a { color: red; }')

        # 设置布局
        layout = QVBoxLayout()

        urlLayout = QHBoxLayout()
        urlLayout.addWidget(urlLabel)
        urlLayout.addWidget(self.urlLineEdit)
        urlLayout.addWidget(setConifgButton)

        downloadLayout = QHBoxLayout()
        downloadLayout.addWidget(pathLabel)
        downloadLayout.addWidget(self.pathLineEdit)
        downloadLayout.addWidget(browseButton)

        logTitleLayout = QHBoxLayout()
        logTitleLayout.addWidget(logLabel)
        logTitleLayout.addWidget(redownloadLabel)

        logLayout = QHBoxLayout()
        logLayout.addWidget(self.logTextBrowser)
        logLayout.addWidget(self.reDownloadBrowser)

        layout.addLayout(urlLayout)
        layout.addLayout(downloadLayout)
        layout.addWidget(addButton)
        layout.addWidget(self.downloadProgressBar)
        layout.addLayout(logTitleLayout)
        layout.addLayout(logLayout)

        self.setLayout(layout)

        # 连接按钮点击事件
        setConifgButton.clicked.connect(self.setConfigButtonClicked)
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

    def setConfigButtonClicked(self):
        self.setConfigPage.show()

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
    
    def updateRoot(self):
        self.pathLineEdit.setText(commImage.g_imageRoot)

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
        elif commImage.logLevel.URLTITLE == _logLevel:
            self.reDownloadBrowser.append(log)
        elif commImage.logLevel.URLERROR == _logLevel:
            self.reDownloadBrowser.insertHtml(log)

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

    def downloadHamiePicture(self, url, path, imgName, cookie):
        imgId = re.compile(r'(?<=<img id="current-page-image" src=").+?(?=")', re.DOTALL)
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


    def getHaminePicture(self, text, path, cookie):
        futureResultList = []
        picture = re.compile('<div class="comics-panel-margin comics-panel-margin-top comics-panel-padding comics-thumbnail-wrapper comic-rows-wrapper" style="position: relative;">.+?</div>', re.DOTALL)
        pictureText =re.search(picture, text).group()
        pictureLink = re.compile('(?<=<a href=").+?(?=")', re.DOTALL)
        allPictureLink = re.findall(pictureLink,pictureText)
        executor = concurrent.futures.ThreadPoolExecutor(max_workers=10)
        try:
            cnt = 0
            for pictureLink in allPictureLink:
                futureResultList.append(executor.submit(self.downloadHamiePicture, pictureLink, path, cnt, cookie))
                cnt += 1
        finally:
            # 在使用完毕后显式地关闭线程池
            executor.shutdown()

    def getEhentaiPicture(self, text, path, dex, cookie):
        futureResultList = []
        picture = re.compile('<div class="gdtm".+?</div>', re.DOTALL)
        allPictureText =re.findall(picture, text)
        pictureLink = re.compile('(?<=<a href=").+?(?=")', re.DOTALL)
        #目前支持jpg、png、jpeg、tif、webp、gif、bmp、eps、pcx、tga、svg、psd
        executor = concurrent.futures.ThreadPoolExecutor(max_workers=10)
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
        
    def findHamineTextPageNum(self, text):
        pageNumPattern = re.compile(r'class="no-select".*?>(\d+)<\/div>')
        try:
            self.pageNum = int(pageNumPattern.search(text).group(1))
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
        
    def startCrawlHamineImage(self, url, dlPath, cookie):
        if False == self.createPath(dlPath):
            self.sendLogMsg(commImage.logLevel.ERROR, "下载目录错误!")
            return
        dlPath += '/'
        self.downloadNum = 0
        self.pageNum = 0
        self.sendUpdateBarMsg()

        try:
            response = requests.get(url, timeout=20, headers=commImage.g_headers, cookies=cookie)
            responseText = response.text

        except:
            self.sendLogMsg(commImage.logLevel.ERROR, 'URL获取HTML失败，请检查网络连接')

        else:
            self.findHamineTextPageNum(responseText)
            self.sendLogMsg(commImage.logLevel.DEBUG, dlPath + " 开始爬取！")
            self.getHaminePicture(responseText, dlPath, cookie)

            if 0 != len(self.reDownloadUrl):
                for item in self.reDownloadUrl:
                    self.sendLogMsg(commImage.logLevel.URLTITLE, dlPath)
                    self.sendLogMsg(commImage.logLevel.URLERROR, f'第' +str(item) + '张图片爬取失败:<font color="red"><a href="{self.reDownloadUrl[item]}">{self.reDownloadUrl[item]}</a></font>')
                self.reDownloadUrl.clear()
            self.sendLogMsg(commImage.logLevel.DEBUG, dlPath + " 爬取完成！")

    def startCrawlEhentaiImage(self, url, dlPath, cookie):
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
                    self.sendLogMsg(commImage.logLevel.URLTITLE, dlPath)
                    self.sendLogMsg(commImage.logLevel.URLERROR, f'第' +str(item) + '张图片爬取失败, 在第' + str((int(item) // 40) + 1) + '页:<font color="red"><a href="{self.reDownloadUrl[item]}">{self.reDownloadUrl[item]}</a></font>')
                self.reDownloadUrl.clear()
            self.sendLogMsg(commImage.logLevel.DEBUG, dlPath + " 爬取完成！")

    def startDownloadThread(self):
        if self.downloadThread and self.downloadThread.is_alive():
            return
        
        if len(self.downloadUrl) and len(self.downloadPath):
            # 创建线程
            if 'ex' == commImage.g_type:
                self.downloadThread = threading.Thread(target=self.startCrawlEhentaiImage, args=(self.downloadUrl[0],self.downloadPath[0],commImage.g_cookie2))
            elif 'e' == commImage.g_type:
                cookie = {}
                self.downloadThread = threading.Thread(target=self.startCrawlEhentaiImage, args=(self.downloadUrl[0],self.downloadPath[0], cookie))
            elif 'h' == commImage.g_type:
                cookie = {}
                self.downloadThread = threading.Thread(target=self.startCrawlHamineImage, args=(self.downloadUrl[0],self.downloadPath[0], cookie))
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

'''if __name__ == '__main__':
    showMenu()'''
    