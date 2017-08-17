#!/usr/bin/env python
# -*- coding:utf-8 -*
import os
import re
import json
from pypinyin import lazy_pinyin


def loadDict(path):
    dict = {}
    with open(path, 'r', encoding='utf-8') as f:
        for line in f:
            arr = line.split(':::')
            para = json.loads(arr[1])['paraphrase']
            pp = {}
            for word in para:
                word.replace(' ', '')
                if word.find('.') != -1:
                    t = word.split('.')[0]
                    w = word.split('.')[1].split(';')[0].strip()
                    pp[t] = w
                else:
                    pp['*'] = word.strip()
            dict[arr[0]] = pp
    return dict


class Youdao(object):

    def __init__(self):
        super(Youdao, self).__init__()

    def query(self, word):
        import requests
        try:
            import xml.etree.cElementTree as ET
        except ImportError:
            import xml.etree.ElementTree as ET
        sess = requests.Session()
        headers = {
            'Host': 'dict.youdao.com',
            'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64; rv:50.0) Gecko/20100101 Firefox/50.0',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate'
        }
        sess.headers.update(headers)
        url = 'http://dict.youdao.com/fsearch?q=%s' % (word)
        try:
            resp = sess.get(url, timeout=100)
        except:
            return None
        text = resp.content
        if (resp.status_code == 200) and (text):
            tree = ET.ElementTree(ET.fromstring(text))
            returnPhrase = tree.find('return-phrase')
            if returnPhrase.text.strip() != word:
                return None
            customTranslation = tree.find('custom-translation')
            if not customTranslation:
                return None
            trans = ''
            for t in customTranslation.findall('translation'):
                transText = t[0].text
                if transText:
                    trans = transText
                    return trans
            return None
        else:
            return None


class trans(object):
    def __init__(self, path):
        self.dict = loadDict(path)

    def translate(self, word, pos, use_online=False):
        if self.dict.get(word):
            d = self.dict.get(word)
            if d.get(pos.lower()):
                return d.get(pos.lower())
            return next(iter(d.values()))
        elif use_online:
            pass
        else:
            return ' '.join(lazy_pinyin(word))

    def pinyin(self, word):
        return ' '.join(lazy_pinyin(word))
