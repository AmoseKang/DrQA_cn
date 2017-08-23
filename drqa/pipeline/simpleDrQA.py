import re
import sqlite3
from drqa import retriever


# singel thread simple DrQA agent
class SDrQA(object):
    def __init__(self, predictor, rankerPath, dbPath):
        self.predictor = predictor
        self.ranker = retriever.get_class('tfidf')(tfidf_path=rankerPath)
        conn = sqlite3.connect(dbPath)
        self.db = conn.cursor()

    def predict(self, query, qasTopN=1, docTopN=1):
        doc_names, doc_scores = self.ranker.closest_docs(query, docTopN)
        ans = []
        for i, doc in enumerate(doc_names):
            cursor = self.db.execute(
                'SELECT text from documents WHERE id = "%s"' % doc)
            for row in cursor:
                text = row[0]
            lines = self.BrealLine(text)
            for line in lines:
                predictions = self.predictor.predict(
                    line, query, None, qasTopN)
                for p in predictions:
                    ans.append({
                        'id': doc,
                        'text': line,
                        'dbScore': doc_scores[i],
                        'answer': p[0],
                        'answerScore': p[1]
                    })
        return ans

    def BrealLine(self, text, minLen=64, maxLen=192):
        return re.split('\n|\.|\?|\!', text)
