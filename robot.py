import itchat
import logging
import time
import json
import robotui
logger = logging.getLogger()
startNowYMD = time.strftime("%Y-%m-%d", time.localtime())
try:
    with open('config.json', encoding='utf-8') as config:
        config = json.loads(config.read())
        logging.basicConfig(level=config["log"]["level"],filename='info.log',filemode='w')
except Exception as e:
    logger.error("配置文件异常 %s" % e.args)

@itchat.msg_register(itchat.content.INCOME_MSG, isGroupChat = True)
def ListenMsgGroup(msg):
    try:
        result = vaildGroupsRules(msg,config)
        if result:
            loginfo="接收到需要自动回复消息----"+"接收时间"+time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())+"发送人："+msg["ActualNickName"]
            printfInfo(loginfo)
            itchat.send(result, msg['FromUserName'])
            loginfo="回复消息----"+"回复时间"+time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())+"消息内容："+result
            printfInfo(loginfo)
    except Exception as e:
        loginfo="异常"+"接收时间"+e.args
        printfInfo(loginfo)

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
    nickName=app.removeEmoji(msg["User"]["NickName"])
    if(nickName == groupRule["groupName"]):
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
            actualNickName=msg['ActualNickName']
            if actualNickName.find(user['userName'])>=0:
                result = user["replyMsg"]
                break
    return result

def printfInfo(loginfo):
    app.logTextBoxInsert(loginfo)
    logger.info(loginfo)


if __name__=='__main__':
    app = robotui.Application()
    # to do
    app.mainloop()

