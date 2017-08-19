#!/usr/bin/env python
# -*- coding:utf-8 -*
import os
import re
import json
from pypinyin import lazy_pinyin
from hanziconv import HanziConv
import unicodedata


def loadDict(path):
    dict = {}
    with open(path, 'r', encoding='utf-8') as f:
        for line in f:
            arr = line.split(':::')
            para = json.loads(arr[1])['paraphrase']
            pp = {}
            for word in para:
                word = word.replace('  ', '')
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


STOPWORDS = {
    'i', 'me', 'my', 'myself', 'we', 'our', 'ours', 'ourselves', 'you', 'your',
    'yours', 'yourself', 'yourselves', 'he', 'him', 'his', 'himself', 'she',
    'her', 'hers', 'herself', 'it', 'its', 'itself', 'they', 'them', 'their',
    'theirs', 'themselves', 'what', 'which', 'who', 'whom', 'this', 'that',
    'these', 'those', 'am', 'is', 'are', 'was', 'were', 'be', 'been', 'being',
    'have', 'has', 'had', 'having', 'do', 'does', 'did', 'doing', 'a', 'an',
    'the', 'and', 'but', 'if', 'or', 'because', 'as', 'until', 'while', 'of',
    'at', 'by', 'for', 'with', 'about', 'against', 'between', 'into', 'through',
    'during', 'before', 'after', 'above', 'below', 'to', 'from', 'up', 'down',
    'in', 'out', 'on', 'off', 'over', 'under', 'again', 'further', 'then',
    'once', 'here', 'there', 'when', 'where', 'why', 'how', 'all', 'any',
    'both', 'each', 'few', 'more', 'most', 'other', 'some', 'such', 'no', 'nor',
    'not', 'only', 'own', 'same', 'so', 'than', 'too', 'very', 's', 't', 'can',
    'will', 'just', 'don', 'should', 'now', 'd', 'll', 'm', 'o', 're', 've',
    'y', 'ain', 'aren', 'couldn', 'didn', 'doesn', 'hadn', 'hasn', 'haven',
    'isn', 'ma', 'mightn', 'mustn', 'needn', 'shan', 'shouldn', 'wasn', 'weren',
    'won', 'wouldn', "'ll", "'re", "'ve", "n't", "'s", "'d", "'m", "''", "``"
}
with open('drqa/retriever/stopword_zh.txt') as f:
    # load chinese stop word
    for line in f:
        STOPWORDS.add(line.replace('\n', ''))


class similar(object):
    def __init__(self):
        self.chs_arabic_map = {u'零': 0, u'一': 1, u'二': 2, u'三': 3, u'四': 4,
                                    u'五': 5, u'六': 6, u'七': 7, u'八': 8, u'九': 9,
                                    u'十': 10, u'百': 100, u'千': 10 ** 3, u'万': 10 ** 4,
                                    u'亿': 10 ** 8}

    def compare(self, word0, word1):
        # print(word0 + '|' + word1)
        word0 = normalize(word0)
        word1 = normalize(word1)
        if word0 not in STOPWORDS and word1 not in STOPWORDS:
            if ' '.join(lazy_pinyin(word0)) == ' '.join(lazy_pinyin(word1)):
                return 1.0
            elif self.convertHan(word0) == self.convertHan(word1):
                return 1.0
            else:
                return 0.0
        else:
            return 0.0

    def convertHan(self, text):
        ls = re.finditer(
            '[零|一|二|三|四|五|六|七|八|九|十][零|一|二|三|四|五|六|七|八|九|十|百|千|万|亿]+', text)
        for i in ls:
            s = text[i.span()[0]:i.span()[1]]
            text = text.replace(s, (str)(self.convertChineseDigitsToArabic(s)))
        return text

    def convertChineseDigitsToArabic(self, chinese_digits):
        result = 0
        tmp = 0
        hnd_mln = 0
        for count in range(len(chinese_digits)):
            curr_char = chinese_digits[count]
            curr_digit = self.chs_arabic_map.get(curr_char, None)
            # meet 「亿」 or 「億」
            if curr_digit == 10 ** 8:
                result = result + tmp
                result = result * curr_digit
                # get result before 「亿」 and store it into hnd_mln
                # reset `result`
                hnd_mln = hnd_mln * 10 ** 8 + result
                result = 0
                tmp = 0
            # meet 「万」 or 「萬」
            elif curr_digit == 10 ** 4:
                result = result + tmp
                result = result * curr_digit
                tmp = 0
            # meet 「十」, 「百」, 「千」 or their traditional version
            elif curr_digit >= 10:
                tmp = 1 if tmp == 0 else tmp
                result = result + curr_digit * tmp
                tmp = 0
            # meet single digit
            elif curr_digit is not None:
                tmp = tmp * 10 + curr_digit
            else:
                return result
        result = result + tmp
        result = result + hnd_mln
        return result


def normalize(text):
    toSim = HanziConv.toSimplified(text.replace('\n', ' '))
    t2 = unicodedata.normalize('NFKC', toSim)
    table = {ord(f): ord(t) for f, t in zip(
        u'，。！？【】（）％＃＠＆１２３４５６７８９０',
        u',.!?[]()%#@&1234567890')}
    t3 = t2.translate(table)
    return t3
