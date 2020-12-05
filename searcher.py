
import pickle

from gensim.scripts.glove2word2vec import glove2word2vec

from ranker import Ranker
from collections import OrderedDict
import time
from gensim.models import KeyedVectors
from collections import Counter
import numpy as np
import itertools

class Searcher:

    def __init__(self):
        """
        :param inverted_index: dictionary of inverted index
        """
        self.ranker = Ranker()
        self.inverted_index = {}
        self.ids= []
        # glove_input_file = 'glove.twitter.27B.25d.txt'
        glove_input_file = '../../../../glove.twitter.27B.25d.txt'
        word2vec_output_file = 'glove.twitter.27B.25d.txt.word2vec'
        glove2word2vec(glove_input_file, word2vec_output_file)
        self.model = KeyedVectors.load_word2vec_format(word2vec_output_file, binary=False)




    def relevant_docs_from_posting(self, query ,stemming):
        """
        This function loads the posting list and count the amount of relevant documents per term.
        :param query: query
        :return: dictionary of relevant documents.
        """

        start_time = time.time()

        def get_vector(term):
            try:
                return self.model[term]
            except:
                return np.zeros((25,))


        print("--- %s seconds model load---" % (time.time() - start_time))
        word_list={}
        for term in query:
            try:
                word_list[term] = 1
                result2 = self.model.most_similar(term)
                to_arr = [x[0] for x in result2]
                for w in to_arr[0:3]:
                    if w in word_list:
                        word_list[w] += 1
                    else:
                        word_list[w] = 1
            except :
                print('term {} not found in similarity'.format(term))

        query_vector= {}
        if len(query) != 0:
            v = sum([get_vector(w) for w in query]) / (len(query) + 0.001)
        else:
            v = np.zeros((25,))
        query_vector=v

        for term in query:
            try:
                if term[0].islower():
                    if stemming:
                        file='\\stemming\\lowers\\posting_file_'+term[0]
                    else:
                        file='\\lowers\\posting_file_'+term[0]
                    self.load_doc(term,file)
                elif term[0].isupper():
                    if stemming:
                        file = '\\stemming\\uppers\\posting_file_' + term[0]
                    else:
                        file='\\uppers\\posting_file_'+term[0]
                    self.load_doc(term,file)
                else:
                    if stemming:
                        file = '\\stemming\\others\\posting_file_'+term[0]
                    else:
                        file='\\others\\posting_file_'+term[0]
                    self.load_doc(term,file)

            except Exception as e:
                print(e)
                print('term {} not found in posting'.format(term))

        relevant = Counter(self.ids)
        print("--- %s seconds found relevant docs---" % (time.time() - start_time))
        relevant_docs = OrderedDict(sorted(relevant.items(), key=lambda x: x[1], reverse=True))

        relevant_docs= dict(itertools.islice(relevant_docs.items(), 2000))

        return relevant_docs,self.model,query_vector

    def load_doc(self, term, string):
        with open('./posting/' + string + '.pkl', 'rb') as f:
            while 1:
                try:
                    objs = pickle.load(f)
                    if term in objs:
                        ids_to_add=objs[term]
                        self.ids=self.ids+list(ids_to_add.keys())
                except EOFError:
                    break