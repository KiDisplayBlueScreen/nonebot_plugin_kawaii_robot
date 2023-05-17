from cmath import log
from nonebot.plugin.on import on_message,on_notice,on,on_command
from nonebot.adapters import Bot as BaseBot
from nonebot.message import event_postprocessor
import time,datetime,json
from nonebot.rule import to_me
from nonebot.permission import SUPERUSER
from nonebot.params import CommandArg
from nonebot.log import logger
from apscheduler.triggers.interval import IntervalTrigger
from nonebot import require
from bs4 import BeautifulSoup
from nonebot.adapters.onebot.v11 import (
    GROUP,
    GroupMessageEvent,
    Message,
    MessageEvent,
    MessageSegment,
    PokeNotifyEvent,
    GroupRecallNoticeEvent,
    PrivateMessageEvent,
    GroupIncreaseNoticeEvent,
    Bot,
)
from typing import Any, Dict, Optional
import nonebot
import asyncio
from random import *
import pathlib
import re
import os
from PIL import Image
from io import BytesIO
import requests
from .utils import *
from .config import Config
from .AntiRecall import *

# 加载全局配置
global_config = nonebot.get_driver().config
leaf = Config.parse_obj(global_config.dict())

reply_type = leaf.leaf_reply_type
poke_rand = leaf.leaf_poke_rand

repeater_limit = leaf.leaf_repeater_limit
interrupt = leaf.leaf_interrupt

ignore = leaf.leaf_ignore
group_list=[]
# 配置合法检测

if repeater_limit[0] < 2 or repeater_limit[0] > repeater_limit[1]:
    raise Exception('config error: repeater_limit')

# 权限判断

if leaf.leaf_permission == "GROUP":
    permission = GROUP
else:
    permission = None

#获取表情包路径
img_path = os.path.join(os.path.dirname(__file__), "龙")
all_file_name = os.listdir(img_path)
require("nonebot_plugin_apscheduler")
from nonebot_plugin_apscheduler import scheduler


Trigger = IntervalTrigger(minutes=30,jitter=10)
scheduler.add_job(func=Check,trigger=Trigger)  #添加一个定时任务, 到时间后执行func的函数

Recall = on_notice()
@Recall.handle()
async def Recall_handle(bot:Bot, event: GroupRecallNoticeEvent):
          if str(event.user_id) != str(bot.self_id):
              mid = event.message_id
              gid = event.group_id
              uid = event.user_id  #被撤回人Q号
              oid = event.operator_id   #撤回人Q号
              if uid == oid and uid in Bot_QID:
                 await Recall.finish()
              userinfo = await bot.get_group_member_info(group_id = gid, user_id = uid)
              Nickname=userinfo['nickname']
              #logger.info(f"username:{Nickname}")
              SelfRecall = 0
              Text_to_send1 = "哦~有人撤回了他的消息, 让我来看看他说了什么:"
              Text_to_send2 ="\r\n天哪 这也太~劲爆了⑧~怪不得要撤回呢♥让我们为他献上衷心的祝福~†升天†"
              Text_to_MakeSticker = ["唉怀孕了","怎么办"]
              Text_to_MakeSticker2 = ["管理员被我干怀孕了"]
              Avatar_FileName=await GetAvatar(str(uid))
              ImageList = [Avatar_FileName]
              if uid!=oid:
                 Text_to_send1="唉~管理员又在撤回别人的消息了,权蛆真的是~让我来看看他说了什么:"
                 IO_sticker = await StickerGen(ImageList,Text_to_MakeSticker2,Nickname)
              else:
                 IO_sticker = await StickerGen(ImageList,Text_to_MakeSticker,Nickname)

              if IO_sticker:
                  os.remove(Avatar_FileName)
                  try:
                    await Recall.send(message=Text_to_send1+MessageSegment.image(IO_sticker)+Text_to_send2)
                  except Exception as e:
                    logger.info(f"被禁言可能性微存: {e}")
                 

notice_handle = on_notice(priority=5, block=True)
@notice_handle.handle()
async def GroupNewMember(bot: Bot, event: GroupIncreaseNoticeEvent):
    if event.user_id == event.self_id:
        await bot.send_group_msg(group_id=event.group_id, message=Message(MessageSegment.text('这又是什么鸡巴群 没节目效果就退了\n')))
    else:
      try:
        await bot.send_group_msg(group_id=event.group_id, message=Message(MessageSegment.at(event.user_id) + MessageSegment.text("哈哈 年纪轻轻就进这种群 这辈子有咯~")))
      except Exception as e:
            logger.info(f"发送消息失败,被禁言可能性微存: {e}")

CommandTest = on_command("test",aliases={"测试"},priority=1,block=False)
@CommandTest.handle()
async def TestHandle(bot: Bot, event: GroupMessageEvent):
                #logger.info(f"收到测试指令")
                res = await bot.call_api('get_group_list', no_cache=True)
                group_list= [d['group_id'] for d in res]
                MsgHis = await bot.call_api('get_group_msg_history', group_id=group_list[0], message_seq=None)
                #Data_dict = json.loads(MsgHis)
                time =MsgHis['messages'][19]['time']
                dt = datetime.datetime.fromtimestamp(time)
                #logger.info(f"群列表: {group_list}")
                logger.info(f"历史消息: {MsgHis}")
                logger.info(f"历史消息时间: {dt}")

def message_preprocess(message: str):
    raw_message = message
    contained_images = {}
    images = re.findall(r'\[CQ:image.*?]', message)
    for i in images:
        contained_images.update({i: [re.findall(r'url=(.*?)[,\]]', i)[0][0], re.findall(r'file=(.*?)[,\]]', i)[0][0]]})
    for i in contained_images:
        message = message.replace(i, f'[{contained_images[i][1]}]')
    return message, raw_message

MassSending = on_command("群发",aliases={"qf"},priority=1,block=False,permission=SUPERUSER)
@MassSending.handle()
async def MassHandle(bot: Bot, event: PrivateMessageEvent,arg: Message = CommandArg()):               
                message, raw_message= message_preprocess(str(event.message))
                logger.info(f"即将群发: {raw_message}")
                raw_message=raw_message.replace("/qf", "").strip()
                for i in range(len(BrocastGroup)):
                     try: 
                         await bot.send_group_msg(group_id=BrocastGroup[i],message=raw_message,auto_escape=False)
                         await asyncio.sleep(1)
                     except Exception as e:
                         logger.info(f"可能被禁言: {e}")  


# 优先级99，条件：艾特bot就触发(改为不需at, 即处理所有消息)
if reply_type > -1:
    ai = on_message(permission = permission, priority=99, block=False)

    @ai.handle()
    async def _(bot: Bot,event: MessageEvent):
        # 获取消息文本
        Is_Reply = 0
        Is_long_img=0
        Is_text=event.get_message().extract_plain_text()

        
        msg = str(event.get_message())
        TempName = "temp.jpg"
        SessionID = event.get_session_id()
        parts = SessionID.split("_")
        GroupID = parts[1]
        UserID = parts[2]

        seed(a=None)
        random_int1= random.randint(0,100)
        random_int2= random.randint(0,100)
        logger.info(f"本次生成的随机数1的值为: {random_int1}")
        logger.info(f"本次生成的随机数2的值为: {random_int2}")

        logger.info(f"The Msg is {event.message_type}")
        
        if random_int1<2 and (GroupID in Target_Group):
           Is_Reply=1

        if random_int2<4 and (GroupID in Target_Group):
           Is_long_img=1

        # 如果是已配置的忽略项，直接结束事件
        for i in range(len(ignore)):
            if msg.startswith(ignore[i]):
                await ai.finish()
 
        if "空调" in msg:
            AirconPath = Path(img_path) / "吹空调.gif"
            #user =
            #at_ = "[CQ:at,qq={}]".format(user)
            #await bot.send_group_msg(group_id=GroupID,message=at_)
            await ai.finish(MessageSegment.image(AirconPath))


        if "早" in msg and len(msg)>4:
            await ai.finish()

        if "领导" in msg and Is_Reply==1:
            await ai.finish(Message("哈哈, 你这傻逼是不是还没下班"),at_sender=True)

        if ("星铁" in msg or "星穹铁道" in msg) and len(msg)>=4:
            await ai.finish(Message(random.choice(Star_Rail_Reply)),reply_message=True)

        if "老婆" in msg and Is_Reply==1:
            await ai.finish(Message("哈哈, 你这傻逼怎么整天在网上叫别人老婆, 现实里没有老婆吗"),at_sender=True)
            #await ai.finish(MessageSegment.image())
         

        if "？" in msg and len(msg)==1 and Is_Reply==1:
            await ai.finish(Message("¿"),at_sender=True)

        if "CQ:image" in msg and Is_Reply==1:  #图片消息
            pattern = r'url=([^]]+)'
            IsMatch = re.search(pattern, msg)
            ImgURL = IsMatch.group(1) #获取图片URL
            response = requests.get(ImgURL) #获取图片内容
            with open(TempName,"wb") as f:
                    f.write(response.content)
            img = Image.open(BytesIO(response.content))
            SizeInKB = os.path.getsize(TempName)/1024
            width, height = img.size
            logger.info(f"图片大小: {SizeInKB}KB")
            os.remove(TempName)

            if ((width<900 and height <900) or SizeInKB <100) and (GroupID in Target_Group): #粗略判断是否为表情包
                await ai.finish(Message(random.choice(hello__reply)),at_sender=True)
            else:
             await ai.finish(Message(random.choice(Img_reply)),at_sender=True)

        if (len(Is_text)) == 0 and Is_Reply==1:
           await ai.finish(Message(random.choice(hello__reply)),at_sender=True)

        if Is_long_img==1:
           img_name = random.choice(all_file_name)
           img = Path(img_path) / img_name
           await ai.finish(MessageSegment.image(img),at_sender=True) #发送表情

        # 去掉带中括号的内容(去除cq码)
        msg = re.sub(r"\[.*?\]", "", msg)
        # 如果是光艾特bot(没消息返回)，就回复以下内容
        if ((not msg) or msg.isspace()) and Is_Reply==1:
            await ai.finish(Message(random.choice(hello__reply)),at_sender=True)
            
        # 如果是打招呼的话，就回复以下内容
       
        
       
        
        # 获取用户nickname
        if isinstance(event, GroupMessageEvent):
            nickname = event.sender.card or event.sender.nickname
        else:
            nickname = event.sender.nickname

        if len(nickname) > 10:
            nickname = nickname[:2] + random.choice(["酱","亲","ちゃん","同志","老师"])
        # 从个人字典里获取结果（优先）
        result = await get_chat_result_my(msg,  nickname)
        if result != None:
            await ai.finish(Message(result))
        # 从LeafThesaurus里获取结果
        result = await get_chat_result_leaf(msg,  nickname)
        if result != None and Is_Reply==1:
            await ai.finish(Message(result),reply_message=True)
        # 从AnimeThesaurus里获取结果
        result = await get_chat_result(msg,  nickname)
        if result != None:
            await ai.finish(Message(result),reply_message=True) #reply_message控制是否回复消息
        #await LastSendTimeRecord(GroupID,time)
        

# 优先级10，不会向下阻断，条件：戳一戳bot触发

if poke_rand > -1:
    poke_ = on_notice(rule = to_me(), priority=10, block=False)

    @poke_.handle()
    async def _poke_event(event: PokeNotifyEvent):
        if event.is_tome:
            if poke_rand == 0:
                await asyncio.sleep(1.0)
                await poke_.finish(Message(f'[CQ:poke,qq={event.user_id}]'))
            else:
                if random.randint(1,poke_rand) == 1:
                    await asyncio.sleep(1.0)
                    await poke_.finish(Message(random.choice(poke__reply)))
                else:
                    await asyncio.sleep(1.0)
                    await poke_.finish(Message(f'[CQ:poke,qq={event.user_id}]'))

# 打断/复读姬

if interrupt > -1:
    repeater = on_message(permission=GROUP, priority=10, block=False)

    msg_last = {}
    msg_times = {}
    repeater_times = {}

    @repeater.handle()
    async def _(event: GroupMessageEvent):
        global msg_last, msg_times,repeater_times,repeater_flag
        group_id = event.group_id
        repeater_times.setdefault(group_id,random.randint(repeater_limit[0], repeater_limit[1]) - 1)
        msg = messagePreprocess(event.message)
        if msg_last.get(group_id) != msg:
            msg_last[group_id] = msg
            msg_times[group_id] = 1
        elif msg_times[group_id] == repeater_times[group_id]:
            repeater_times[group_id] = random.randint(repeater_limit[0], repeater_limit[1]) - 1
            msg_times[group_id] += repeater_limit[1]
            if interrupt == 0:
                await repeater.finish(event.message)
            else:
                if random.randint(1,interrupt) == 1:
                    await repeater.finish(random.choice(interrupt_msg))
                else:
                    await repeater.finish(event.message)
        else:
            msg_times[group_id] += 1
