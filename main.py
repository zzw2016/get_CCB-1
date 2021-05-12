# Author: leeyiding(乌拉)
# Date: 2020-05-05
# Link: https://github.com/leeyiding/get_CCB
# Version: 0.10.3
# UpdateDate: 2020-05-12 13:39
# UpdateLog: 优化请求接口及Cookie有效性检测流程

import requests
import json
import os
import sys
import time
import re
import random
import urllib.parse
import logging

class getCCB():
    def __init__(self,cookies,shareCode):
        self.cookies = cookies
        self.ua = 'Mozilla/5.0 (Linux; Android 11; Redmi K30 5G Build/RKQ1.200826.002; wv) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/77.0.3865.120 MQQBrowser/6.2 TBS/045613 Mobile Safari/537.36 MMWEBID/6824 micromessenger/8.0.1.1841(0x28000151) Process/tools WeChat/arm64 Weixin NetType/WIFI Language/zh_CN ABI/arm64'
        shareCodeKeys = shareCode.keys()
        if(not 'common' in shareCodeKeys):
            shareCode['common'] = []
        if(not 'motherDay' in shareCodeKeys):
            shareCode['motherDay'] = []
        if(not 'whcanswer' in shareCodeKeys):
            shareCode['whcanswer'] = []
        if(not 'xbanswer' in shareCodeKeys):
            shareCode['xbanswer'] = []
        if(not 'xbpickon' in shareCodeKeys):
            shareCode['xbpickon'] = []
        if(not 'lctopic' in shareCodeKeys):
            shareCode['lctopic'] = []
        self.commonShareCode = shareCode['common'] + ["37ff922b-ba7b-4fb0-b6f9-c28042297b75"]
        self.motherDayShareCode = shareCode['motherDay']
        self.whcanswerShareCode = shareCode['whcanswer']
        self.xbanswerShareCode = shareCode['xbanswer']
        self.xbpickonShareCode = shareCode['xbpickon']
        self.lctopicShareCode = shareCode['lctopic']
        self.xsrfToken = self.cookies['XSRF-TOKEN'].replace('%3D','=')
        self.whcanswerFilePath = rootDir + '/whcanswer.json'
        self.xbanswerFilePath = rootDir + '/xbanswer.json'
        self.xbpickonFilePath = rootDir + '/xbpickon.json'


    def getApi(self,functionId,activityId='lPYNjdmN',params=()):
        '''
        通用GET请求接口
        '''
        url = 'https://fission-events.ccbft.com/{}/91/{}'.format(functionId,activityId)
        headers = {
            'authority': 'fission-events.ccbft.com',
            'user-agent': self.ua,
            'referer': 'https://fission-events.ccbft.com/a/91/lPYNjdmN/fdtopic_v1/index',
        }
        for i in range(5):
            try:
                r = requests.get(url, headers=headers, params=params, cookies=self.cookies)
                r.encoding = 'utf-8'
                if r.status_code == 200:
                    if re.findall('DOCTYPE',r.text):
                        return r.text
                    else:
                        return r.json()
                else:
                    logger.error('调用接口失败，等待10秒重试')
                    time.sleep(10)
            except:
                logger.error('调用接口失败，等待10秒重试')
                time.sleep(10)
                

    def postApi(self,functionId,data,activityId='lPYNjdmN'):
        '''
        通用POST请求接口
        '''
        url = 'https://fission-events.ccbft.com/{}/91/{}'.format(functionId,activityId)
        headers = {
            'authority': 'fission-events.ccbft.com',
            'x-xsrf-token': self.xsrfToken,
            'user-agent': self.ua,
            'origin': 'https://fission-events.ccbft.com',
            'referer': 'https://fission-events.ccbft.com/a/91/lPYNjdmN/fdtopic_v1/index',
            'content-type': 'application/json;charset=UTF-8',
        }
        for i in range(5):
            try:
                r = requests.post(url, headers=headers, data=data, cookies=self.cookies)
                r.encoding = 'utf-8'
                if r.status_code == 200:
                    if re.findall('DOCTYPE',r.text):
                        logger.error('Cookie已失效，请更新Cookie')
                        return r.text
                    else:
                        return r.json()
                else:
                    logger.error('调用接口失败，等待10秒重试')
                    time.sleep(10)
            except:
                logger.error('调用接口失败，等待10秒重试')
                time.sleep(10)


    def payCostApi(self,functionId,params):
        '''
        越花越赚活动GET请求接口
        '''
        url = 'https://event.ccbft.com/api/activity/nf/payCost/avtivity/{}'.format(functionId)
        headers = {
            'Accept': 'application/json, text/plain, */*',
            'User-Agent': self.ua,
            'Referer': self.location,
        }
        params = (
            ('activityCode', 'AP010202102041005765'),
            ('verFlag', 'act'),
        ) + params
        try:
            r = requests.get(url, headers=headers, params=params, cookies=self.cookies)
            return r.json()
        except:
            logger.error('调用接口失败，等待10秒重试')
            time.sleep(10)
            r = requests.get(url, headers=headers, params=params, cookies=self.cookies)
            return r.json()


    def checkCookie(self):
        checkResult = self.getApi('Common/activity/getUserInfo')
        if checkResult['status'] == 'success':
            return True
        else:
            logger.error('第{}个账号已失效'.format(i+1))
            return False


    def getUserInfo(self):
        '''
        获取账户信息
        '''
        userInfo = self.getApi('activity/fbtopic/userInfo')
        logger.info('用户{}信息获取成功'.format(userInfo['data']['nickname']))
        logger.info('已获得CC币总量{}，剩余CC币总量{}'.format(userInfo['data']['ccb_money'],userInfo['data']['remain_ccb_money']))
        logger.info('当前建筑等级{}级，已获得建设值总量{},升级还需建设值{}'.format(userInfo['data']['grade'],userInfo['data']['build_score'],userInfo['data']['need_build_score']))
        logger.info('您的助力码为：{}'.format(userInfo['data']['ident']))
        try:
            user_name = urllib.parse.quote(userInfo['data']['nickname'])
            addCodeResult = requests.get('http://47.100.61.159:10080/add?user={}&code={}&type={}'.format(user_name,userInfo['data']['ident'],"ccbcommon"))
            if addCodeResult.status_code == 200:
                logger.info('提交云端助力池成功')
            else:
                logger.error('提交云端助力池失败')
        except Exception as e:
            logger.error(e)


    def acceptCCB(self):
        '''
        领取每日CCB或建设值
        '''
        # 查询可领取的CC币
        ccbList = self.postApi('activity/fbtopic/ccbList',{})
        for i in range(len(ccbList['data'])):
            data = '{"id":"' + str(ccbList['data'][i]['task_id']) + '","result_id": "' + str(ccbList['data'][i]['id']) + '"}'
            if ccbList['data'][i]['type'] == 'dailyCcb':
                acceptCcbResult = self.postApi('activity/fbtopic/acceptCcb',data)
                logger.info('领取{}个每日CCB成功'.format(ccbList['data'][i]['ccb_num']))
            elif ccbList['data'][i]['type'] == 'task':
                acceptCcbResult = self.postApi('Component/task/draw',data)
                logger.info('领取{}建设值成功'.format(ccbList['data'][i]['ccb_num']))


    def doFdtopicTask(self):
        '''
        主会场完成任务
        '''
        logger.info('')
        logger.info('开始做日常任务')
        self.getUserInfo()
        activityInfo = self.getApi('Common/activity/getActivityInfo')
        if int(time.time()) < activityInfo['data']['end_time']:
            # 获取任务列表
            taskList = self.getApi('Component/task/lists')
            logger.info('共获取到{}个任务'.format(len(taskList['data']['task'])))
            for i in range(len(taskList['data']['task'])):
                logger.info('开始做任务{}【{}】'.format(i+1,taskList['data']['task'][i]['show_set']['name']))
                # 判断任务状态
                if taskList['data']['userTask'][i]['finish'] ==1:
                    logger.info('该任务已完成，无需重复执行')
                    # 领取邀请任务奖励
                    if taskList['data']['task'][i]['type'] == 'share':
                        data = '{"id":"' + taskList['data']['task'][i]['id'] + '"}'
                        acceptResult = self.postApi('Component/task/draw',data)
                        logger.info(acceptResult['message'])
                else:
                    # 判断任务类型
                    if taskList['data']['task'][i]['type'] == 'visit' or taskList['data']['task'][i]['type'] == 'other':
                        # 浏览类型任务
                        data = '{"id": "' + taskList['data']['task'][i]['id'] + '"}'
                        doTaskResult = self.postApi('Component/task/do',data)
                        logger.info(doTaskResult['message'])
                    elif taskList['data']['task'][i]['type'] == 'signin':
                        # 签到任务
                        signinResult = self.postApi('activity/autographnew/qdEvery',{},'5Z9WJoPK')
                        logger.info(signinResult['message'])
                        if signinResult['status'] == 'success':
                            logger.info('获得{}'.format(signinResult['data']['prize_name']))
                    elif taskList['data']['task'][i]['type'] == 'share':
                        pass
                    # 领取奖励
                    if taskList['data']['task'][i]['draw_type'] == 'number':
                        # 气泡类型奖励
                        self.acceptCCB()
                    elif taskList['data']['task'][i]['draw_type'] == 'accept':
                        # 按钮类型奖励
                        data = '{"id":"' + taskList['data']['task'][i]['id'] + '"}'
                        acceptResult = self.postApi('Component/task/draw',data)
                        logger.info(acceptResult['message'])
                    # 休息五秒，防止接口提示频繁 
                    time.sleep(5)
            # 助力好友
            self.doHelp()
            # 升级建筑
            self.buildingUp()
        else:
            logger.info('抱歉，该活动已结束')

    def getCommonCode(self):
        '''
        获取主会场互助码
        '''
        try:
            commonres = requests.get("http://47.100.61.159:10080/ccbcommon")
            if commonres.status_code == 200:
                commoncode = commonres.text.split('@')
                logger.info('从云端拉取到{}个互助码{}'.format(len(commoncode),commoncode))
            else:
                commoncode = []
        except:
            commoncode = []
        self.commonShareCode += commoncode

    def doHelp(self):
        '''
        助力任务
        '''
        logger.info('')
        logger.info('开始助力好友')
        # 拉取云端助力码
        self.getCommonCode()
        if len(self.commonShareCode) == 0:
            logger.info('未提供任何助力码')
        else:
            logger.info('您提供了{}个好友助力码'.format(len(self.commonShareCode)))
        for i in range(len(self.commonShareCode)):
            logger.info('开始助力好友{}'.format(i+1))
            self.getApi('a','lPYNjdmN',(('u', self.commonShareCode[i]),))
            time.sleep(2)

    def buildingUp(self):
        '''
        升级建筑
        '''
        logger.info('')
        logger.info('开始升级建筑')
        userInfo = self.getApi('activity/fbtopic/userInfo')
        if userInfo['data']['remainder_build_score'] >= userInfo['data']['next_grade_build_score']:
            buildingUpResult = self.postApi('activity/fbtopic/buildingUp',{})
            if len(buildingUpResult['data']['up_awards']['up_awards']) > 0:
                upAwardsName = buildingUpResult['data']['up_awards']['up_awards'][0]['name']
                logger.info('升级{}成功，获得奖励{}'.format(buildingUpResult['data']['up_building']['name'],upAwardsName))
            else:
                logger.info('升级{}成功，无奖励'.format(buildingUpResult['data']['up_building']['name']))
            # 继续检查是否能升级
            time.sleep(5)
            self.buildingUp()
        else:
            logger.info('建设值不足,距下一等级还需{}建设值'.format(userInfo['data']['need_build_score']))


    def doSubvenueTask(self):
        '''
        分会场 龙支付优惠集锦
        '''
        logger.info('')
        logger.info('开始做龙支付分会场任务')
        activityInfo = self.getApi('Common/activity/getActivityInfo','5Z9WxaPK')
        if int(time.time()) < activityInfo['data']['end_time']:
            # 获取任务列表
            taskList = self.getApi('activity/lzfsubvenue/getIndicatorList','5Z9WxaPK')
            logger.info('共获取到{}个任务'.format(len(taskList['data']['task'])))
            for i in range(len(taskList['data']['task'])):
                logger.info('开始做任务【{}】'.format(taskList['data']['task'][i]['indicator']['show_name']))
                if taskList['data']['task'][i]['day_complete'] == 1:
                    logger.info('该任务今日已完成，无需重复执行')
                elif taskList['data']['task'][i]['day_complete'] == 0:
                    data = '{"code": "' + taskList['data']['task'][i]['indicator']['code'] + '"}'
                    doTaskResult = self.postApi('activity/lzfsubvenue/visit',data,'5Z9WxaPK')
                    logger.info(doTaskResult)
                    if doTaskResult['message'] == 'ok':
                        logger.info('任务完成，获得5CC币')
                    time.sleep(5)
        else:
            logger.info('抱歉，该活动已结束')


    def doCarTask(self):
        '''
        车主分会场做任务、抽奖
        '''
        logger.info('')
        logger.info('开始做车主分会场任务')
        activityInfo = self.getApi('Common/activity/getActivityInfo','dmRe4rPD')
        if int(time.time()) < activityInfo['data']['end_time']:
            # 访问首页，获得三次抽奖机会
            self.getApi('a','dmRe4rPD/parallelsessions_v1/index',(('CCB_Chnl', '6000213'),))
            # 获取任务列表
            taskList = self.getApi('activity/parallelsessions/getIndicatorList','dmRe4rPD')
            logger.info('共获取到{}个任务'.format(len(taskList['data']['task'])))
            for i in range(len(taskList['data']['task'])):
                logger.info('开始做任务【{}】'.format(taskList['data']['task'][i]['indicator']['show_name']))
                if taskList['data']['task'][i]['day_complete'] == 1:
                    logger.info('该任务今日已完成，无需重复执行')
                elif taskList['data']['task'][i]['day_complete'] == 0:
                    data = '{"code": "' + taskList['data']['task'][i]['indicator']['code'] + '"}'
                    doTaskResult = self.postApi('activity/parallelsessions/visit',data,'dmRe4rPD')
                    logger.info(doTaskResult['message'])
            # 获取抽奖次数
            carIndexInfo = self.getApi('activity/parallelsessions/index','dmRe4rPD')
            logger.info('车主分会场剩余抽奖次数{}'.format(carIndexInfo['data']['remain_num']))
            # 抽奖
            if int(carIndexInfo['data']['remain_num']) > 0:
                for i in range(int(carIndexInfo['data']['remain_num'])):
                    drawResult = self.postApi('activity/parallelsessions/draw',{},'dmRe4rPD')
                    if drawResult['status'] == 'success':
                        logger.info(drawResult['data']['prizename'])
                    else:
                        logger.info(drawResult['message'])
                    # 休息四秒，防止接口频繁
                    time.sleep(4)
        else:
            logger.info('抱歉，该活动已结束')


    def draw(self):
        '''
        抽奖，每日10次机会
        抽奖策略：
        1. 若已进行抽奖次数小于3，则执行抽奖
        3. 总盈利达30 CC币跳出抽奖
        '''
        logger.info('')
        logger.info('开始天天抽奖')
        activityInfo = self.getApi('Common/activity/getActivityInfo','03ljx6mW')
        if int(time.time()) < activityInfo['data']['end_time']:
            # 检查报名状态
            drawStatus = self.getApi('Component/signup/status','03ljx6mW')
            if drawStatus['status'] == 'fail':
                logger.info('未报名，请前往天天抽奖进行报名')
            else:
                getUserCCBResult = self.getApi('Component/draw/getUserCCB','03ljx6mW')
                userRemainDrawNum = getUserCCBResult['data']['draw_day_max_num'] - int(getUserCCBResult['data']['user_day_draw_num'])
                if int(getUserCCBResult['data']['user_day_draw_num']) < 3:
                    logger.info('今日已抽奖次数小于3，开始执行抽奖')
                    breakTotalCCB = 30
                    drawTotalCCB = 0
                    for i in range(userRemainDrawNum):
                        drawResult = self.postApi('Component/draw/commonCcbDrawPrize',{},'03ljx6mW')
                        if drawResult['data']['prize_type'] == 'jccb':
                            logger.info(drawResult['message'] + drawResult['data']['prizename'])
                            prizeNum = int(re.findall('[0-9]*',drawResult['data']['prizename'])[0]) - 30
                            drawTotalCCB += prizeNum
                            logger.info('当前总盈利{}'.format(drawTotalCCB))
                        else:
                            logger.info(drawResult['message'] + drawResult['data']['prizename'])
                        # 判断总盈利
                        if drawTotalCCB >= breakTotalCCB:
                            logger.info('本轮抽奖总盈利已达{}CC币，退出抽奖'.format(breakTotalCCB))
                            break
                        # 休息5秒，避免接口频繁
                        time.sleep(5)
                else:
                    logger.info('今日已进行过{}次抽奖了,若有剩余次数可手动执行'.format(getUserCCBResult['data']['user_day_draw_num']))
        else:
            logger.info('抱歉，该活动已结束')


    def dayAnswer(self):
        '''
        奋斗学院每日一答
        无论对错，奖励均为10建设值
        '''
        logger.info('')
        logger.info('开始每日一答')
        activityInfo = self.getApi('Common/activity/getActivityInfo','jmX0aKmd')
        if int(time.time()) < activityInfo['data']['end_time']:
            # 获取用户答题信息
            userDataInfo = self.getApi('activity/dopanswer/getUserDataInfo','jmX0aKmd')
            if userDataInfo['data']['remain_num'] == 1:
                # 获取题目
                question = self.getApi('activity/dopanswer/getQuestion','jmX0aKmd')
                questionTitle =question['data']['all_question'][0]['question']['title']
                questionId = question['data']['all_question'][0]['question']['id']
                logger.info('问：{} id:{}'.format(questionTitle,questionId))
                for i in range(len(question['data']['all_question'][0]['option'])):
                    logger.info('选项{}：{}'.format(i+1,question['data']['all_question'][0]['option'][i]['title']))
                # 随机答题
                randomOption = random.randint(1,len(question['data']['all_question'][0]['option']))
                logger.info('随机选择选项{}'.format(randomOption))
                data = '{"answerId":"' + str(randomOption) +'","questionId":"' + str(questionId) + '"}'
                answerQuestionResult = self.postApi('activity/dopanswer/answerQuestion',data,'jmX0aKmd')
                logger.info('正确答案：选项{}'.format(answerQuestionResult['data']['right']))
                logger.info(answerQuestionResult['message'])
            else:
                logger.info('今日答题机会已用尽')
        else:
            logger.info('抱歉，该活动已结束')


    def mothersDayTask(self):
        '''
        母亲节晒妈活动
        '''
        logger.info('')
        logger.info('开始做 母亲节集赞得520CC币 活动')
        activityInfo = self.getApi('Common/activity/getActivityInfo','jmX08Ymd')
        if int(time.time()) < activityInfo['data']['end_time']:
            # 获取用户信息
            userInfo = self.getApi('activity/mumbit/getUserInfo','jmX08Ymd')
            logger.info('您的活动助力码为：{}'.format(userInfo['data']['ident']))
            try:
                user_name = urllib.parse.quote(userInfo['data']['nickname'])
                addCodeResult = requests.get('http://47.100.61.159:10080/add?user={}&code={}&type={}'.format(user_name,userInfo['data']['ident'],"ccbmother"))
                if addCodeResult.status_code == 200:
                    logger.info('提交云端助力池成功')
                else:
                    logger.error('提交云端助力池失败')
            except Exception as e:
                logger.error(e)
            judgeStatus = self.getApi('activity/mumbit/judgeStatus','jmX08Ymd')
            if judgeStatus['data']['ext'] == '':
                logger.info('您从未参加该活动，开始初始化活动')
                 # 设置标签
                data = '{"ext":"[{\\"title\\":\\"\u89C9\u5F97\u6211\u6C38\u8FDC\u5403\u4E0D\u9971\\",\\"thumbnail_url\\":\\"https://ccbhdimg.kerlala.com/hd/users/10461/20210430/8645701907.png\\",\\"isChoosed\\":true,\\"left\\":\\"0rem\\",\\"top\\":\\"2.6rem\\"}]"}'.encode("utf-8").decode("latin1")
                updatePhraseResult = self.postApi('activity/mumbit/updatePhrase',data,'jmX08Ymd')
                logger.info('初始化活动结果：'.format(updatePhraseResult['message']))
            userLaunchInfo = self.getApi('activity/mumbit/getUserLaunchInfo','jmX08Ymd',(('share_ident', userInfo['data']['ident']),))
            if userLaunchInfo['code'] == 2101:
                # 开启分享
                doUserLaunchResult = self.postApi('activity/mumbit/doUserLaunch',{},'jmX08Ymd',)
                logger.info('开启分享结果：'.format(doUserLaunchResult['message']))
            logger.info('当前账号已获赞{}，还需{}个点赞'.format(judgeStatus['data']['help_num'],judgeStatus['data']['need_help_num']))

            # 领取满助力奖励
            if int(judgeStatus['data']['help_num']) >= 20:
                logger.info('已达到领奖条件，开始领取奖励')
                getRewardResult = self.getApi('activity/mumbit/draw','jmX08Ymd')
                logger.info(getRewardResult['message'])

            # 助力好友
            logger.info('开始助力好友')
            # 拉取云端助力码
            self.getMothercode()
            if len(self.motherDayShareCode) == 0:
                logger.info('未发现任何助力码')
            else:
                logger.info('您提供了{}个好友助力码'.format(len(self.motherDayShareCode)))
            for i in range(len(self.motherDayShareCode)):
                userLaunchInfo = self.getApi('activity/mumbit/getUserLaunchInfo','jmX08Ymd',(('share_ident', self.motherDayShareCode[i]),))
                if userLaunchInfo['code'] == 2101:
                    logger.info('该好友未开启分享')
                else:
                    friendName = userLaunchInfo['data']['nickname']
                    launchId = userLaunchInfo['data']['launchId']
                    data = '{"launch_id":"' + str(launchId) +'","share_ident":"' + self.motherDayShareCode[i] + '"}'
                    doUserHelpResult = self.postApi('activity/mumbit/doUserHelp',data,'jmX08Ymd')
                    logger.info('助力好友{}结果：{}'.format(friendName,doUserHelpResult['message']))
                    if doUserHelpResult['message'] == '抱歉已达帮助上限':
                        logger.info('助力次数已达上限，跳出助力')
                        break
                    # 休息5秒，防止接口频繁
                    time.sleep(5)
        else:
            logger.info('抱歉，该活动已结束')
  

    def getMothercode(self):
        '''
        获取母亲节互助码
        '''
        try:
            motherres = requests.get("http://47.100.61.159:10080/ccbmother")
            if motherres.status_code == 200:
                mothercode = motherres.text.split('@')
                logger.info('从云端拉取到{}个互助码{}'.format(len(mothercode),mothercode))
            else:
                mothercode = []
        except:
            mothercode = []
        self.motherDayShareCode += mothercode


    def doWhcanswer(self):
        '''
        学外汇 得实惠活动答题、抽奖、助力
        '''
        logger.info('')
        logger.info('开始做 学外汇 得实惠 活动')
        # 读取题库
        if os.path.exists(self.whcanswerFilePath):
            with open(self.whcanswerFilePath,encoding='UTF-8') as fp:
                questionDict = json.load(fp)
        else:
            logger.info('题库不存在，请下载完整题库')
            return False
        # 读取活动信息
        activityInfo = self.getApi('Common/activity/getActivityInfo','dmRev1PD')
        if int(time.time()) < activityInfo['data']['end_time']:
            # 答题
            # 获取用户信息
            userInfo = self.getApi('Common/activity/getUserInfo','dmRev1PD')
            logger.info('您的活动助力码为：{}'.format(userInfo['data']['ident']))
            userDataInfo = self.getApi('activity/whcanswer/getUserDataInfo','dmRev1PD')
            if userDataInfo['data']['remain_num'] > 0:
                logger.info('今日剩余{}次答题机会'.format(userDataInfo['data']['remain_num']))
                for num in range(userDataInfo['data']['remain_num']):
                    logger.info('开始第{}轮答题'.format(num+1))
                    # 使用答题机会
                    self.getApi('activity/whcanswer/reduceNum','dmRev1PD')
                    # 获取题目
                    questionInfo = self.postApi('activity/whcanswer/getQuestion','{levelId: 1}','dmRev1PD')
                    # 查询正确答案ID
                    rightOptionsId = []
                    for questionId in questionInfo['data']['question_id']:
                        rightOptionsId.append(questionDict[str(questionId)]['rightOptionId'])
                    logger.info(rightOptionsId)
                    # 获取正确答案位序
                    rightOptionsNum = []
                    for i in range(len(questionInfo['data']['all_question'])):
                        for j in range(len(questionInfo['data']['all_question'][i]['option'])):
                            if questionInfo['data']['all_question'][i]['option'][j]['id'] == rightOptionsId[i]:
                                rightOptionsNum.append(j+1)
                                break
                    logger.info(rightOptionsNum)
                    # 开始答题
                    for i in range(len(questionInfo['data']['all_question'])):
                        logger.info('问题{}：{}'.format(i+1,questionInfo['data']['all_question'][i]['question']['title']))
                        for j in range(len(questionInfo['data']['all_question'][i]['option'])):
                            logger.info('选项{}：{}'.format(j+1,questionInfo['data']['all_question'][i]['option'][j]['title']))
                        # 提交答案
                        logger.info('选择选项{}'.format(rightOptionsNum[i]))
                        data = '{"levelId": 1, "questionId": ' + str(i+1) + ', "answerId":' + str(rightOptionsNum[i]) + '}'
                        answerResult = self.postApi('activity/whcanswer/answerQuestion',data,'dmRev1PD')
                        logger.info('当前得分{}'.format(answerResult['data']['curScore']))
                        # 休息3秒，防止接口频繁
                        time.sleep(3)
            else:
                logger.info('今日已无答题机会')

            # 抽奖
            # 获取剩余抽奖次数
            userDataInfo = self.getApi('activity/whcdraw/getUserDataInfo','lPYNEEmN')
            if int(userDataInfo['data']['drawUserExt']['remain_num']) > 0:
                logger.info('今日剩余抽奖次数{}'.format(userDataInfo['data']['drawUserExt']['remain_num']))
                for i in range(int(userDataInfo['data']['drawUserExt']['remain_num'])):
                    drawResult = self.getApi('activity/whcdraw/draw','lPYNEEmN')
                    logger.info(drawResult)
                    # 休息5秒，防止接口频繁
                    time.sleep(5)
            else:
                logger.info('今日已无抽奖机会')

            # 助力
            logger.info('开始助力好友')
            if len(self.whcanswerShareCode) == 0:
                logger.info('未提供任何助力码')
            else:
                logger.info('您提供了{}个好友助力码'.format(len(self.whcanswerShareCode)))
            for i in range(len(self.whcanswerShareCode)):
                logger.info('开始助力好友{}'.format(i+1))
                self.getApi('a','dmRev1PD',(('u', self.whcanswerShareCode[i]),))
                time.sleep(3)
        else:
            logger.info('抱歉，该活动已结束')


    def doXbanswer(self):
        '''
        消保分会场知识大考验答题、抽奖、助力
        '''
        logger.info('')
        logger.info('开始做 消保分会场知识大考验 活动')
        # 读取题库
        if os.path.exists(self.xbanswerFilePath):
            with open(self.xbanswerFilePath,encoding='UTF-8') as fp:
                questionDict = json.load(fp)
        else:
            logger.info('题库不存在，请下载完整题库')
            return False
        # 读取活动信息
        activityInfo = self.getApi('Common/activity/getActivityInfo','03lj14mW')
        if int(time.time()) < activityInfo['data']['end_time']:
            # 答题
            # 获取用户信息
            userInfo = self.getApi('Common/activity/getUserInfo','03lj14mW')
            logger.info('您的活动助力码为：{}'.format(userInfo['data']['ident']))
            userDataInfo = self.getApi('activity/xbanswer/getUserDataInfo','03lj14mW')
            if userDataInfo['data']['remain_num'] > 0:
                logger.info('今日剩余{}次答题机会'.format(userDataInfo['data']['remain_num']))
                for num in range(userDataInfo['data']['remain_num']):
                    logger.info('开始第{}轮答题'.format(num+1))
                    # 随机答题等级
                    levelId = random.randint(1,4)
                    logger.info('随机选择等级{}题目'.format(levelId))
                    # 使用答题机会
                    self.getApi('activity/xbanswer/reduceNum','03lj14mW')
                    # 获取题目
                    data = '{"levelId":"' + str(levelId) + '"}'
                    questionInfo = self.postApi('activity/xbanswer/getQuestion',data,'03lj14mW')
                    # 查询正确答案ID
                    rightOptionsId = []
                    for questionId in questionInfo['data']['question_id']:
                        rightOptionsId.append(questionDict[str(questionId)]['rightOptionId'])
                    logger.info(rightOptionsId)
                    # 获取正确答案位序
                    rightOptionsNum = []
                    for i in range(len(questionInfo['data']['all_question'])):
                        for j in range(len(questionInfo['data']['all_question'][i]['option'])):
                            if questionInfo['data']['all_question'][i]['option'][j]['id'] == rightOptionsId[i]:
                                rightOptionsNum.append(j+1)
                                break
                    logger.info(rightOptionsNum)
                    # 开始答题
                    for i in range(len(questionInfo['data']['all_question'])):
                        logger.info('问题{}：{}'.format(i+1,questionInfo['data']['all_question'][i]['question']['title']))
                        for j in range(len(questionInfo['data']['all_question'][i]['option'])):
                            logger.info('选项{}：{}'.format(j+1,questionInfo['data']['all_question'][i]['option'][j]['title']))
                        # 提交答案
                        logger.info('选择选项{}'.format(rightOptionsNum[i]))
                        data = '{"levelId": ' + str(levelId) + ', "questionId": ' + str(i+1) + ', "answerId":' + str(rightOptionsNum[i]) + '}'
                        answerResult = self.postApi('activity/xbanswer/answerQuestion',data,'03lj14mW')
                        logger.info('当前得分{}'.format(answerResult['data']['curScore']))
                        # 休息5秒，防止接口频繁
                        time.sleep(5)
            else:
                logger.info('今日已无答题机会')

            # 抽奖
            # 获取剩余抽奖次数
            userDataInfo = self.getApi('activity/xbdraw/getUserDataInfo','jmX05Qmd')
            if int(userDataInfo['data']['drawUserExt']['remain_num']) > 0:
                logger.info('今日剩余抽奖次数{}'.format(userDataInfo['data']['drawUserExt']['remain_num']))
                for i in range(int(userDataInfo['data']['drawUserExt']['remain_num'])):
                    drawResult = self.getApi('activity/xbdraw/draw','jmX05Qmd')
                    logger.info(drawResult)
                    # 休息5秒，防止接口频繁
                    time.sleep(5)
            else:
                logger.info('今日已无抽奖机会')

            # 助力
            logger.info('开始助力好友')
            if len(self.xbanswerShareCode) == 0:
                logger.info('未提供任何助力码')
            else:
                logger.info('您提供了{}个好友助力码'.format(len(self.xbanswerShareCode)))
            for i in range(len(self.xbanswerShareCode)):
                logger.info('开始助力好友{}'.format(i+1))
                self.getApi('a','03lj14mW',(('u', self.xbanswerShareCode[i]),))
                time.sleep(3)
        else:
            logger.info('抱歉，该活动已结束')


    def doXbpickon(self):
        '''
        消保分会场眼力大考验答题、抽奖、助力
        '''
        logger.info('')
        logger.info('开始做 消保分会场眼力大考验 活动')
        # 读取题库
        if os.path.exists(self.xbpickonFilePath):
            with open(self.xbpickonFilePath,encoding='UTF-8') as fp:
                questionDict = json.load(fp)
        else:
            logger.info('题库不存在，请下载完整题库')
            return False
        # 读取活动信息
        activityInfo = self.getApi('Common/activity/getActivityInfo','QPyo86Zj')
        if int(time.time()) < activityInfo['data']['end_time']:
            # 答题
            # 获取用户信息
            userInfo = self.getApi('Common/activity/getUserInfo','QPyo86Zj')
            logger.info('您的活动助力码为：{}'.format(userInfo['data']['ident']))
            userDataInfo = self.getApi('activity/xbpickon/getUserDataInfo','QPyo86Zj')
            if userDataInfo['data']['remain_num'] > 0:
                logger.info('今日剩余{}次答题机会'.format(userDataInfo['data']['remain_num']))
                for num in range(userDataInfo['data']['remain_num']):
                    logger.info('开始第{}轮答题'.format(num+1))
                    # 使用答题机会
                    self.getApi('activity/xbpickon/reduceNum','QPyo86Zj')
                    # 获取题目
                    questionInfo = self.getApi('activity/xbpickon/getQuestion','QPyo86Zj')
                    questionWordList = []
                    rightIdList = []
                    rightWordList = []
                    for i in range(len(questionInfo['data'])):
                        questionWordList.append(questionInfo['data'][i]['word'])
                        if questionDict[str(questionInfo['data'][i]['id'])]['isRight'] == True:
                            rightIdList.append(str(questionInfo['data'][i]['id']))
                            rightWordList.append(questionInfo['data'][i]['word'])
                    strQuestionIds = ','.join(rightIdList)
                    logger.info('请在下列词汇中找出所有正面词汇{}'.format(questionWordList))
                    logger.info(rightIdList)
                    logger.info('选择{}'.format(rightWordList))
                    data = '{"answerId":"' + strQuestionIds + '"}'
                    answerResult = self.postApi('activity/xbpickon/answerQuestion',data,'QPyo86Zj')
                    # 休息5秒，防止接口频繁
                    time.sleep(5)
            else:
                logger.info('今日已无答题机会')

            # 抽奖
            # 获取剩余抽奖次数
            userDataInfo = self.getApi('activity/xbpickon/getUserDataInfo','QPyo86Zj')
            if int(userDataInfo['data']['draw_remain_num']) > 0:
                logger.info('今日剩余抽奖次数{}'.format(userDataInfo['data']['draw_remain_num']))
                for i in range(int(userDataInfo['data']['draw_remain_num'])):
                    drawResult = self.getApi('activity/xbpickon/draw','QPyo86Zj')
                    if drawResult['status'] == 'success':
                        logger.info('获得{}'.format(drawResult['data']['prizename']))
                    else:
                        logger.info(drawResult)
                    # 休息5秒，防止接口频繁
                    time.sleep(5)
            else:
                logger.info('今日已无抽奖机会')

            # 助力
            logger.info('开始助力好友')
            if len(self.xbpickonShareCode) == 0:
                logger.info('未提供任何助力码')
            else:
                logger.info('您提供了{}个好友助力码'.format(len(self.xbpickonShareCode)))
            for i in range(len(self.xbpickonShareCode)):
                logger.info('开始助力好友{}'.format(i+1))
                self.getApi('a','QPyo86Zj',(('u', self.xbpickonShareCode[i]),))
                time.sleep(3)
        else:
            logger.info('抱歉，该活动已结束')
        

    def doPayCost(self):
        '''
        龙支付越花越赚每日领奖
        '''
        logger.info('')
        logger.info('开始领取龙支付越花越赚奖励')
        # 获取openID
        headers = {
            'authority': 'jxjkhd.kerlala.com',
            'user-agent': self.ua,
            'referer': 'https://fission-events.ccbft.com/a/91/lPYNjdmN/fdtopic_v1/index',
        }
        params = (
            ('url', 'https://event.ccbft.com/ccbact/m3007/AP010202102041005765-act.html?CCB_Chnl=6000210'),
        )
        oauthResult = requests.get('https://fission-events.ccbft.com/oauth/carry/91/CCBFFGY001', headers=headers, params=params, cookies=self.cookies, allow_redirects=False)
        if oauthResult.status_code == 302:
            self.location = oauthResult.headers['Location']
            kerlalaOpenid = re.findall('openid=([a-z0-9\-]*)',self.location)[0]
        else:
            return False

        # 获取活动及用户信息
        activityDetail = self.payCostApi('queryActivityDetail',(('kerlalaOpenid', kerlalaOpenid),))
        if (int(round(time.time()*1000))) < activityDetail['data']['endTime']:
            if 'userInfo' in activityDetail['data']:
                signsInfo = activityDetail['data']['userInfo']['signs']
                for i in range(len(signsInfo)):
                    if signsInfo[i]['received'] == 0:
                        logger.info('第{}天奖励可领取'.format(signsInfo[i]['continueDays']))
                        date = signsInfo[i]['signInDate']
                        userId = activityDetail['data']['userInfo']['userId']
                        taskId = activityDetail['data']['tasks'][0]['taskId']
                        awardResult = self.payCostApi('activityRedeemPoint',(('userId', userId),('taskId', taskId),('date', date),))
                        logger.info(awardResult)
                    else:
                        logger.info('第{}天暂无奖励可领取'.format(signsInfo[i]['continueDays']))
            else:
                logger.info('未报名，请前往活动主页报名')
        else:
            logger.info('抱歉，该活动已结束')

    
    def doLctopicTask(self):
        '''
        建行社区商圈专属会场日常任务、助力、砸金蛋
        '''
        logger.info('')
        logger.info('开始做社区商圈专属会场任务')
        activityInfo = self.getApi('Common/activity/getActivityInfo','kZMNeB3W')
        if int(time.time()) < activityInfo['data']['end_time']:
            # 获取用户信息
            userInfo = self.getApi('Common/activity/getUserInfo','kZMNeB3W')
            logger.info('您的活动助力码为：{}'.format(userInfo['data']['ident']))
            try:
                user_name = urllib.parse.quote(userInfo['data']['nickname'])
                addCodeResult = requests.get('http://47.100.61.159:10080/add?user={}&code={}&type={}'.format(user_name,userInfo['data']['ident'],"ccblctopic"))
                if addCodeResult.status_code == 200:
                    logger.info('提交云端助力池成功')
                else:
                    logger.error('提交云端助力池失败')
            except Exception as e:
                logger.error(e)
            # 访问首页，获得一次抽奖机会
            self.getApi('a','kZMNeB3W/index')
            # 获取任务列表
            taskList = self.getApi('activity/community/getTaskList','kZMNeB3W')
            # 日常任务
            logger.info('共获取到{}个日常任务'.format(len(taskList['data']['task']['loop'])))
            for i in range(len(taskList['data']['task']['loop'])):
                logger.info('开始做任务{}【{}】'.format(i+1,taskList['data']['task']['loop'][i]['show_set']['name']))
                if taskList['data']['userTask']['loop'][i]['finish'] == 0:
                    if taskList['data']['task']['loop'][i]['type'] == 'visit':
                        data = '{"id":"' + taskList['data']['task']['loop'][i]['id'] + '"}'
                        dotaskResult = self.postApi('Component/task/do',data,'kZMNeB3W')
                        logger.info(dotaskResult['message'])
                        drawResult = self.postApi('Component/task/draw',data,'kZMNeB3W')
                        logger.info(drawResult['message'])
                    time.sleep(5)
                else:
                    logger.info('该任务已完成，无需重复执行')
                    # 邀请任务领奖
                    if taskList['data']['task']['loop'][i]['type'] == 'share':
                        data = '{"id":"' + taskList['data']['task']['loop'][i]['id'] + '"}'
                        drawResult = self.postApi('Component/task/draw',data,'kZMNeB3W')
                        logger.info(drawResult['message'])
            # 单次任务
            logger.info('共获取到{}个单次任务'.format(len(taskList['data']['task']['once'])))
            for i in range(len(taskList['data']['task']['once'])):
                logger.info('开始做任务{}【{}】'.format(i+1,taskList['data']['task']['once'][i]['show_set']['name']))
                if taskList['data']['userTask']['once'][i]['finish'] == 0:
                    if taskList['data']['task']['once'][i]['type'] == 'visit':
                        data = '{"id":"' + taskList['data']['task']['once'][i]['id'] + '"}'
                        dotaskResult = self.postApi('Component/task/do',data,'kZMNeB3W')
                        logger.info(dotaskResult['message'])
                        drawResult = self.postApi('Component/task/draw',data,'kZMNeB3W')
                        logger.info(drawResult['message'])
                    else:
                        logger.info('请手动完成')
                else:
                    logger.info('该任务已完成，无需重复执行')
            # 助力
            logger.info('开始助力好友')
            logger.info(self.lctopicShareCode)
            self.getLctopicode()
            if len(self.lctopicShareCode) == 0:
                logger.info('未提供任何助力码')
            else:
                logger.info('您提供了{}个好友助力码'.format(len(self.lctopicShareCode)))
            for i in range(len(self.lctopicShareCode)):
                logger.info('开始助力好友{}'.format(i+1))
                self.getApi('a','kZMNeB3W',(('u', self.lctopicShareCode[i]),))
                time.sleep(3)
            # 抽奖
            logger.info('开始砸金蛋')
            indexInfo = self.getApi('activity/community/getIndex','kZMNeB3W')
            remainNum = int(indexInfo['data']['remain_num'])
            logger.info('当前剩余{}次机会'.format(remainNum))
            if int(remainNum) > 0:
                for i in range(remainNum):
                    drawPrizeResult =  self.postApi('activity/community/commonDrawPrize',{},'kZMNeB3W')
                    if drawPrizeResult['status'] == 'fail':
                        logger.info(drawPrizeResult['message'])
                    else:
                        logger.info('抽中{}'.format(drawPrizeResult['data']['prizename']))
                    time.sleep(5)
        else:
            logger.info('抱歉，该活动已结束')

    def getLctopicode(self):
        '''
        获取商圈分会场互助码
        '''
        try:
            lctopicres = requests.get("http://47.100.61.159:10080/ccblctopic")
            if lctopicres.status_code == 200:
                lctopiccode = lctopicres.text.split('@')
                logger.info('从云端拉取到{}个互助码{}'.format(len(lctopiccode),lctopiccode))
            else:
                lctopiccode = []
        except:
            lctopiccode = []
        self.lctopicShareCode += lctopiccode


    def main(self):
        try:
            # 主会场活动
            self.doFdtopicTask()
            # 龙支付分会场活动
            self.doSubvenueTask()
            # 车主分会场活动
            self.doCarTask()
            # 天天抽奖活动
            self.draw()
            # 每日一答
            self.dayAnswer()
            # 母亲节晒妈活动
            self.mothersDayTask()
            # 学外汇 得实惠活动
            self.doWhcanswer()
            # 消保分会场知识大考验
            self.doXbanswer()
            # 消保分会场眼力大考验
            self.doXbpickon()
            # 越花越赚领奖
            self.doPayCost()
            # 社区商圈专属会场
            self.doLctopicTask()
        except Exception as e:
            logger.error(e)
    
def readConfig(configPath):
    if os.path.exists(configPath):
        with open(configPath,encoding='UTF-8') as fp:
            try:
                config = json.load(fp)
                return config
            except:
                print('读取配置文件失败，请检查配置文件是否符合json语法')
                sys.exit(1)
    else:
        print('配置文件不存在，请复制模板文件config.sample.json为config.json')
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

if __name__ == '__main__':
    global rootDir
    rootDir = os.path.dirname(os.path.abspath(__file__))
    configPath = rootDir + "/config.json"
    config = readConfig(configPath)
    logDir = rootDir + "/logs/main/"
    if 'logDir' in config:
        if config['logDir'] != '':
            logDir = config['logDir'] + "/ccb_main/"
    global logger
    logger = createLog(logDir)
    for i in range(len(config['cookie'])):
        user = getCCB(config['cookie'][i],config['shareCode'])
        if user.checkCookie():
            user.main()
        else:
            logger.error('账号{}已失效，请及时更新Cookie'.format(i+1))
        logger.info('')
        logger.info('')
        logger.info('')
    cleanLog(logDir)
