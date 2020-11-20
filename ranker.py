import json

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
        #pass



    #@staticmethod
    def rank_relevant_doc(self,relevant_doc):


        # gloveFile = "glove.twitter.27B.200d.txt"
        # dim = 200
        #
        # stop = set(stopwords.words('english'))
        # exclude = set(string.punctuation)
        # lemma = WordNetLemmatizer()
        #
        # def rem_ascii(s):
        #     return "".join(s)
        #
        # # Cleaning the text sentences so that punctuation marks, stop words and digits are removed.
        # def clean(doc):
        #     stop_free = " ".join([i for i in doc.lower().split() if i not in stop])
        #     punc_free = ''.join(ch for ch in stop_free if ch not in exclude)
        #     processed = re.sub(r"\d+", "", punc_free)
        #     return processed
        #
        # def loadGloveModel(gloveFile):
        #     word_embeddings = {}
        #     f = open(gloveFile, encoding='utf-8')
        #     for line in f:
        #         values = line.split()
        #         word = values[0]
        #         coefs = np.asarray(values[1:], dtype='float32')
        #         word_embeddings[word] = coefs
        #     f.close()
        #     return word_embeddings
        #
        # word_embeddings = loadGloveModel(gloveFile)
        #
        # print("Vocab Size = ", len(word_embeddings))
        #
        # text = """SBI, PNB, HDFC, ICICI,  Debit Card Customers: If you are using a bank debit card which doesn't have EMV (Europay, Mastercard and Visa), then you may have to face a problem during money withdrawal from the ATM after 31st December 2019 as your debit card may be blocked from 1st january 2020. According to the Reserve Bank of India (RBI) guidelines, all Indian banks need to replace the magnetic debit card of their customers with a new EMV card. This debit card replacement is mandatory as it is aimed at meeting the international payment standards. Hence, SBI, PNB, HDFC Bank, ICICI Bank or any other bank customers who are using a magnetic debit card are advised to replace their debit card otherwise they will have to face difficulty in money withdrawal from the ATM. The RBI guidelines say all Indian banks will have to replace all magnetic chip-based debit cards with EMV and PIN-based cards by 31st December 2019. Keeping in view of the continuing online frauds on magnetic stripe cards, the RBI has proposed to deactivate them by 31st December 2019. So, all magnetic chip-based debit cards will be deactivated from 1st January 2020 (irrespective of the validity of the existing magnetic SBI debit cards). All banks are sending messages to their customers via various means asking them to replace their magnetic chip-based debit card by a new EMV debit card. The SBI warned its debit cardholders through a tweet citing, "Apply now to change your Magnetic Stripe Debit Cards to the more secure EMV Chip and PIN-based SBI Debit card at your home branch by 31st December 2019. Safeguard yourself with guaranteed authenticity, greater security for online payments and added security against fraud". So, the SBI has made it clear that SBI debit card will be blocked if it is a magnetic card. In fact, the SBI has already started deactivating the SBI cards of those SBI accounts in which PAN or Form 60 is not updated."""
        # print(text)
        # sentences = sent_tokenize(text)
        # cleaned_texts = [rem_ascii(clean(sentence)) for sentence in sentences]
        #
        # sentence_vectors = []
        # for i in cleaned_texts:
        #     if len(i) != 0:
        #         v = sum([word_embeddings.get(w, np.zeros((dim,))) for w in i.split()]) / (len(i.split()) + 0.001)
        #     else:
        #         v = np.zeros((dim,))
        #     sentence_vectors.append(v)
        #
        # sim_mat = np.zeros([len(cleaned_texts), len(cleaned_texts)])
        # for i in range(len(sentences)):
        #     for j in range(len(sentences)):
        #         if i != j:
        #             sim_mat[i][j] = \
        #             cosine_similarity(sentence_vectors[i].reshape(1, dim), sentence_vectors[j].reshape(1, dim))[0, 0]
        # sim_mat = np.round(sim_mat, 3)
        # print(sim_mat)

        # # Creating the network graph
        # nx_graph = nx.from_numpy_array(sim_mat)
        # plt.figure(figsize=(10, 10))
        # pos = nx.spring_layout(nx_graph)
        # nx.draw(nx_graph, with_labels=True, font_weight='bold')
        # nx.draw_networkx_edge_labels(nx_graph, pos, font_color='red')
        # plt.show()
        #
        # scores = nx.pagerank(nx_graph)
        # print(scores)
        #
        # ranked_sentences = sorted(((scores[i], i) for i, s in enumerate(sentences)), reverse=True)
        # arranged_sentences = sorted(ranked_sentences[0:int(len(sentences) * 0.5)], key=lambda x: x[1])
        # print("\n".join([sentences[x[1]] for x in arranged_sentences]))


        """
        This function provides rank for each relevant document and sorts them by their scores.
        The current score considers solely the number of terms shared by the tweet (full_text) and query.
        :param relevant_doc: dictionary of documents that contains at least one term from the query.
        :return: sorted list of documents by score
        """
        return sorted(relevant_doc.items(), key=lambda item: item[1], reverse=True)

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