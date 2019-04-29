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
startNowYMD = time.strftime("%Y-%m-%d", time.localtime())
logging.basicConfig(level=logging.INFO,filename='info.log',filemode='w')
def configByWxServerInfo(self):
    self.cleanInfo()
    try:
        with open('config.json', encoding='utf-8') as configJsonFile:
            config.config = json.loads(configJsonFile.read())
            if len(config.config["rules"]):
                chatrooms = itchat.get_chatrooms(update=True)
                for rule in config.config["rules"]:
                    if len(rule["groupRules"]):
                        for groupRule in rule["groupRules"]:
                            for chatroom in chatrooms:
                                chatroom = itchat.update_chatroom(chatroom['UserName'])
                                groupInfo=utils.removeEmoji(chatroom["NickName"])
                                if(utils.vaildName(groupInfo,groupRule["groupName"])):
                                    self.setGroupInfo(groupInfo)
                                    groupRule["groupName"]=chatroom["UserName"]
                                    for friend in chatroom['MemberList']:
                                        displayName=utils.removeEmoji(friend["DisplayName"])
                                        nickName=utils.removeEmoji(friend["NickName"])
                                        if len(groupRule["users"]):
                                            for user in groupRule["users"]:
                                                if displayName:
                                                    if utils.vaildName(displayName,user['userName']):
                                                        usersInfo="--"+nickName+"--"+displayName
                                                        self.setUsersInfo(usersInfo)
                                                        user['userName']=friend["UserName"]
                                                elif nickName:
                                                    if utils.vaildName(nickName,user['userName']):
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
                            ct = time.time()
                            local_time = time.localtime(ct)
                            data_head = time.strftime("%Y-%m-%d %H:%M:%S", local_time)
                            data_secs = (ct - int(ct)) * 1000
                            time_stamp = "%s.%03d" % (data_head, data_secs)
                            loginfo=threadInfo+"接收到消息----"+"接收时间"+time_stamp+"----"+m['Content']
                            printfInfo(self,loginfo)
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
    if '@@' in m["FromUserName"]:
        r = re.match('(@[0-9a-z]*?):<br/>(.*)$', m['Content'])
        if r:
            actualUserName, content = r.groups()
        m['ActualUserName'] = actualUserName
        result = vaildGroupsRules(m,config.config)
        if(result):
            itchat.send(result, m['FromUserName'])
            ct = time.time()
            local_time = time.localtime(ct)
            data_head = time.strftime("%Y-%m-%d %H:%M:%S", local_time)
            data_secs = (ct - int(ct)) * 1000
            time_stamp = "%s.%03d" % (data_head, data_secs)
            loginfo="回复消息----"+"回复时间"+time_stamp+"消息内容："+result
            printfInfo(self,loginfo)


# 验证规则是否进行自动回复
def vaildGroupsRules(msg,config):
    if len(config["rules"]):
        for rule in config["rules"]:
            if len(rule["groupRules"]):
                for groupRule in rule["groupRules"]:
                    return vaildGroup(msg,groupRule)
            else:
                return False
    else:
        return False

# 验证群规则
def vaildGroup(msg,groupRule):
    if(msg["FromUserName"] == groupRule["groupName"]):
        return vaildTimeRange(msg,groupRule)
    else:
        return False

# 验证时间区间
def vaildTimeRange(msg,groupRule):
    nowYMD = time.strftime("%Y-%m-%d", time.localtime())
    nowHM = time.strftime("%H:%M%S", time.localtime())
    if len(groupRule["timeRanges"]):
        for groupTime in groupRule["timeRanges"]:
            if startNowYMD!=nowYMD:
                groupTime["sendCcount"]=0
                startNowYMD = time.strftime("%Y-%m-%d", time.localtime())

            times = groupTime["timeRange"].split("-")
            if(times[0] <= nowHM <= times[1]):
                result = vaildUser(msg,groupRule)
                if(groupRule["sendOnlyOne"]):
                    if(groupTime["sendCcount"]<=0):
                        if result:
                            groupTime["sendCcount"]=groupTime["sendCcount"]+1
                            return result
                            break
                        else:
                            return result
                            break
                else:
                    if result:
                        groupTime["sendCcount"]=groupTime["sendCcount"]+1
                        return result
                        break
                    else:
                        return result
                        break
    else:
        return False

# 验证发送者并返回回复消息
def vaildUser(msg,groupRule):
    result = False
    if len(groupRule["users"]):
        for user in groupRule["users"]:
            if msg['ActualUserName'] and msg['ActualUserName']==user['userName']:
                result = user["replyMsg"]
                break
    return result

def printfInfo(self,loginfo):
    self.logTextBoxInsert(utils.removeEmoji(loginfo))
    logger.info(utils.removeEmoji(loginfo))

if __name__=='__main__':
    robotui_instance = robotui.Application()
    # to do
    robotui_instance.mainloop()
