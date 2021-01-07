import json
import logging
import os
import traceback

import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

import util

logging.basicConfig()
log = logging.getLogger(__name__)
log.setLevel(level=logging.INFO)

HOT_URL = "https://www.zhihu.com/api/v3/feed/topstory/hot-lists/total?limit=50"

retries = Retry(total=2,
                backoff_factor=0.1,
                status_forcelist=[k for k in range(400, 600)])


def getContent(url: str) -> str:
    try:
        with requests.session() as s:
            s.mount("http://", HTTPAdapter(max_retries=retries))
            s.mount("https://", HTTPAdapter(max_retries=retries))
            r = s.get(url)
            return r.text
    except:
        log.error(traceback.format_exc())


def parseTopics(content):
    """解析话题
    """
    def topic(item):
        info = {}
        info['id'] = item['id']
        info['title'] = item['title']
        info['content'] = item['content']
        info['url'] = item['url']
        return info

    result = []
    try:
        arr = json.loads(content)
        if arr:
            result = [topic(item) for item in arr]
    except:
        log.error(traceback.format_exc())

    return result


def generateArchiveReadme(items):
    """生成归档readme
    """
    def topic(item):
        return '1. [{}]({})'.format(item['title'], item['url'])

    topics = '暂无数据'
    if items:
        topics = '\n'.join([topic(item) for item in items])

    readme = ''
    with open('README_archive.template', 'r') as f:
        readme = f.read()

    date = util.currentDateStr()
    now = util.currentTimeStr()
    readme = readme.replace("{date}", date)
    readme = readme.replace("{updateTime}", now)
    readme = readme.replace("{topics}", topics)

    return readme


def generateTodayReadme(items):
    """生成今日readme
    """
    def topic(item):
        return '1. [{}]({})'.format(item['title'], item['url'])

    topics = '暂无数据'
    if items:
        topics = '\n'.join([topic(item) for item in items])

    readme = ''
    with open('README.template', 'r') as f:
        readme = f.read()

    now = util.currentTimeStr()
    readme = readme.replace("{updateTime}", now)
    readme = readme.replace("{topics}", topics)

    return readme


def handleTodayMd(md):
    log.debug('today md:%s', md)
    util.writeText('README.md', md)


def handleArchiveMd(md):
    log.debug('archive md:%s', md)
    name = util.currentDateStr()+'.md'
    file = os.path.join('archives', name)
    util.writeText(file, md)


def handleRawContent(content: str):
    log.debug('raw content:%s', content)
    name = util.currentDateStr()+'.json'
    file = os.path.join('raw', name)
    util.writeText(file, content)


def run():
    # 获取数据
    content = getContent(HOT_URL)
    topics = parseTopics(content)

    # 最新数据
    todayMd = generateTodayReadme(topics)
    handleTodayMd(todayMd)
    # 归档
    archiveMd = generateArchiveReadme(topics)
    handleArchiveMd(archiveMd)
    # 原始数据
    raw = json.dumps(json.loads(content), ensure_ascii=False)
    handleRawContent(raw)


if __name__ == "__main__":
    run()
