import json
import math

from numpy import asarray, zeros
import numpy as np

from numpy import array
from nltk.tokenize import word_tokenize
# from pandas import np
from scipy import spatial

# from glove_py import GloVe
import nltk
from nltk.corpus import brown
import logging
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

class Ranker:
    def __init__(self):
        self.posting_file= {}
        self.inverted_idx= {}
        self.documents = []
        #pass


    #@staticmethod
    def rank_relevant_doc(selfs, relevant_doc, dict_dictionary, documents_info , stemming_bool):

        twitts_dict = []
        for id in relevant_doc:

            # doc = documents_list_after_parse[id]`
            twitts_dict.append(relevant_doc[id])

        gloveFile = "glove.twitter.27B.25d.txt"
        dim = 25

        def loadGloveModel(gloveFile):
            word_embeddings = {}
            f = open(gloveFile, encoding='utf-8')
            for line in f:
                values = line.split()
                word = values[0]
                coefs = np.asarray(values[1:], dtype='float32')
                word_embeddings[word] = coefs
            f.close()
            return word_embeddings

        word_embeddings = loadGloveModel(gloveFile)

        sentence_vectors = []
        for dict in twitts_dict:
            if len(dict) != 0:
                v = sum([word_embeddings.get(w, np.zeros((dim,))) for w in dict]) / (len(dict) + 0.001)
            else:
                v = np.zeros((dim,))
            sentence_vectors.append(v)

        sim_mat = np.zeros([len(twitts_dict), len(twitts_dict)])
        for i in range(len(twitts_dict)):
            for j in range(len(twitts_dict)):
                if i != j:
                    sim_mat[i][j] = \
                    cosine_similarity(sentence_vectors[i].reshape(1, dim), sentence_vectors[j].reshape(1, dim))[0, 0]
        sim_mat = np.round(sim_mat, 3)
        print(sim_mat)
        print(nx.__version__)

        #Creating the network graph
        nx_graph = nx.from_numpy_array(sim_mat)
        # plt.figure(figsize=(10, 10))
        # pos = nx.spring_layout(nx_graph)
        # nx.draw(nx_graph, with_labels=True, font_weight='bold')
        # nx.draw_networkx_edge_labels(nx_graph, pos, font_color='red')
        # plt.show()

        scores = nx.pagerank(nx_graph)
        print(scores)

        ranked_sentences = sorted(((scores[i], i) for i, s in enumerate(twitts_dict)), reverse=True)
        arranged_sentences = sorted(ranked_sentences[0:int(len(twitts_dict) * 0.5)], key=lambda x: x[0],reverse=True)

        print("\n".join([twitts_dict[x[1]] for x in arranged_sentences]))

        """
        This function provides rank for each relevant document and sorts them by their scores.
        The current score considers solely the number of terms shared by the tweet (full_text) and query.
        :param relevant_doc: dictionary of documents that contains at least one term from the query.
        :return: sorted list of documents by score
        """
        return sorted(relevant_doc.items(), key=lambda item: item[1], reverse=True)
    # def rank_relevant_doc(self, relevant_doc, dict_dictionary, documents_info, documents_list_after_parse):
    #     """
    #     This function provides rank for each relevant document and sorts them by their scores.
    #     The current score considers solely the number of terms shared by the tweet (full_text) and query.
    #     :param relevant_doc: dictionary of documents that contains at least one term from the query.
    #     :return: sorted list of documents by score
    #     """
    #
    #     # posting_file = self.load_postiong_file('a')
    #     # documents[relevant_doc[0]]
    #     # documents_info[document]
    #
    #     # self.posting_file= inverted_index
    #     # self.inverted_idx= inverted_index
    #     # self.dict_dictionary = dict_dictionary
    #     doc_score = {}
    #     doc_numbers = len(documents_list_after_parse)
    #
    #     for id in relevant_doc:
    #         doc = documents_list_after_parse[id]
    #         tf_max = documents_info[doc.tweet_id]['max_tf']
    #         score = 0
    #         for term in doc.term_doc_dictionary:
    #             tf = doc.term_doc_dictionary[term]
    #             df = dict_dictionary[term][1]
    #             score += (tf / tf_max) * math.log10(doc_numbers / df)
    #         doc_score[doc.tweet_id] = score
    #     return sorted(doc_score.items(), key=lambda item: item[1], reverse=True)


    #@staticmethod
    def retrieve_top_k(self,sorted_relevant_doc, k=1):
        """
        return a list of top K tweets based on their ranking from highest to lowest
        :param sorted_relevant_doc: list of all candidates docs.
        :param k: Number of top document to return
        :return: list of relevant document
        """
        return sorted_relevant_doc[:k]


    # def rank_relevant_id( self, list, docs ):
    #     self.ranker =list
    #     self.document=docs
    #     self.ranker