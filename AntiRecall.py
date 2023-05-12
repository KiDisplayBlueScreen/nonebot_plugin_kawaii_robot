# -*- coding: utf-8 -*-
from lib2to3.pgen2.token import AWAIT
from unittest import result
from nonebot import get_driver, on_command, on_notice
from nonebot import on_command, on_fullmatch, on_keyword, on_message
from nonebot.log import logger
import requests
import pathlib
import re
import os
import asyncio
from nonebot.internal.adapter import Bot as BaseBot
from nonebot.adapters.onebot.v11 import (
    Bot,
    Message,
    Event,
    MessageEvent,
    GroupMessageEvent,
    GroupRecallNoticeEvent,
    PrivateMessageEvent,
)
import asyncio
from meme_generator import get_meme
from typing import List

AvatarUrl = "http://q1.qlogo.cn/g?b=qq&nk="
AvatarUrl_Suffix = "&s=100"

async def GetAvatar(UserID:str):
          if not UserID or len(UserID)==0:
              return 0
          URL = AvatarUrl+UserID+AvatarUrl_Suffix
          Temp_Avatar_Name = UserID+".jpg"
          try:
           response = requests.get(URL)
           with open(Temp_Avatar_Name,"wb") as f:
                  f.write(response.content)
          except Exception as e:
            logger.info(f"获取头像失败: {e}")
          logger.info(f"获取头像成功")
          return Temp_Avatar_Name

async def StickerGen(image: List[str],text:List[str],name:str):
                meme = get_meme("my_friend")
                arg ={"circle": True}
                arg["name"]=name
                try:
                    result = await meme(images=image, texts=text, args=arg)
                except Exception as e:
                    logger.info(f"创建表情失败: {e}")
                return result
                """
                file_path = os.path.abspath(os.path.join(os.path.dirname(__file__), 'result.gif'))
                try:
                 with open(file_path, "wb") as f:
                        f.write(result.getvalue())
                        os.remove(image[0])
                except Exception as e:
                         logger.info(f"创建表情失败: {e}")
                         return 0
                return 1
                """