

from scipy import spatial
import pandas as pd
from parser_module import Parse
from ranker import Ranker
import glob
import utils

import numpy as np
import collections
from nltk.corpus import stopwords
import os
import re
import string
import time
from gensim.scripts.glove2word2vec import glove2word2vec
from gensim.models import KeyedVectors

import numpy as np
import networkx as nx
import matplotlib.pyplot as plt
from nltk.corpus import stopwords
from nltk.tokenize import sent_tokenize
from nltk.stem.wordnet import WordNetLemmatizer
from sklearn.metrics.pairwise import cosine_similarity
from operator import itemgetter, attrgetter
import itertools
class Searcher:

    def __init__(self, inverted_index):
        """
        :param inverted_index: dictionary of inverted index
        """
        self.stemming = None
        self.parser = Parse()
        self.ranker = Ranker()
        self.inverted_index = inverted_index


    def relevant_docs_from_posting(self, query):
        """
        This function loads the posting list and count the amount of relevant documents per term.
        :param query: query
        :return: dictionary of relevant documents.
        """

        start_time = time.time()


        glove_input_file = 'glove.twitter.27B.25d.txt'
        word2vec_output_file = 'glove.twitter.27B.25d.txt.word2vec'
        glove2word2vec(glove_input_file, word2vec_output_file)

        # load the Stanford GloVe model
        filename = 'glove.twitter.27B.25d.txt.word2vec'
        model = KeyedVectors.load_word2vec_format(filename, binary=False)

        print("--- %s seconds model load---" % (time.time() - start_time))

        word_list={}
        try:
            for term in query:
                result2 = model.most_similar(term)
                to_arr = [x[0] for x in result2]
                for w in to_arr[0:3]:
                    if w in word_list:
                        word_list[w] += 1
                    else:
                        word_list[w] = 1
            # test=find_closest_embeddings(word_embeddings["dog"])
            # print(test[0:3])
        except:
            print('term {} not found in similarity'.format(term))



        print("--- %s seconds words2 load---" % (time.time() - start_time))


        # print(result2)



        relevant_docs={}
        # tokenized_query='hydroxychloroquine, zinc, and Zithromax can cure coronavirus'
        words_list = []
        once = True
        for term in word_list:
            try: # an example of checks that you have to do
                # files_list = []
                if term[0].islower():
                    file='\\lowers\\posting_file_'+term[0]
                    posting_file = utils.load_obj(file)
                    posting_file = posting_file[0]
                    posting_file = posting_file[term]
                elif term[0].islower():
                    file='\\uppers\\posting_file_'+term[0]
                    posting_file = utils.load_obj(file)
                    posting_file = posting_file[0][term]
                else:
                    file='\\others\\posting_file_'+term[0]
                    posting_file = utils.load_obj(file)
                    posting_file = posting_file[0][term]

                for item in posting_file:
                    if item[0] not in relevant_docs:
                        relevant_docs[item[0]]=[]
                    relevant_docs[item[0]].append(term)

                    # if item[0] in relevant_docs:
                    #     relevant_docs[item[0]] += 1
            except:
                print('term {} not found in posting'.format(term))



        relevant_docs= dict(sorted(relevant_docs.items(), key=lambda item: len(item[1]), reverse=True))
        relevant_docs= dict(itertools.islice(relevant_docs.items(), 200))


        return relevant_docs
