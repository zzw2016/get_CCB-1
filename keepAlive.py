import requests
import json
import os
import logging
import time

def getUserInfo(cookies):
    headers = {
        'authority': 'jxjkhd1.kerlala.com',
        'user-agent': 'Mozilla/5.0 (Linux; Android 11; Redmi K30 5G Build/RKQ1.200826.002; wv) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/77.0.3865.120 MQQBrowser/6.2 TBS/045613 Mobile Safari/537.36 MMWEBID/6824 micromessenger/8.0.1.1841(0x28000151) Process/tools WeChat/arm64 Weixin NetType/WIFI Language/zh_CN ABI/arm64',
        'referer': 'https://jxjkhd1.kerlala.com/a/91/lPYNjdmN/fdtopic_v1/index',
    }

    r = requests.get('https://jxjkhd1.kerlala.com/Common/activity/getUserInfo/91/lPYNjdmN', headers=headers,cookies=cookies)
    return r.json()

def readConfig(configPath):
    if os.path.exists(configPath):
        with open(configPath,encoding='UTF-8') as fp:
            try:
                config = json.load(fp)
                return config
            except:
                logger.error('读取配置文件失败，请检查配置文件是否符合json语法')
                sys.exit(1)
    else:
        logger.error('配置文件不存在，请复制模板文件config.sample.json为config.json')
        sys.exit(2)

def createLog(logDir):
    # 日志输出控制台
    logging.basicConfig(level = logging.INFO,format = '%(asctime)s - %(levelname)s - %(message)s')
    logger = logging.getLogger(__name__)
    # 日志输入文件
    date = time.strftime("%Y-%m-%d-%H-%M-%S", time.localtime()) 
    logPath = '{}/{}.log'.format(logDir,date)
    if not os.path.exists(logDir):
        logger.warning("未检测到日志目录存在，开始创建logs目录")
        os.makedirs(logDir)
    fh = logging.FileHandler(logPath, mode='a', encoding='utf-8')
    fh.setFormatter(logging.Formatter("%(asctime)s - %(levelname)s - %(message)s"))
    logger.addHandler(fh)
    return logger

def cleanLog(logDir):
    logger.info("开始清理日志")
    cleanNum = 0
    files = os.listdir(logDir)
    for file in files:
        today = time.mktime(time.strptime(time.strftime("%Y-%m-%d-%H-%M-%S", time.localtime()),"%Y-%m-%d-%H-%M-%S"))
        logDate = time.mktime(time.strptime(file.split(".")[0],"%Y-%m-%d-%H-%M-%S"))
        dayNum = int((int(today) - int(logDate)) / (24 * 60 * 60))
        if dayNum > 7:
            os.remove("{}/{}".format(logDir,file))
            cleanNum += 1
            logger.info("已删除{}天前日志{}".format(dayNum,file))
    if cleanNum == 0:
        logger.info("未检测到过期日志，无需清理！")

rootDir = os.path.dirname(os.path.abspath(__file__))
configPath = rootDir + "/config.json"
logDir = rootDir + "/logs/keepAlive/"
logger = createLog(logDir)
config = readConfig(configPath)
logger.info('共获取到{}个用户，开始Cookie保活'.format(len(config['cookie'])))
for i in range(len(config['cookie'])):
    result = getUserInfo(config['cookie'][i])
    if result['status'] == 'success':
        logger.info('第{}个账号{}Cookie保活成功'.format(i+1,result['data']['nickname']))
    else:
        logger.error('第{}个账号已失效'.format(i+1))
cleanLog(logDir)
