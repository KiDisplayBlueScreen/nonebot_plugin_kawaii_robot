from nonebot.plugin.on import on_message,on_notice
from nonebot.rule import to_me
from nonebot.log import logger
from bs4 import BeautifulSoup
from nonebot.adapters.onebot.v11 import (
    GROUP,
    GroupMessageEvent,
    Message,
    MessageEvent,
    MessageSegment,
    PokeNotifyEvent,
)

import nonebot
import asyncio
import random
import pathlib
import re
import os
from PIL import Image
from io import BytesIO
import requests
from .utils import *
from .config import Config

# 加载全局配置
global_config = nonebot.get_driver().config
leaf = Config.parse_obj(global_config.dict())

reply_type = leaf.leaf_reply_type
poke_rand = leaf.leaf_poke_rand

repeater_limit = leaf.leaf_repeater_limit
interrupt = leaf.leaf_interrupt

ignore = leaf.leaf_ignore

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

# 优先级99，条件：艾特bot就触发(改为不需at, 即处理所有消息)
if reply_type > -1:
    ai = on_message(permission = permission, priority=99, block=False)

    @ai.handle()
    async def _(event: MessageEvent):
        # 获取消息文本
        Is_Reply = 0
        Is_long_img=0
        Is_text=event.get_message().extract_plain_text()
        msg = str(event.get_message())
        #MsgType = event.get_type()


        random_int1= random.randint(0,100)
        random_int2= random.randint(0,100)
        logger.info(f"本次生成的随机数1的值为: {random_int1}")
        logger.info(f"本次生成的随机数2的值为: {random_int2}")
        #logger.info(f"The Msg is {msg}")
        
        if random_int1<10:
           Is_Reply=1

        if random_int2<7:
           Is_long_img=1

        

        if "领导" in msg and Is_Reply==1:
            await ai.finish(Message("哈哈, 你这傻逼是不是还没下班"),at_sender=True)

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
            img = Image.open(BytesIO(response.content))
            width, height = img.size
            if width<1000 and height <1000: #粗略判断是否为表情包
                await ai.finish(Message(random.choice(Sticker_reply)),at_sender=True)
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
       
        
        # 如果是已配置的忽略项，直接结束事件
        for i in range(len(ignore)):
            if msg.startswith(ignore[i]):
                await ai.finish()
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
        if result != None:
            await ai.finish(Message(result))
        # 从AnimeThesaurus里获取结果
        result = await get_chat_result(msg,  nickname)
        if result != None:
            await ai.finish(Message(result))
        # 随机回复cant__reply的内容
        

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
