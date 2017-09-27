import re
import sqlite3
from drqa import retriever
from drqa.retriever.net_retriever import retriver
from drqa.tokenizers.zh_features import normalize, STOPWORDS
import jieba
import logging
import Levenshtein

logger = logging.getLogger(__name__)

# simplesingel thread DrQA agent


class SDrQA(object):
    def __init__(self, predictor, rankerPath, dbPath, ebdPath=None):
        self.predictor = predictor
        self.ranker = retriever.get_class('tfidf')(tfidf_path=rankerPath)
        conn = sqlite3.connect(dbPath)
        self.db = conn.cursor()
        self.filter = filtText('drqa/features/map.txt')
        self.score = contextScore(ebdPath)

    def predict(self, query, qasTopN=1, docTopN=1, netTopN=1):
        def process(text):
            ans = []
            print('=================raw text==================')
            print(text)
            print('===================================')
            lines = self.BrealLine(text)
            for line in lines:
                predictions = self.predictor.predict(
                    line, query, candidates=None, top_n=qasTopN)
                for p in predictions:
                    ans.append({
                        'text': line,
                        'contextScore': self.score.releventScore(line, query),
                        'answer': p[0],
                        'answerScore': p[1]
                    })
            return ans
        query = self.NormAndFilt(query)
        logger.info('[question after filting : %s ]' % query)
        ans = []
        if netTopN > 0:
            docs = self.retrieveFromNet(query, k=netTopN)
            logger.info('[retreive from net : %s | expect : %s]' %
                        (len(docs), netTopN))
            for i, text in enumerate(docs):
                ans.extend(process(text))

        logger.info('[retreive from db]')
        doc_names, doc_scores = self.ranker.closest_docs(query, k=docTopN)
        for i, doc in enumerate(doc_names):
            cursor = self.db.execute(
                'SELECT text from documents WHERE id = "%s"' % doc)
            for row in cursor:
                text = row[0]
            ans.extend(process(text))
        return ans

    def retrieveFromNet(self, text, k=1):
        texts = retriver(text, k)
        return [self.NormAndFilt(t) for t in texts]

    def BrealLine(self, text, minLen=64, maxLen=128):
        curr = []
        curr_len = 0

        def replace(match):
            s = text[match.start():match.end()]
            return s.replace('.', '$$$')
        text = re.sub('[[0-9]+\.[0-9]+]', replace, text)
        for split in re.split('[\n+\.+\?+\!+]', text):
            split = split.strip().replace('$$$', '.')
            if len(split) == 0:
                continue
            # Maybe group paragraphs together until we hit a length limit
            if len(curr) > 0 and curr_len + len(split) > maxLen:
                yield ' '.join(curr)
                curr = []
                curr_len = 0
            curr.append(split)
            curr_len += len(split)
        if len(curr) > 0:
            yield ' '.join(curr)

    def NormAndFilt(self, text):
        return self.filter.filt(normalize(text))


class filtText(object):
    def __init__(self, path):
        self.table = {}
        if not path:
            return

        with open(path, encoding='utf-8') as f:
            for line in f:
                l = line.split(' ')
                self.table[l[0]] = l[1]

    def filt(self, text, ng=1):
        for key in self.table.keys():
            val = self.table[key].replace('\n', '')
            l = text.split(key)
            ngram = None
            bngram = None
            if key in val:
                ngram = val[val.find(key) +
                            len(key): val.find(key) + len(key) + ng]
                bngram = val[ngram if val.find(
                    key) - ng >= 0 else 0:val.find(key)]
            idx = 0
            tout = ''
            for sep in l:
                tout += sep
                if idx + 1 < len(l) and key in val and not\
                    (ngram and len(l[idx + 1]) > len(ngram) and not
                     l[idx + 1][0:len(ngram)] == ngram) and not\
                        (bngram and len(text) > len(bngram) and not
                         text[-len(bngram):] == bngram):
                    tout += key
                elif idx + 1 < len(l):
                    tout += val
                idx += 1
            text = tout

        return text


class contextScore(object):
    def __init__(self, dictpath=None):
        self.dic = {}
        if not dictpath:
            return

        logger.info('[ loading embedding for text score ]')
        with open(dictpath) as f:
            for line in f:
                parsed = line.rstrip().split(' ')
                w = normalize(parsed[0])
                vec = [float(i) for i in parsed[1:]]
                self.dic[w] = vec

    def releventScore(self, text, ques, tfidf={}):
        def filtWord(li):
            # filt out stop words
            nl = []
            for l in li:
                if l not in STOPWORDS:
                    nl.append(l)
            return nl

        def sims(t, q):
            if t in self.dic.keys() and q in self.dic.keys():
                vector1 = self.dic[t]
                vector2 = self.dic[q]
                dot_product = 0.0
                normA = 0.0
                normB = 0.0
                for a, b in zip(vector1, vector2):
                    dot_product += a * b
                    normA += a**2
                    normB += b**2
                if normA == 0.0 or normB == 0.0:
                    return 0
                else:
                    return dot_product / ((normA * normB)**0.5)
            else:
                l = max([len(t), len(q)])
                if Levenshtein.distance(t, q) < l:
                    return (l - Levenshtein.distance(t, q)) / l * 0.7
                else:
                    return 0

        ttoks = filtWord(jieba.lcut_for_search(text))
        qtoks = filtWord(jieba.lcut_for_search(ques))

        score = 0
        if len(ttoks) == 0:
            return 0
        for tword in ttoks:
            for qword in qtoks:

                if tword in tfidf.keys():
                    rate = tfidf[tword]
                else:
                    rate = 1

                if tword == qword:
                    # exact match
                    score += rate * 2.5
                elif sims(tword, qword) > 0.4:
                    # similar
                    score += sims(tword, qword) * rate
        # remove advantage of length
        return score / len(ttoks) / len(qtoks) * 100
