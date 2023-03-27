from bigbang.archive import load as load_archive
from bigbang.archive import Archive
import bigbang.ingress.mailman as mailman
import bigbang.analysis.process as process
import networkx as nx
import pandas as pd
from pprint import pprint as pp
import pytz
import numpy as np
import math
import nltk
from itertools import repeat
from nltk.stem.lancaster import LancasterStemmer
st = LancasterStemmer()
from nltk.corpus import stopwords
import re

__all__ = ["get_word_trends"]

stem = False

def count_word(text,word):
    if not text:
        return 0
    
    if len(word.split(" ")) <= 1:
        ## normalize the text - remove apostrophe and punctuation, lower case
        normalized_text = re.sub(r'[^\w]', ' ',text.replace("'","")).lower()
    
        tokenized_text = nltk.tokenize.word_tokenize(normalized_text)

        if stem:
            tokenized_text = [st.stem(t) for t in tokenized_text]
    
        return tokenized_text.count(word)
    else:
        return text.lower().count(word)


def get_word_trends(archive):

    archives_data = archive

    checkwords = ["protocol","middlebox","standard","chair"]

    for word in checkwords:
        archives_data[word] = archives_data['Body'].apply(lambda x: count_word(x,word))

    archives_data = archives_data.dropna(subset=['Date'])
    archives_data['Date-ordinal'] = archives_data['Date'].apply(lambda x: x.toordinal())
    archives_data_sums = archives_data.groupby('Date-ordinal').sum()

    return archives_data_sums
