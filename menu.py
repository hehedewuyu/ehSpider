import tkinter as tk
from tkinter import *
from tkinter import filedialog
from crawlEhentai import startCrawlImage
import commImage
from commImage import initData

root = Tk()
root.title("spider")
root.geometry("500x500+100+50")

Label(root, text="请选择爬取的类型").place(x = 200, y= 10)



def show_crawl_image_menu():
    topLevelPic = Toplevel(root, height=500, width=500)
    topLevelPic.transient(root)

    Label(topLevelPic, text="请输入密钥").place(x = 10, y=100)

    entryKey = Entry(topLevelPic,width=30)
    entryKey.place(x=110, y=100)

    Label(topLevelPic, text="请输入URL").place(x = 10, y=200)

    entryUrl = Entry(topLevelPic,width=30)
    entryUrl.place(x=110, y=200)
    Label(topLevelPic, text="请输入保存地址").place(x=10, y=300)

    entryRoot = Entry(topLevelPic,width=30)
    entryRoot.place(x = 110, y =300)

    # 输入文件路径
    def selectPath():
        path = filedialog.askdirectory()
        entryRoot.insert(0, path)

    def downloadPic():
        print(entryUrl.get())

        downloadRoot = entryRoot.get() + '/'

        startCrawlImage(entryUrl.get(),downloadRoot, commImage.g_cookie2)




    Button(topLevelPic, text="请选择文件夹", command=selectPath).place(x = 350,y = 290)

    Button(topLevelPic, text="下载", command=downloadPic).place(x = 200, y= 320)






def show_menu():
    initData()
    Button(root, text="爬取图片", command=show_crawl_image_menu, width=10).place(x = 200, y =50)
    root.mainloop()
