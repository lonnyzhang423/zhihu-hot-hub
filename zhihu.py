# coding=utf8

import contextlib
import json
import traceback

import requests
from bs4 import BeautifulSoup
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

from util import logger

HOT_SEARCH_URL = 'https://www.zhihu.com/api/v4/search/top_search'
HOT_QUESTION_URL = 'https://www.zhihu.com/api/v3/feed/topstory/hot-lists/total?limit=50'
HOT_VIDEO_URL = 'https://www.zhihu.com/api/v3/feed/topstory/hot-lists/zvideo?limit=50'

HOT_SEARCH_URL2 = 'https://www.zhihu.com/topsearch'

HEADERS = {
    'x-api-version': '3.0.76',
    'user-agent': 'Mozilla/5.0 (iPhone; CPU iPhone OS 13_2_3 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/13.0.3 Mobile/15E148 Safari/604.1'
}
RETRIES = Retry(total=3,
                backoff_factor=1,
                status_forcelist=[k for k in range(400, 600)])


@contextlib.contextmanager
def request_session():
    s = requests.session()
    try:
        s.headers.update(HEADERS)
        s.mount("http://", HTTPAdapter(max_retries=RETRIES))
        s.mount("https://", HTTPAdapter(max_retries=RETRIES))
        yield s
    finally:
        s.close()


class Zhihu:

    def get_hot_search(self):
        """热搜
            {
                "queryDisplay": "空军宣传片疑似出现轰 20 ",
                "realQuery": "轰20",
                "queryDescription": "暗示首飞在即？",
                "redirectLink": "",
                "type": 0,
                "status": 0,
                "isNew": false
            }
        """
        items = []
        resp = None
        try:
            with request_session() as s:
                resp = s.get(HOT_SEARCH_URL2)
                soup = BeautifulSoup(resp.text)
                script = soup.find(
                    'script', type='text/json', id='js-initialData')
                if script:
                    obj = json.loads(script.string)
                    items = obj['initialState']['topsearch']['data']
        except:
            logger.warning(traceback.format_exc())
        return (items, resp)

    def get_hot_question(self):
        """热门问题
            {
                "type": "hot_list_feed",
                "style_type": "1",
                "id": "0_1610377259.41369",
                "card_id": "Q_438830539",
                "feed_specific": { "answer_count": 1376 },
                "target": {
                    "title_area": {
                    "text": "拼多多回应解约发帖员工，称「员工网上发布极端言论 ，违反员工手册」，公司是否有权利因网络言论开除员工？"
                    },
                    "excerpt_area": {
                    "text": "事件背景 1 月 11 日上午消息，针对员工王某（花名太虚）在网络平台发布不实视频讯息，自称「《因为看到同事被抬上救护车我被拼多多开除了》」一事，拼多多人力资源部发布的情况说明表示，王某被公司解约，并非因为其在匿名社区发布了「救护车照片」，而是公司事后调查发现王某多次在这一匿名社区发布带有显著恶意的「极端言论」，违反了员工手册中双方约定的行为规范。于是决定与其解约。 据悉 1 月 7 日，王 * 在公司楼下拍摄救护车照片并匿名将不恰当猜测发布至某匿名社区引发社会讨论。 在公司问询于事发拍摄地路过的同事时收到反馈，高度怀疑是王某在事实不清的情况下随意拍摄及匿名发布了有可能会对公司造成伤害的信息。公司 HR 和行政在主动问询王某时，他承认了是其本人进行了拍摄及发布。 拼多多公司根据王某所发帖的某匿名社区公开页面外显 ID（JgD+STsWV2E），公司查询到其既往匿名发帖内容充斥不良「极端言论」，诸如：「想要××死」，「把××的骨灰扬了」等。 公司人力资源部研判该员工上述言论严重违反员工手册，且有可能其极端情绪会对其他同事造成不可知威胁，决定与其解除劳动合同。 在公司与其解除劳动合同之后，王 * 及其周边人继续在网上发布不实言论，包括公司 HR 通过翻看其手机获悉其在某匿名社区发帖，以及公司 HR 威胁毁坏其档案，公司有 300 小时工时的「本分计算器」等，被各网络社区置顶推送，引发了新一轮网民关注。 公司人力资源部表示，上述均为不实讯息且之前已在相关渠道予以澄清。 以下为情况说明原文： 关于员工王 * 多次在某匿名社区发布「极端言论」被公司解约的情况说明 1 月 10 日，原为我司技术开发工程师的王 *（花名太虚）在网络平台发布不实视频讯息，自称「《因为看到同事被抬上救护车我被拼多多开除了》」。 真实情况为，王 * 被公司解约，不是因为其在匿名社区发布了「救护车照片」，而是公司事后调查发现王 * 多次在这一匿名社区发布带有显著恶意的「极端言论」，违反了员工手册中双方约定的行为规范。于是决定与其解约。 1 、事发当天情况： 1 月 7 日，王 * 在公司楼下拍摄救护车照片并匿名将不恰当猜测发布至某匿名社区引发社会讨论。 在公司问询于事发拍摄地路过的同事时收到反馈，高度怀疑是王 * 在事实不清的情况下随意拍摄及匿名发布了有可能会对公司造成伤害的信息。 公司 HR 和行政在主动问询王 * 时，他承认了是其本人进行了拍摄及发布。 根据王 * 所发帖的某匿名社区公开页面外显 ID（JgD+STsWV2E），公司查询到其既往匿名发帖内容充斥不良「极端言论」，诸如：「想要××死」，「把××的骨灰扬了」等。 公司人力资源部研判该员工上述言论严重违反员工手册，且有可能其极端情绪会对其他同事造成不可知威胁，决定与其解除劳动合同。 2 、其他澄清事项： 在公司与其解除劳动合同之后，王 * 及其周边人继续在网上发布不实言论，包括公司 HR 通过翻看其手机获悉其在某匿名社区发帖，以及公司 HR 威胁毁坏其档案，公司有 300 小时工时的「本分计算器」等，被各网络社区置顶推送，引发了新一轮网民关注。 公司特此对上述不实谣言予以澄清。 上海寻梦信息技术有限公司 人力资源部 1 月 11 日"
                    },
                    "image_area": {
                    "url": "https://pic2.zhimg.com/80/v2-e698cffa8b974ad49c728cf2098232d9_720w.png"
                    },
                    "metrics_area": { "text": "4975 万热度" },
                    "label_area": {
                    "type": "trend",
                    "trend": 0,
                    "night_color": "#B7302D",
                    "normal_color": "#F1403C"
                    },
                    "link": { "url": "https://www.zhihu.com/question/438830539" }
                },
                "attached_info": "Cj8IoNnq1oWDvdMWEAMaCDU5Nzk2MTIzIO7j7v8FMHI4nypAAHIJNDM4ODMwNTM5eACqAQliaWxsYm9hcmTSAQA="
            }
        """
        items = []
        resp = None
        try:
            with request_session() as s:
                resp = s.get(HOT_QUESTION_URL)
                obj = resp.json()
                items = obj['data']
        except:
            logger.warning(traceback.format_exc())
        return (items, resp)

    def get_hot_video(self):
        """热门视频
            {
                "type": "hot_list_feed",
                "style_type": "1",
                "id": "0_1610377795.4384937",
                "card_id": "ZV_1331729488393428992",
                "feed_specific": { "answer_count": 0 },
                "target": {
                    "title_area": { "text": "因为看到同事被抬上救护车我被拼多多开除了" },
                    "excerpt_area": { "text": "" },
                    "image_area": {
                    "url": "https://pic3.zhimg.com/50/v2-32df40175486b892fd1c77e12d280b87_b.jpg",
                    "video_length": "15:18"
                    },
                    "metrics_area": { "text": "383 万领域热度" },
                    "label_area": {
                    "type": "trend",
                    "trend": 0,
                    "night_color": "#B7302D",
                    "normal_color": "#F1403C"
                    },
                    "author_area": {
                    "type": "people",
                    "id": "f5c18526ffa5bb2a74c9a9bbd31c5594",
                    "url_token": "wang-tai-xu",
                    "url": "https://www.zhihu.com/people/wang-tai-xu",
                    "is_following": False,
                    "is_followed": False,
                    "avatar_url": "https://pic2.zhimg.com/50/8b5819fd5ab1204e304248d984a08175_s.jpg",
                    "name": "王太虚",
                    "badge": [
                        {
                        "type": "identity",
                        "description": "拼多多被辞退事件当事人",
                        "topic_names": []
                        }
                    ],
                    "badge_v2": {
                        "title": "拼多多被辞退事件当事人",
                        "merged_badges": [
                        {
                            "type": "identity",
                            "detail_type": "identity",
                            "title": "认证",
                            "description": "拼多多被辞退事件当事人",
                            "url": "https://www.zhihu.com/account/verification/intro",
                            "sources": [],
                            "icon": "",
                            "night_icon": ""
                        }
                        ],
                        "detail_badges": [
                        {
                            "type": "identity",
                            "detail_type": "identity_people",
                            "title": "已认证的个人",
                            "description": "拼多多被辞退事件当事人",
                            "url": "https://www.zhihu.com/account/verification/intro",
                            "sources": [],
                            "icon": "https://pic4.zhimg.com/v2-235258cecb8a0f184c4d38483cd6f6b6_l.png",
                            "night_icon": "https://pic4.zhimg.com/v2-45e870b8f0982bcd7537ea4627afbd00_l.png"
                        }
                        ],
                        "icon": "https://pic1.zhimg.com/v2-235258cecb8a0f184c4d38483cd6f6b6_l.png",
                        "night_icon": "https://pic4.zhimg.com/v2-45e870b8f0982bcd7537ea4627afbd00_l.png"
                    },
                    "description": "拼多多被辞退事件当事人"
                    },
                    "link": { "url": "https://www.zhihu.com/zvideo/1331729488393428992" }
                },
                "attached_info": "CloI1OTArvDzveIlEGMaEzEzMzE3Mjk0ODgzOTM0Mjg5OTIg1p/s/wUwhgZAAEoCIAByEzEzMzE3Mjk0ODgzOTM0Mjg5OTJ4AKoBEGJpbGxib2FyZC16dmlkZW8="
            }
        """
        items = []
        resp = None
        try:
            with request_session() as s:
                resp = s.get(HOT_VIDEO_URL)
                items = resp.json()['data']
        except:
            logger.warning(traceback.format_exc())
        return (items, resp)


if __name__ == "__main__":
    zhihu = Zhihu()
    # searches, resp = zhihu.get_hot_search()
    # logger.info('%s', searches[0])
    # questions, resp = zhihu.get_hot_question()
    # logger.info('%s', questions[0])
    videos, resp = zhihu.get_hot_video()
    logger.info('%s', videos[0])
