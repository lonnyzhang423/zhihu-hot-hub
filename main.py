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
from util import logger
from zhihu import Zhihu


def generate_archive_md(searches, questsions, videos):
    """生成归档readme
    """
    def search(item):
        title = item['queryDisplay']
        q = urllib.parse.quote(item['realQuery'])
        url = 'https://www.zhihu.com/search?q={}'.format(q)
        return '1. [{}]({})'.format(title, url)

    def question(item):
        target = item['target']
        title = target['title_area']['text']
        url = target['link']['url']
        return '1. [{}]({})'.format(title, url)

    def video(item):
        target = item['target']
        title = target['title_area']['text']
        url = target['link']['url']
        return '1. [{}]({})'.format(title, url)

    searchMd = '暂无数据'
    if searches:
        searchMd = '\n'.join([search(item) for item in searches])

    questionMd = '暂无数据'
    if questsions:
        questionMd = '\n'.join([question(item) for item in questsions])

    videoMd = '暂无数据'
    if videos:
        videoMd = '\n'.join([video(item) for item in videos])

    md = ''
    file = os.path.join('template', 'archive.md')
    with open(file) as f:
        md = f.read()

    now = util.current_time()
    md = md.replace("{updateTime}", now)
    md = md.replace("{searches}", searchMd)
    md = md.replace("{questions}", questionMd)
    md = md.replace("{videos}", videoMd)

    return md


def generate_readme(searches, questsions, videos):
    """生成readme
    """
    def search(item):
        title = item['queryDisplay']
        q = urllib.parse.quote(item['realQuery'])
        url = 'https://www.zhihu.com/search?q={}'.format(q)
        return '1. [{}]({})'.format(title, url)

    def question(item):
        target = item['target']
        title = target['title_area']['text']
        url = target['link']['url']
        return '1. [{}]({})'.format(title, url)

    def video(item):
        target = item['target']
        title = target['title_area']['text']
        url = target['link']['url']
        return '1. [{}]({})'.format(title, url)

    searchMd = '暂无数据'
    if searches:
        searchMd = '\n'.join([search(item) for item in searches])

    questionMd = '暂无数据'
    if questsions:
        questionMd = '\n'.join([question(item) for item in questsions])

    videoMd = '暂无数据'
    if videos:
        videoMd = '\n'.join([video(item) for item in videos])

    readme = ''
    file = os.path.join('template', 'README.md')
    with open(file) as f:
        readme = f.read()

    now = util.current_time()
    readme = readme.replace("{updateTime}", now)
    readme = readme.replace("{searches}", searchMd)
    readme = readme.replace("{questions}", questionMd)
    readme = readme.replace("{videos}", videoMd)

    return readme


def handleTodayMd(md):
    logger.debug('today md:%s', md)
    util.write_text('README.md', md)


def handleArchiveMd(md):
    logger.debug('archive md:%s', md)
    name = util.current_date()+'.md'
    file = os.path.join('archives', name)
    util.write_text(file, md)


def handleRawContent(content: str, filePrefix: str, fileSuffix='json'):
    logger.debug('raw content:%s', content)
    name = '{}-{}.{}'.format(filePrefix, util.current_date(), fileSuffix)
    file = os.path.join('raw', name)
    util.write_text(file, content)


def run():
    zhihu = Zhihu()
    # 热搜数据
    searches, resp = zhihu.get_hot_search()
    if resp:
        handleRawContent(resp.text, 'hot-search', 'html')
    # 问题数据
    questions, resp = zhihu.get_hot_question()
    if resp:
        text = util.cnsafe_json(resp.text)
        handleRawContent(text, 'hot-question', 'json')
    # 视频数据
    videos, resp = zhihu.get_hot_video()
    if resp:
        text = util.cnsafe_json(resp.text)
        handleRawContent(text, 'hot-video', 'json')
    # 最新数据
    todayMd = generate_readme(searches, questions, videos)
    handleTodayMd(todayMd)
    # 归档
    archiveMd = generate_archive_md(searches, questions, videos)
    handleArchiveMd(archiveMd)


if __name__ == "__main__":
    run()
