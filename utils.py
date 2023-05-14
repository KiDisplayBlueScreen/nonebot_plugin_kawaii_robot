import os
import re
import random
import nonebot
import time,datetime

try:
    import ujson as json
except ModuleNotFoundError:
    import json

from httpx import AsyncClient
from pathlib import Path
from nonebot.adapters.onebot.v11 import Message, MessageSegment
from nonebot.log import logger
from nonebot.adapters import Bot
from nonebot import get_bot
import asyncio

Bot_NICKNAME: str = list(nonebot.get_driver().config.nickname)[0]      # bot的nickname,可以换成你自己的
Bot_MASTER: str = list(nonebot.get_driver().config.superusers)[0]      # bot的主人名称,也可以换成你自己的     

path = os.path.join(os.path.dirname(__file__), "resource")
img_path = os.path.join(os.path.dirname(__file__), "龙")
StickerPath = Path(img_path) / "620.png"
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
    "¿",
     "怎么啦♡",
     "哈哈, 你这傻逼说话真有意思",
     "呐, 你知道什么事二刺螈吗?",
     "你是不是这个群里最二刺螈的?",
     "你言语混乱, 建议看看医生",
      "呜...♡主人（小声）",
      "我去, 这不是我们原神的角色吗",
      "你们都知道，我们没有条件这个样子，你不上班哪来的收入嘛。每个人都想懒啊，一天睡觉就睡到自然醒嘛，醒了就吃东西，然后想干什么自己想干的事就干。每个人都想啊。你们不要说我，你们何尝不是。你们如果有这个条件你们每个人都是懒狗，在那说我，比你们很多人都勤快吧，还有人说我是懒狗。很多读带学的你们觉得你们自己是不是懒狗，睡觉睡到课都不去上，一下午就在那，下午就在那打游戏，晚上就在那看直播。一天三顿都在寝室里面，还是叫同一个寝室的室友给你们带饭的，你不是懒狗吗？",
      "臭烧鸡, 糙死你",
      "杂鱼, 杂鱼♥",
      "你发的再多也只会制造焦虑与愤怒，愤怒之后呢？你明天还是要上班要工作，还要面对不知道前方是哪而的迷茫感，虚无主义充满了你的大脑",
      "呜呜...对不起QAQ",
      "好好滴伺候, 老爷有赏啊",
      "在?借点钱充原神",
      "哈哈, 傻逼们聊了这么多啊, 刚刚玩原神晕过去了现在才醒",
      "退QQ了 出自己的账号 号上有15个极品脑残 17个龙图贵物 3个原批 9个南通 已经经营过感情了 看到你说话会直接开始发龙图",
      "群主强调，振兴米哈游要做好“四批一体化”工作，落实好绝区零预下载这一任务，建成以高等级高练度铁道玩家及绝区测试玩家为中心的小组网络，各小组组长做好对组内成员原崩铁绝下载及游玩情况的调查，督促组内成员尽快下载崩原铁绝，加快“崩到原，原到铁，铁到绝”这一进程，深化改革本群结构，将本群改造为一个以重度米哈游玩家为主体的QQ群",
      "对不起，其实，我是二次元\r\n每天至少亲吻三次我的手机，不是因为我恋物，而是我对于爱的痴迷\r\n我看着扁平的手机，不立体的角色却映出来立体的感情\r\n每当我看见纸片人物，我的心就像潮水一般奔涌\r\n我不清楚这是不是爱，但我清楚的感受到，我的心在跳动\r\n起初，我很讨厌二次元，但自从我看过了以后，我才发现，我在骗自己，这是一种谎言，对于爱的谎言\r\n我必须面对自己，我控制住自己的言语，却控制不住自己的身体和情绪，所以我胶如涌泉的渲泄在纸片小人的身上，这一刻，我感受到充实\r\n我太爱二次元了，所以我模仿着二次元女孩娇滴滴的说话方式，仿佛我也是一个可爱的二次元女孩，但我呢，我只是一个高中生，我被压力压得走不动道，只有，在二次元中，我如飞鸟一般自由\r\n 我不怕你们笑话，其实，我是二次元",
      "吶吶吶，米娜桑，扣祢起哇，瓦込西二刺猿の焼酒desu!あああ，让我们①起守択，最好の二刺猿肥!吶吶，不憧我的，愚蠢の人炎們呵，果畔那塞，我二刺猿の焼酒是不会和祢有共同語言的jio豆麻袋,込祥子垪活有什幺錯喝?吶,告泝我呵。搜嚆,祢仞已経不喜炊了呵..真是冷酷の人昵,果鮮納塞,止祢看到不愉快のな西了。像我送祥的人,果然消失就好了昵。也午只有在二次元的世界里,オ有真正的美好存在的肥,吶?ねぇねぇねぇ，果然灰悪了呵，帯jio不，瓦込西，二刺猿の焼酒!博古哇zeidei不会人輸!米娜桑!吶!瓦込西二刺猿ぁぁ!哦晦吻扣賽伊弓斯!吶吶吶!米娜桑!我要幵劫了~一キ打去咢死!诶多诶多~「多洗忒」?为什么要「妄.图.抹.杀」这样的「自己」呢?★(笑)呐、「中二病的你」也好、「二次元的你」也好....「全部」daisuki~呐~二次元民那赛高desuwa!今后也.请.多.多.指.教.喔?~啊啊……是♡鲜♡血♡の♡味♡道♡呐♡~！（眯眼笑）kukuku——汝の「血」、会是什么样的「气味」呢☆？诶多多~说着说着有些期待了呢♪品尝「挚·爱·之·人」の「鲜血」什么的~嘛……如果是「你」的话，一定可以的!"
]

Img_reply = ["别发了, 我今天看了114514遍了","你这傻逼图都爆浆了还发呢?","有没有不穿衣服的"]
Sticker_reply = ["你怎么整天发这些表情包, 你是骚0吗"]
# 戳一戳消息
poke__reply = [
    "没吃饭?用点力",
     "戳你妈呢 我待会就像这样戳你妈的批"
]

Star_Rail_Reply = ["最新通知:4月26日，米哈游新作《崩坏：星穹铁道》（以下简称《星铁》）正式公测，本群要求所有人将电脑上的steam、Origin、Epic等游戏平台卸载，并于4月26日前下载并安装《星铁》，4月26日后将安排专人对电脑进行检查，收到请回复\r\n 1.本群非星铁玩家跟星铁玩家说话前要添加敬语 \r\n 2.本群星铁玩家对话途中非星铁玩家不允许插嘴\r\n 3.非星铁玩家每天早晚都要向本群星铁玩家问好\r\n 4.非星铁玩家发言控制在14字以内，必须打标点符号，不允许出现猴语录，不允许使用QQ第一排以下的表情\r\n 5.非星铁玩家不允许发表情包 \r\n6.非星铁玩家发图或语音必须征得星铁玩家同意 \r\n7.非星铁玩家一天只能发10句话，超过必禁\r\n 8.22:00后对非星铁玩家实行宵禁",
                              "中国人不开比亚迪,可以理解，毕竟不是一般人能买得起\r\n中国人不用华为,也可以理解,毕竟华为也不算便宜\r\n但是中国人不玩星穹铁道就很难理解了。口口声声说爱国,但是面对目前世界最顶尖的国产3A游戏。就算零氪给国产游戏流量这种举手之劳都不愿意如果连玩星穹铁辑这种无成本的爱国都拒绝,那就是汉奸"]
Long_time_noreply=["死群了","怎么没人了 都去玩原神还是操大B了","怎么没人了 都去玩原神还是操大B了?求求你们不要再操大B了, 我过得再苦再穷都不会难过, 只有一想到你们都在操大B的时候, 我的心就像被刀割一样疼, 一边打字一边泪水就忍不住往下流"]

Target_Group=[]
GroupList=[]

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


async def Check():
    now = datetime.datetime.now()
    if now.hour<=9:
        return 0
# 遍历每个GroupID和对应的LastSendTime
    bot:Bot = get_bot()
    res = await bot.call_api('get_group_list', no_cache=True)
    GroupList = [d['group_id'] for d in res]

    if len(GroupList)!=0:
       for i in range(len(GroupList)):
          try:
             if str(GroupList[i]) not in Target_Group:
                 continue
             MsgHis = await bot.call_api('get_group_msg_history', group_id=GroupList[i], message_seq=None)
          except Exception as e:
            logger.info(f"获取群历史消息失败: {e}")
          time = MsgHis['messages'][-1]['time']
          LastSendTime = datetime.datetime.fromtimestamp(time)
          time_diff = now - LastSendTime
          if time_diff.total_seconds() > 3600 and str(GroupList[i]) in Target_Group:
        #logger.info(f"{GroupID}: {LastSendTime_str} > 30 minutes")
           try: 
            await bot.send_group_msg(group_id=GroupList[i],message=random.choice(Long_time_noreply))
            await asyncio.sleep(4)
            continue
           except Exception as e:
            logger.info(f"可能被禁言: {e}")
            await asyncio.sleep(1)
            continue
          else:
              logger.info(f"{GroupList[i]}: {LastSendTime} < 60 minutes")
              continue
       return  0

