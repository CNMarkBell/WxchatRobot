import os
import itchat
import robot
import utils,config
from tkinter import *

class Application(Frame):
    def __init__(self, master=None):
        Frame.__init__(self, master)
        self.window_init()
        self.pack()
        self.createWidgets()

    def createWidgets(self):
        # operateFrame
        self.operateFrame=Frame(self)
        self.btnLoad=Button(self.operateFrame,text="重新加载",width=7,command=self.loadConfigInfo)
        self.btnLogin=Button(self.operateFrame,text="登录",width=7,command=self.startLogin)
        self.btnLogout=Button(self.operateFrame,text="退出",width=7,command=self.logout)
        self.btnLoad.pack(side= RIGHT)
        self.btnLogin.pack(side= RIGHT)
        # loginFrame
        self.loginFrameLeft=Frame(self.operateFrame)
        self.loginLabel=Label(self.loginFrameLeft,text="当前登录用户：",width="15")
        self.loginLabel.pack(side=LEFT)
        self.loginInfo=Entry(self.loginFrameLeft,width="40")
        self.loginInfo.pack(side=LEFT)
        self.loginFrameLeft.pack(side=LEFT)
        self.operateFrame.pack(side=TOP,expand=YES,fill='x',pady=20)

        # logFrame
        self.logFrame=Frame(self)
        self.scrollbar = Scrollbar(self.logFrame)
        self.scrollbar.pack(side=RIGHT,fill=Y)
        self.logInfo=Listbox(self.logFrame,width=82,height=13,yscrollcommand=self.scrollbar.set)
        self.logInfo.pack(side=LEFT,fill=BOTH)
        self.scrollbar.config(command=self.logInfo.yview)
        self.logFrame.pack(side=BOTTOM,fill=BOTH,pady=20)

        # groupFrame
        self.userListFrame=Frame(self)
        self.groupFrame=Frame(self.userListFrame)
        self.usersFrame=Frame(self.userListFrame)

        self.scrollbarGroup = Scrollbar(self.groupFrame)
        self.scrollbarGroup.pack(side=RIGHT,fill=Y)
        self.scrollbarUsers = Scrollbar(self.usersFrame)
        self.scrollbarUsers.pack(side=RIGHT,fill=Y)

        self.groupInfo=Listbox(self.groupFrame,width=41,height=13,yscrollcommand=self.scrollbarGroup.set)
        self.groupInfo.pack(side=LEFT,fill=BOTH)

        self.usersInfo=Listbox(self.usersFrame,width=41,height=13,yscrollcommand=self.scrollbarUsers.set)
        self.usersInfo.pack(side=LEFT,fill=BOTH)

        self.scrollbarGroup.config(command=self.groupInfo.yview)
        self.scrollbarUsers.config(command=self.usersInfo.yview)

        self.groupFrame.pack(side=LEFT)
        self.usersFrame.pack(side=LEFT)
        self.userListFrame.pack(side=BOTTOM,fill=BOTH,pady=20)

    def window_init(self):
        self.master.title('微信自动回复程序')
        self.master.geometry("600x600+300+300")
        self.master.protocol("WM_DELETE_WINDOW", self.closeWin)
        self.master.resizable(width=True, height=False)

    def startLogin(self):
        # 通过扫描二维码登录微信网页版。
        itchat.auto_login(loginCallback=self.loginCallback,exitCallback=self.exitCallback)
        itchat.run(False, False)

    def logTextBoxInsert(self,msg):
        if(self.logInfo.size()>1000):
            self.logInfo.insert(0, msg)
            self.logInfo.delete(999,END)
        else:
            self.logInfo.insert(0, msg)

    # 登录成功回调
    def loginCallback(self):
        curruser=itchat.search_friends()
        loginfo=curruser["NickName"]+"----登录成功"
        robot.configByWxServerInfo(self)
        robot.start_receiving(self)
        utils.clear_screen()
        os.remove(config.DEFAULT_QR)
        self.btnLogin.pack_forget()
        self.btnLogout.pack(side= RIGHT)
        self.loginInfo.delete(0,END)
        self.loginInfo.insert(0,curruser["NickName"])
        self.logTextBoxInsert(loginfo)

    # 退出登录回调
    def exitCallback(self):
        self.logTextBoxInsert("用户退出登录，请重新登录")
        self.btnLogin.pack(side= RIGHT)
        self.btnLogout.pack_forget()

    # 设置当前匹配到的群
    def setGroupInfo(self,groupInfo):
        self.groupInfo.insert(0, groupInfo)

    # 清理GroupInfo、UsersInfo信息框
    def cleanInfo(self):
        self.groupInfo.delete(0,END)
        self.usersInfo.delete(0,END)

    def loadConfigInfo(self):
        robot.configByWxServerInfo(self)

    # 设置当前匹配成员信息
    def setUsersInfo(self,userInfo):
        self.usersInfo.insert(0, userInfo)

    def removeEmoji(self,text):
        highpoints = re.compile(u'[\U00010000-\U0010ffff]')
        return highpoints.sub(u'',text)

    # 退出登录
    def logout(self):
        itchat.logout()
        self.usersInfo.delete(0,END)
        self.groupInfo.delete(0,END)

    # 关闭窗口
    def closeWin(self):
        itchat.logout()
        self.master.destroy()