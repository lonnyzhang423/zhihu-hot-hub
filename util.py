import os
from datetime import datetime


def currentTimeStr():
    return datetime.now().astimezone().strftime('%Y-%m-%d %H:%M:%S %z')


def currentDateStr():
    return datetime.now().astimezone().strftime('%Y-%m-%d')


def ensureDir(file):
    directory = os.path.abspath(os.path.dirname(file))
    if not os.path.exists(directory):
        os.makedirs(directory)


def writeText(file: str, text: str):
    ensureDir(file)
    with open(file, mode='w') as f:
        f.write(text)
