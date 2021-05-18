## 抓包说明

1. 前往[龙支付奋斗季主会场](https://fission-events.ccbft.com/a/91/lPYNjdmN?u=37ff922b-ba7b-4fb0-b6f9-c28042297b75)，使用手机号登陆并报名首页天天抽奖活动

2. 在Cookie中抓取`XSRF-TOKEN`和`_session`参数并填入配置文件

## 使用方法

1. 安装git和python3

2. 克隆仓库

   ```
   git clone https://github.com/leeyiding/get_CCB.git && cd get_CCB
   ```

3. 安装依赖

   ```
   pip3 install pip -U
   pip3 config set global.index-url https://pypi.tuna.tsinghua.edu.cn/simple
   pip3 install -r requirements.txt
   ```

4. 复制配置文件模板

   ```
   cp ./config.sample.json ./config.json
   ```

   配置文件示例

   ```
   {
       "cookie": [
    		//账户1   
           {
               "XSRF-TOKEN": "",
               "_session": ""
           },
           //账户2
           {
               "XSRF-TOKEN": "",
               "_session": ""
           }
       ],
       "shareCode": {
            //奋斗季互助码   
           "common": [
              //助力码1
               "",
               //助力码2
               ""
           ],
            //母亲节活动互助码   
           "motherDay": [
               //助力码1
               "",
               //助力码2
               ""
           ],
           //学外汇活动互助码   
           "whcanswer": [
               //助力码1
               "",
               //助力码2
               ""
           ],
           //消保分会场知识大考验活动互助码   
           "xbanswer": [
               //助力码1
               "",
               //助力码2
               ""
           ],
           //消保分会场眼力大考验活动互助码   
           "xbpickon": [
               //助力码1
               "",
               //助力码2
               ""
           ],
           //商圈分会场活动互助码   
           "lctopic": [
               //助力码1
               "",
               //助力码2
               ""
           ]
       },
        //日志保存路径
        "logDir": "",
        //天天抽奖开关
        "dayDraw": false
   }
   ```

5. 添加定时任务

   `keepAlive.py`每三小时运行一次
   `main.py`每天早晨、晚上各运行一次，尽量不要凌晨运行、不要选择整点运行



