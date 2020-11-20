import json

from scipy import spatial

from parser_module import Parse
from ranker import Ranker
import utils
import os
import re
import string
import numpy as np
import networkx as nx
import matplotlib.pyplot as plt
from nltk.corpus import stopwords
from nltk.tokenize import sent_tokenize
from nltk.stem.wordnet import WordNetLemmatizer
from sklearn.metrics.pairwise import cosine_similarity

# import torch
# import torchtext
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

        # with open('posting_file.txt') as json_file:
        #     posting_file = json.load(json_file)
        # self.ranker.posting_file=posting_file
        self.ranker.inverted_idx= self.inverted_index
        relevant_docs = {}

        gloveFile = "glove.twitter.27B.200d.txt"
        dim = 200
        stop = set(stopwords.words('english'))


        def loadGloveModel(gloveFile):
            word_embeddings = {}
            f = open(gloveFile, encoding='utf-8')
            for line in f:
                values = line.split()
                word = values[0]
                coefs = np.asarray(values[1:], dtype='float32')
                # test=len(coefs)
                if len(coefs)==200:
                    word_embeddings[word] = coefs
            f.close()
            return word_embeddings

        word_embeddings = loadGloveModel(gloveFile)

        print("Vocab Size = ", len(word_embeddings))
        #test=word_embeddings.keys()
        def find_closest_embeddings(embedding):
            return sorted(word_embeddings.keys(),key=lambda word: spatial.distance.euclidean(word_embeddings[word], embedding))

        test=find_closest_embeddings(word_embeddings["king"])
        print(test[1:6])

        tokenized_query=self.parser.parse_sentence(query)

        if self.stemming:
            tokenized_query = [self.stemming.stem_term(w) for w in tokenized_query if
                           self.stemming.stem_term(w) not in stop ]
        else:
            tokenized_query = [w for w in tokenized_query if w not in stop]


        for term in tokenized_query:
            try: # an example of checks that you have to do






                if term in self.inverted_index.keys():
                    indexes_in_posting=[self.inverted_index[term][1],self.inverted_index[term][2]]
                    #list_in_posting = posting_file[indexes_in_posting[0],indexes_in_posting[1]]
                    x = indexes_in_posting[0]
                    y = indexes_in_posting[1]
                    #test= posting_file['s'][135]
                    # list_in_posting = posting_file[x][y]
                    # for item in list_in_posting:
                    #     if item[1] not in relevant_docs.keys():
                    #         relevant_docs[item[1]] = 1
                    #     else:
                    #         relevant_docs[item[1]] += 1
            except:
                print('term {} not found in posting'.format(term))



        return relevant_docs
