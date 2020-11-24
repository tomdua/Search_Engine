import codecs
import json
from scipy import spatial
from parser_module import Parse
from ranker import Ranker
from nltk.corpus import words
import utils
import os
import re
import string
import numpy as np
from nltk.corpus import stopwords
import time

class Searcher:
    def __init__(self, inverted_index,dict_dictionary):
        """
        :param inverted_index: dictionary of inverted index
        """
        self.stemming = None
        self.parser = Parse()
        self.ranker = Ranker()
        self.inverted_index = inverted_index
        self.dict_dictionary=dict_dictionary


    def loadGloveModel ( self,gloveFile ) :
        """
        It loads embedding provided by glove which is saved as binary file. Loading of this model is
        about  second faster than that of loading of txt glove file as model.
        :param embeddings_path: path of glove file.
        :return: glove model
        """
        word_embeddings = {}
        f = open(gloveFile, encoding='utf-8')
        for line in f:
            values = line.split()
            word = values[0]
            coefs = np.asarray(values[1:], dtype='float32')
            # test=len(coefs)
            if len(coefs)==25:
                word_embeddings[word] = coefs
        f.close()
        return word_embeddings


    def get_w2v ( self,sentence , model ) :
        """
        :param sentence: inputs a single sentences whose word embedding is to be extracted.
        :param model: inputs glove model.
        :return: returns numpy array containing word embedding of all words    in input sentence.
        """
        for val in sentence.split():
            if val:
                dsf= np.array([model.get(val , np.zeros(100)) ] , dtype=np.float64)
        return dsf

    def find_closest_embeddings (self,modal,embedding):
        return sorted(modal.keys() ,
                      key=lambda word : spatial.distance.euclidean(modal[word] , embedding))





    def relevant_docs_from_posting(self, query):
        """
        This function loads the posting list and count the amount of relevant documents per term.
        :param query: query
        :return: dictionary of relevant documents.
        """
        # glove_file = self.convert_to_binary('glove.twitter.27B.25d')
        # self.load_glove()
        # self.gloVe()
        # modaalll=self.find_closest_embeddings(model,model['child'])
        # modaalll
        # similarity1= np.array(similarity)
        # similarity1
        # query.append('soccer')
        similarity = []
        start_time = time.time()
        # query = re.sub(r'www\.\S+\.com', '', query)

        model = self.loadGloveModel('glove.twitter.27B.25d.txt')
        print("--- %s seconds dict in---" % (time.time() - start_time))

        # similarity=self.get_w2v('This is demonstration' , model)

        print("--- %s seconds dict in---" % (time.time() - start_time))
        for term in query :
            try:
                terms = self.find_closest_embeddings(model,model[term.lower()])
                similarity = similarity + terms[0:3]
            except:
                print("proble with")

        print("--- %s seconds dict in---" % (time.time() - start_time))
        indexes_in_posting=[]
        for term in similarity :
            try :  # an example of checks that you have to do
                if term in self.inverted_index:
                    indexes_in_posting.append(self.dict_dictionary[0][term][2])
                    #list_in_posting = posting_file[indexes_in_posting[0],indexes_in_posting[1]]
                    # x = indexes_in_posting[0]
                    # y = indexes_in_posting[1]
                    #test= posting_file['s'][135]
                    # list_in_posting = posting_file[x][y]
                    # for item in list_in_posting:
                    #     if item[1] not in relevant_docs.keys():
                    #         relevant_docs[item[1]] = 1
                    #     else:
                    #         relevant_docs[item[1]] += 1
            except:
                print('term {} not found in posting'.format(term))



        return indexes_in_posting



        # # with open('posting_file.txt') as json_file:
        # #     posting_file = json.load(json_file)
        # # self.ranker.posting_file=posting_file
        # #self.ranker.inverted_idx= self.inverted_index
        # relevant_docs = {}
        #
        # gloveFile = "glove.twitter.27B.25d.txt"
        # dim = 200
        # stop = set(stopwords.words('english'))
        #
        #
        # def loadGloveModel(gloveFile):
        #     word_embeddings = {}
        #     f = open(gloveFile, encoding='utf-8')
        #     for line in f:
        #         values = line.split()
        #         word = values[0]
        #         coefs = np.asarray(values[1:], dtype='float32')
        #         # test=len(coefs)
        #         if len(coefs)==25:
        #             word_embeddings[word] = coefs
        #     f.close()
        #     return word_embeddings
        #
        # word_embeddings = loadGloveModel(gloveFile)
        #
        # print("Vocab Size = ", len(word_embeddings))
        # #test=word_embeddings.keys()
        # def find_closest_embeddings(embedding):
        #     return sorted(word_embeddings.keys(),key=lambda word: spatial.distance.euclidean(word_embeddings[word], embedding))
        #
        #
        #
        #
        # # test=find_closest_embeddings(word_embeddings["king"])
        # # print(test[1:6])
        # #
        # # tokenized_query=self.parser.parse_sentence(query)
        # #
        # # if self.stemming:
        # #     tokenized_query = [self.stemming.stem_term(w) for w in tokenized_query if
        # #                    self.stemming.stem_term(w) not in stop ]
        # # else:
        # #     tokenized_query = [w for w in tokenized_query if w not in stop]
        #
        # # similarity = []
        # # for sent in query :
        # #     query_vec = word_embeddings([query])[0]
        # #     sim = cosine(query_vec , word_embeddings.encode([sent])[0])
        # #     print("Sentence = " , sent , "; similarity = " , sim)
        # similarity = []
        #
        # for term in query :
        #     if term in words.words:
        #         terms = find_closest_embeddings(word_embeddings[term])
        #         similarity = similarity + terms[1:4]
        # terms=[]
        # for term in similarity :
        #     try :  # an example of checks that you have to do
        #         if term in self.inverted_index:
        #             indexes_in_posting=self.dict_dictionary[0][term][2]
        #             #list_in_posting = posting_file[indexes_in_posting[0],indexes_in_posting[1]]
        #             # x = indexes_in_posting[0]
        #             # y = indexes_in_posting[1]
        #             #test= posting_file['s'][135]
        #             # list_in_posting = posting_file[x][y]
        #             # for item in list_in_posting:
        #             #     if item[1] not in relevant_docs.keys():
        #             #         relevant_docs[item[1]] = 1
        #             #     else:
        #             #         relevant_docs[item[1]] += 1
        #     except:
        #         print('term {} not found in posting'.format(term))
        #
        #
        #
        # return relevant_docs
        #

        # id2word = ["PAD" , "UNKNOWN" , "the" , "there" , "year" , "when"]
        #         # word2id = {word : id for id , word in enumerate(id2word)}
        #         #
        #         # import numpy as np
        #         #
        #         # # INITIALIZE EMBEDDINGS TO RANDOM VALUES
        #         # embed_size = 100
        #         # vocab_size = len(id2word)
        #         # sd = 1 / np.sqrt(embed_size)  # Standard deviation to use
        #         # weights = np.random.normal(0 , scale=sd , size=[vocab_size , embed_size])
        #         # weights = weights.astype(np.float32)
        #         #
        #         # from io import open
        #         # file = "glove.twitter.27B.25d.txt"
        #         #
        #         # # EXTRACT DESIRED GLOVE WORD VECTORS FROM TEXT FILE
        #         # with open(file , encoding="utf-8" , mode="r") as textFile :
        #         #     for line in textFile :
        #         #         # Separate the values from the word
        #         #         line = line.split()
        #         #         word = line[0]
        #         #
        #         #         # If word is in our vocab, then update the corresponding weights
        #         #         id = word2id.get(word , None)
        #         #         if id is not None :
        #         #             weights[id] = np.array(line[1 :] , dtype=np.float32)

