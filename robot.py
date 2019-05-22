import re
import itchat
import traceback, logging
import time
import json
import threading
import robotui
import utils,config
import requests
logger = logging.getLogger()
logging.basicConfig(level=logging.INFO,filename='info.log',filemode='w')
def configByWxServerInfo(self):
    self.cleanInfo()
    try:
        with open('config.json', encoding='utf-8') as configJsonFile:
            config.config = json.loads(configJsonFile.read())
            config.startNowYMD = time.strftime("%Y-%m-%d", time.localtime())
            if(config.config["groupRule"]):
                chatrooms = itchat.get_chatrooms(update=True)
                for chatroom in chatrooms:
                    chatroom = itchat.update_chatroom(chatroom['UserName'])
                    groupInfo=utils.removeEmoji(chatroom["NickName"])
                    if(utils.vaildName(groupInfo,config.config["groupRule"]["groupName"],config.config["groupRule"]["likeMatching"])):
                        self.setGroupInfo(groupInfo)
                        config.config["groupRule"]["groupName"]=chatroom["UserName"]
                        for friend in chatroom['MemberList']:
                            displayName=utils.removeEmoji(friend["DisplayName"])
                            nickName=utils.removeEmoji(friend["NickName"])
                            if len(config.config["groupRule"]["users"]):
                                for user in config.config["groupRule"]["users"]:
                                    if displayName:
                                        if utils.vaildName(displayName,user['userName'],user['likeMatching']):
                                            usersInfo="--"+nickName+"--"+displayName
                                            self.setUsersInfo(usersInfo)
                                            user['userName']=friend["UserName"]
                                    elif nickName:
                                        if utils.vaildName(nickName,user['userName'],user['likeMatching']):
                                            usersInfo="--"+nickName+"--"+displayName
                                            self.setUsersInfo(usersInfo)
                                            user['userName']=friend["UserName"]
                        self.setUsersInfo(groupInfo)
        loginfo=str(config.config)
        printfInfo(self,loginfo)
    except Exception as e:
        loginfo="配置文件异常" +e.args
        printfInfo(self,loginfo)

def start_receiving(self):
    itchat.originInstance.alive = True
    def maintain_loop(self,threadInfo):
        retryCount = 0
        while itchat.originInstance.alive:
            try:
                i = itchat.sync_check()
                if i is None:
                    itchat.originInstance.receivingRetryCount=itchat.originInstance.receivingRetryCount-1
                    if itchat.originInstance.receivingRetryCount<0:
                        self.alive = False
                        itchat.logout()
                        self.exitCallback()
                elif i == '0':
                    pass
                else:
                    msgList, contactList = itchat.get_msg()
                    if msgList:
                        for m in msgList:
                            try:
                                vaildAndAutoSend(self,m)
                            except Exception as e:
                                loginfo=e.args
                                printfInfo(self,loginfo)
                retryCount = 0
            except requests.exceptions.ReadTimeout:
                pass
            except:
                retryCount += 1
                logger.error(traceback.format_exc())
        itchat.logout()
        self.exitCallback()
        logger.info('LOG OUT!')
    receiveThread = threading.Thread(target=maintain_loop,args=(self,"receiveThread"))
    receiveThread.setDaemon(True)
    receiveThread.start()

def vaildAndAutoSend(self,m):
    if m["FromUserName"]==config.config["groupRule"]["groupName"]:
        result = vaildTimeRange(m,config.config["groupRule"])
        if(result):
            itchat.send_msg(result, m['FromUserName'])
            loginfo="接收到消息----"+m['Content']
            printfInfo(self,loginfo)
            loginfo="回复消息----"+"消息内容："+result
            printfInfo(self,loginfo)

# 验证时间区间
def vaildTimeRange(msg,groupRule):
    nowYMD = time.strftime("%Y-%m-%d", time.localtime())
    nowHM = time.strftime("%H:%M%S", time.localtime())
    if len(groupRule["users"]):
        for user in groupRule["users"]:
            if nowYMD!=config.startNowYMD:
                user["sendCcount"]=0
                config.startNowYMD = time.strftime("%Y-%m-%d", time.localtime())
            times = user["timeRange"].split("-")
            if(times[0] <= nowHM <= times[1]):
                if(groupRule["sendOnlyOne"]):
                    if(user["sendCcount"]<=1):
                        result = user["replyMsg"]
                        user["sendCcount"]=user["sendCcount"]+1
                        return result
                        #if msg['Content'] and user['userName'] in msg['Content']:
                else:
                    result = user["replyMsg"]
                    user["sendCcount"]=user["sendCcount"]+1
                    return result
                    #if msg['Content'] and user['userName'] in msg['Content']:

        return False
    else:
        return False

def printfInfo(self,loginfo):
    self.logTextBoxInsert(utils.removeEmoji(loginfo))
    logger.info(utils.removeEmoji(loginfo))

if __name__=='__main__':
    robotui_instance = robotui.Application()
    # to do
    robotui_instance.mainloop()
