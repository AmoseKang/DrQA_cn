import re
import sqlite3
from drqa import retriever
from drqa.retriever.net_retriever import retriver


# singel thread simple DrQA agent
class SDrQA(object):
    def __init__(self, predictor, rankerPath, dbPath):
        self.predictor = predictor
        self.ranker = retriever.get_class('tfidf')(tfidf_path=rankerPath)
        conn = sqlite3.connect(dbPath)
        self.db = conn.cursor()
        self.filter = filtText('drqa/pipeline/map.txt')

    def predict(self, query, qasTopN=1, docTopN=1, fromNet=False):
        query = self.filter.filt(query)
        print('[question after filting : %s ]' % query)
        if fromNet:
            doc_names, doc_scores = self.retrieveFromNet(query, k=docTopN)
        else:
            doc_names, doc_scores = self.ranker.closest_docs(query, k=docTopN)
        ans = []
        for i, doc in enumerate(doc_names):
            cursor = self.db.execute(
                'SELECT text from documents WHERE id = "%s"' % doc)
            for row in cursor:
                text = row[0]
            print('=================raw text==================')
            print(text)
            print('===================================')
            lines = self.BrealLine(text)
            for line in lines:
                predictions = self.predictor.predict(
                    line, query, candidates=None, top_n=qasTopN)
                for p in predictions:
                    ans.append({
                        'id': doc,
                        'text': line,
                        'dbScore': doc_scores[i],
                        'answer': p[0],
                        'answerScore': p[1]
                    })
        return ans

    def retrieveFromNet(text, k=1):
        texts = retriver(text, k)
        return texts, [1 for i in texts]

    def BrealLine(self, text, minLen=64, maxLen=128):
        curr = []
        curr_len = 0
        for split in re.split('[\n+|\.+|\?+|\!+]', text):
            split = split.strip()
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


class filtText(object):
    def __init__(self, path):
        self.table = {}
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
                if idx + 1 < len(l) and not\
                    (ngram and len(l[idx + 1]) > len(ngram)
                     and not l[idx + 1][0:len(ngram)] == ngram) and not\
                        (bngram and len(text) > len(bngram) and not
                         text[-len(bngram):] == bngram):
                    tout += key
                elif idx + 1 < len(l):
                    tout += val
                idx += 1
            text = tout

        return text
