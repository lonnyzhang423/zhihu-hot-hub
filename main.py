import json
import logging
import os
import traceback
import urllib.parse

import requests
from bs4 import BeautifulSoup
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

import util

logging.basicConfig()
log = logging.getLogger(__name__)
log.setLevel(level=logging.DEBUG)

HOT_SEARCH_URL = 'https://www.zhihu.com/api/v4/search/top_search'
HOT_QUESTION_URL = 'https://www.zhihu.com/api/v3/feed/topstory/hot-lists/total?limit=50'
HOT_VIDEO_URL = 'https://www.zhihu.com/api/v3/feed/topstory/hot-lists/zvideo?limit=50'

HOT_SEARCH_URL2 = 'https://www.zhihu.com/topsearch'

retries = Retry(total=2,
                backoff_factor=0.1,
                status_forcelist=[k for k in range(400, 600)])

headers = {
    'user-agent': 'Mozilla/5.0 (iPhone; CPU iPhone OS 13_2_3 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/13.0.3 Mobile/15E148 Safari/604.1'
}


headers2 = {
    'x-api-version': '3.0.76',
    'user-agent': 'Mozilla/5.0 (iPhone; CPU iPhone OS 13_2_3 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/13.0.3 Mobile/15E148 Safari/604.1'
}


def getContent(url: str, headers=headers) -> str:
    try:
        with requests.session() as s:
            s.mount("http://", HTTPAdapter(max_retries=retries))
            s.mount("https://", HTTPAdapter(max_retries=retries))
            return s.get(url, headers=headers).text
    except:
        log.error(traceback.format_exc())


def parseSearchList(content):
    """解析热搜
    """
    def search(item):
        info = {}
        info['title'] = item['display_query']
        q = urllib.parse.quote(item['query'])
        info['url'] = 'https://www.zhihu.com/search?q={}'.format(q)
        return info

    result = []
    try:
        arr = json.loads(content)['top_search']['words']
        if arr:
            result = [search(item) for item in arr]
    except:
        log.error(traceback.format_exc())

    return result


def parseSearchList2(content):
    """解析热搜
    """
    def search(item):
        info = {}
        info['title'] = item['queryDisplay']
        q = urllib.parse.quote(item['realQuery'])
        info['url'] = 'https://www.zhihu.com/search?q={}'.format(q)
        return info

    result = []
    try:
        soup = BeautifulSoup(content)
        script = soup.find('script', type='text/json', id='js-initialData')
        if script:
            obj = json.loads(script.string)
            list = obj['initialState']['topsearch']['data']
            if list:
                result = [search(item) for item in list]
    except:
        log.error(traceback.format_exc())
    return result


def parseQuestionList(content):
    """解析热搜
    """
    def question(item):
        info = {}
        target = item['target']
        info['title'] = target['title']
        info['url'] = 'https://www.zhihu.com/question/{}'.format(target['id'])
        return info

    result = []
    try:
        arr = json.loads(content)['data']
        if arr:
            result = [question(item) for item in arr]
    except:
        log.error(traceback.format_exc())

    return result


def parseVideoList(content):
    """解析热门视频
    """
    def video(item):
        info = {}
        target = item['target']
        info['title'] = target['title_area']['text']
        info['url'] = target['link']['url']
        return info

    result = []
    try:
        arr = json.loads(content)['data']
        if arr:
            result = [video(item) for item in arr]
    except:
        log.error(traceback.format_exc())
    return result


def generateArchiveReadme(searches, questsions, videos):
    """生成归档readme
    """
    def liMd(item):
        return '1. [{}]({})'.format(item['title'], item['url'])

    searchMd = '暂无数据'
    if searches:
        searchMd = '\n'.join([liMd(item) for item in searches])

    questionMd = '暂无数据'
    if questsions:
        questionMd = '\n'.join([liMd(item) for item in questsions])

    videoMd = '暂无数据'
    if videos:
        videoMd = '\n'.join([liMd(item) for item in videos])

    readme = ''
    with open('README_archive.template', 'r') as f:
        readme = f.read()

    date = util.currentDateStr()
    now = util.currentTimeStr()
    readme = readme.replace("{date}", date)
    readme = readme.replace("{updateTime}", now)
    readme = readme.replace("{searches}", searchMd)
    readme = readme.replace("{questions}", questionMd)
    readme = readme.replace("{videos}", videoMd)

    return readme


def generateTodayReadme(searches, questsions, videos):
    """生成今日readme
    """
    def liMd(item):
        return '1. [{}]({})'.format(item['title'], item['url'])

    searchMd = '暂无数据'
    if searches:
        searchMd = '\n'.join([liMd(item) for item in searches])

    questionMd = '暂无数据'
    if questsions:
        questionMd = '\n'.join([liMd(item) for item in questsions])

    videoMd = '暂无数据'
    if videos:
        videoMd = '\n'.join([liMd(item) for item in videos])

    readme = ''
    with open('README.template', 'r') as f:
        readme = f.read()

    now = util.currentTimeStr()
    readme = readme.replace("{updateTime}", now)
    readme = readme.replace("{searches}", searchMd)
    readme = readme.replace("{questions}", questionMd)
    readme = readme.replace("{videos}", videoMd)

    return readme


def handleTodayMd(md):
    log.debug('today md:%s', md)
    util.writeText('README.md', md)


def handleArchiveMd(md):
    log.debug('archive md:%s', md)
    name = util.currentDateStr()+'.md'
    file = os.path.join('archives', name)
    util.writeText(file, md)


def handleRawContent(content: str, filePrefix: str, fileSuffix='json'):
    log.debug('raw content:%s', content)
    name = '{}-{}.{}'.format(filePrefix, util.currentDateStr(), fileSuffix)
    file = os.path.join('raw', name)
    util.writeText(file, content)


def run():
    # 热搜数据
    searchHtml = getContent(HOT_SEARCH_URL2)
    searches = parseSearchList2(searchHtml)
    # 问题数据
    questionContent = getContent(HOT_QUESTION_URL)
    questions = parseQuestionList(questionContent)
    # 视频数据
    videoContent = getContent(HOT_VIDEO_URL, headers2)
    videos = parseVideoList(videoContent)

    # 最新数据
    todayMd = generateTodayReadme(searches, questions, videos)
    handleTodayMd(todayMd)
    # 归档
    archiveMd = generateArchiveReadme(searches, questions, videos)
    handleArchiveMd(archiveMd)
    # 原始数据
    handleRawContent(searchHtml, 'hot-search', 'html')
    raw = json.dumps(json.loads(questionContent), ensure_ascii=False)
    handleRawContent(raw, 'hot-question', 'json')
    raw = json.dumps(json.loads(videoContent), ensure_ascii=False)
    handleRawContent(raw, 'hot-video', 'json')


if __name__ == "__main__":
    run()
