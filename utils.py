import os
import re
import random
import nonebot

try:
    import ujson as json
except ModuleNotFoundError:
    import json

from httpx import AsyncClient
from pathlib import Path
from nonebot.adapters.onebot.v11 import Message, MessageSegment
from nonebot.log import logger

Bot_NICKNAME: str = list(nonebot.get_driver().config.nickname)[0]      # bot的nickname,可以换成你自己的
Bot_MASTER: str = list(nonebot.get_driver().config.superusers)[0]      # bot的主人名称,也可以换成你自己的     

path = os.path.join(os.path.dirname(__file__), "resource")

# 载入个人词库
lst = os.listdir(Path(path))
lst.remove("leaf.json")
lst.remove("data.json")
MyThesaurus = {}
for i in lst:
    try:
        tmp = json.load(open(Path(path) / i, "r", encoding="utf8"))
        logger.info(f"{i} 加载成功~")
        for key in tmp.keys():
            if not key in MyThesaurus.keys():
                MyThesaurus.update({key:[]})
            if type(tmp[key]) == list:
                MyThesaurus[key] += tmp[key]
            else:
                logger.info(f"\t文件 {i} 内 {key} 词条格式错误。")
    except UnicodeDecodeError:
        logger.info(f"{i} utf8解码出错！！！")
    except Exception as error:
        logger.info(f"错误：{error} {i} 加载失败...")

# 载入首选词库
LeafThesaurus = json.load(open(Path(path) / "leaf.json", "r", encoding="utf8"))

# 载入词库(这个词库有点涩)
AnimeThesaurus = json.load(open(Path(path) / "data.json", "r", encoding="utf8"))


# 向bot打招呼
hello__bot = [
    "你好啊",
    "你好",
    "在吗",
    "在不在",
    "您好",
    "您好啊",
    "你好",
    "在",
    "早",
]

# hello之类的回复
hello__reply = [
    "哦牛批",
    "这群真的是jb完蛋了，每天点进来就是那几个SB在脑蚕共振，说的B话都他MB差不多，脑子跟腻麻流水线生产出来的一样，从网上看来的老梗梗吃了再拉出来，再吃再拉出来，就像是一坨屎吃下了另一坨屎拉出的第三坨屎，屎都腻麻笔的爆浆了还在这儿乐此不疲的刷，聊了半天跟你妈没聊一样，昨天的图复制粘贴一下就是今天的图。二次元跟这个群都起了一个功效，脑瘫儿童收容所，大脑发育不健全只能当复读机的社会残障人士集体在这里实现了自我价值，还满足了每天的情感交流需求",
    "干嘛....",
    "哈哈, 你这傻逼消息怎么这么灵通",
    "别发了, 我今天看了114514遍了",
    "你这傻逼图都爆浆了还发呢?",
    "¿",
     "哈哈, 你这傻逼说话真有意思",
     "呐, 你知道什么事二刺螈吗?",
     "你是不是这个群里最二刺螈的?",
     "你言语混乱, 建议看看医生",
      "臭烧鸡, 糙死你",
      "哈哈, 傻逼们聊了这么多啊, 刚刚玩原神晕过去了现在才醒",
      "吶吶吶，米娜桑，扣祢起哇，瓦込西二刺猿の焼酒desu!あああ，让我们①起守択，最好の二刺猿肥!吶吶，不憧我的，愚蠢の人炎們呵，果畔那塞，我二刺猿の焼酒是不会和祢有共同語言的jio豆麻袋,込祥子垪活有什幺錯喝?吶,告泝我呵。搜嚆,祢仞已経不喜炊了呵..真是冷酷の人昵,果鮮納塞,止祢看到不愉快のな西了。像我送祥的人,果然消失就好了昵。也午只有在二次元的世界里,オ有真正的美好存在的肥,吶?ねぇねぇねぇ，果然灰悪了呵，帯jio不，瓦込西，二刺猿の焼酒!博古哇zeidei不会人輸!米娜桑!吶!瓦込西二刺猿ぁぁ!哦晦吻扣賽伊弓斯!吶吶吶!米娜桑!我要幵劫了~一キ打去咢死!诶多诶多~「多洗忒」?为什么要「妄.图.抹.杀」这样的「自己」呢?★(笑)呐、「中二病的你」也好、「二次元的你」也好....「全部」daisuki~呐~二次元民那赛高desuwa!今后也.请.多.多.指.教.喔?~啊啊……是♡鲜♡血♡の♡味♡道♡呐♡~！（眯眼笑）kukuku——汝の「血」、会是什么样的「气味」呢☆？诶多多~说着说着有些期待了呢♪品尝「挚·爱·之·人」の「鲜血」什么的~嘛……如果是「你」的话，一定可以的!"
]

# 戳一戳消息
poke__reply = [
    "没吃饭?用点力",
     "戳你妈呢 我待会就像这样戳你妈的批"
]

# 不明白的消息
cant__reply = [
    f"{Bot_NICKNAME}不懂...",
    "呜喵？",
    "没有听懂喵...",
    "装傻（",
    "呜......",
    "喵喵？",
    "(,,• ₃ •,,)",
    "没有理解呢...",
]

# 打断复读
interrupt_msg = [
    "复读蛆你妈死了",
    "复读傻狗全家暴毙",
    MessageSegment.face(212),
    MessageSegment.face(318) + MessageSegment.face(318),
    MessageSegment.face(181),
]

async def get_chat_result_my(text: str, nickname: str) -> str:
    '''
    从个人词库里返还消息
    '''
    if len(text) < 70:
        keys = MyThesaurus.keys()
        for key in keys:
            if text.find(key) != -1:
                return random.choice(MyThesaurus[key])

async def get_chat_result_leaf(text: str, nickname: str) -> str:
    '''
    从leaf.json里返还消息
    '''
    if len(text) < 70:
        keys = LeafThesaurus.keys()
        for key in keys:
            if text.find(key) != -1:
                return random.choice(LeafThesaurus[key])

async def get_chat_result(text: str, nickname: str) -> str:
    '''
    从data.json里返还消息
    '''
    if len(text) < 70:
        keys = AnimeThesaurus.keys()
        for key in keys:
            if text.find(key) != -1:
                return random.choice(AnimeThesaurus[key])

def is_CQ_Code(msg:str) -> bool:
    '''
    判断参数是否为CQ码
    '''
    if len(msg) > 4 and msg[0] == '[' and msg[1:4] == "CQ:" and msg[-1] == ']':
        return True
    else:
        return False

def messagePreprocess(msg: Message):
    '''
    对CQ码返回文件名（主要是处理CQ:image）
    '''
    msg = str(msg)
    if is_CQ_Code(msg):
        data = msg.split(',')
        for x in data:
            if "file=" in x:
                return x
    return msg

