import numpy as np, re
from sklearn.base import BaseEstimator, TransformerMixin
from nltk import PorterStemmer
from urlextract import URLExtract
from scipy.sparse import csr_matrix
from collections import Counter
from html import unescape


urlextractor = URLExtract()
stemmer = PorterStemmer()

class EmailToWordCounterTransformer(BaseEstimator, TransformerMixin):
    def __init__(self, strip_headers=True, lower_case=True, remove_punctuation=True,
                 replace_urls=True, replace_numbers=True, stemming=True):
        
        self.strip_headers = strip_headers
        self.lower_case = lower_case
        self.remove_punctuation = remove_punctuation
        self.replace_urls = replace_urls
        self.replace_numbers = replace_numbers
        self.stemming = stemming

    def fit(self, X, y=None):
        return self
    
    def transform(self, X, y=None):
        X_transformed = []
        for email in X:
            text = email_to_text(email) or ""
            
            if self.lower_case:
                text = text.lower()
            
            if self.replace_urls:
                urls = list(set(urlextractor.find_urls(text)))
                for url in urls:
                    text.replace(url, " URL ")
            
            if self.replace_numbers:
                text = re.sub(r'\d+(?:\.\d*)?(?:[eE][+-]?\d+)?', 'NUMBER', text)
            
            if self.remove_punctuation:
                text = re.sub(r'\W+', ' ', text, flags=re.M)

            
            word_counts = Counter(text.split())
            if self.stemming:
                stemmed_word_counts = Counter()
                for word, count in word_counts.items():
                    stemmed_word = stemmer.stem(word)
                    stemmed_word_counts[stemmed_word] += count
                
                word_counts = stemmed_word_counts

            X_transformed.append(word_counts)
        return np.array(X_transformed)

class WordCounterToVectorTransformer(BaseEstimator, TransformerMixin):

    def __init__(self, vocabulary_size=100):
        self.vocabulary_size = vocabulary_size

    def fit(self, X, y=None):
        total_count = Counter()
        for word_count in X:
            for word, count in word_count.items():
                total_count[word] += min(count, 10)
        
        most_common = total_count.most_common(self.vocabulary_size)
        self.vocabulary = {word:index + 1 for index, (word, count) in enumerate(most_common)}
        return self
    
    def transform(self, X, y=None):
        rows = []
        cols = []
        data = []
        for row, word_count in enumerate(X):
            for word, count in word_count.items():
                rows.append(row)
                cols.append(self.vocabulary.get(word, 0)) #words not in vocab go in column zero
                data.append(count)
        return csr_matrix((data, (rows, cols)), shape=(len(X), self.vocabulary_size + 1))


def html_to_plain_text(html):
    text = re.sub("<head.*?>.*?</head>", "", html, flags=re.M | re.S | re.I)
    text = re.sub("<a\s.*?>", " HYPERLINK ", text, flags=re.M | re.S | re.I)
    text = re.sub("<.*?>", "", text, flags=re.M | re.S)
    text = re.sub(r"(\s*\n)+", "\n", text, flags=re.M | re.S)
    return unescape(text)

def email_to_text(email):
    html = None

    if isinstance(email, str):
        return email
    
    for part in email.walk():
        ctype = part.get_content_type()
        if not ctype in ('text/plain', 'text/html'):
            continue
        try:
            content = part.get_content()
        except:
            content = str(part.get_payload())
        if ctype == 'text/plain':
            return content
        else:
            html = content
        if html:
            return html_to_plain_text(html)