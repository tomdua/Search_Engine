import collections
import re
import time





class Indexer:

    def __init__(self, config):
        self.indexing_temp = {}
        self.entity_temp = {}
        self.posting_file = {}
        self.config = config
        self.documents_info = {}
        self.AB_dict_posting = {}
        self.dict_dictionary = {}
        #self.df = {}

    def small_big_latter ( self, entity,indexing_temp, document_dictionary, term ) :
        try :
            entity_flag=False
            if term in entity :
                if entity[term] == 1 :
                    document_dictionary.pop(term)
                    term=None
                    return entity,document_dictionary,term

            if term[0].isupper() :
                if term.lower() in indexing_temp :
                    term1 = term.lower()
                    if term1 in document_dictionary :
                        document_dictionary[term1] = document_dictionary[term1] + document_dictionary.pop(term)
                    if term1 not in document_dictionary :
                        document_dictionary[term1] = document_dictionary.pop(term)
                    if term in indexing_temp :
                        indexing_temp[term1] = indexing_temp[term1] + indexing_temp.pop(term)
                    term = term1

                else :
                    term2 = term.upper()
                    if term2 in document_dictionary :
                        document_dictionary[term2] = document_dictionary[term2] + document_dictionary.pop(term)
                    if term2 not in document_dictionary :
                        document_dictionary[term2] = document_dictionary.pop(term)
                    if term2 in indexing_temp and term in indexing_temp :
                        indexing_temp[term2] = indexing_temp[term2] + indexing_temp.pop(term)
                    if term2 not in indexing_temp and term in indexing_temp :
                        indexing_temp[term2] = indexing_temp.pop(term)
                    term = term2
                return entity,document_dictionary,term
            else:
                return entity,document_dictionary,term
        except Exception as e:
            print(e)


    def add_new_doc(self, document):
        """
        This function perform indexing process for a document object.
        Saved information is captures via two dictionaries ('inverted index' and 'posting')
        :param document: a document need to be indexed.
        :return: -
        """
        # start_time = time.time()

        document_dictionary = document.term_doc_dictionary
        # Go over each term in the doc
        for term in dict(document_dictionary) :
            try :
                # if term in self.entity_temp :
                #     if self.entity_temp[term] == 1 :
                #         document_dictionary.pop(term)
                #         # self.indexing_temp.pop(term)
                #         continue
                    # entity_temp[term]
                    # continue

                if term is '' :
                    continue
                else :
                    self.entity_temp,document_dictionary,term = self.small_big_latter(self.entity_temp,self.indexing_temp,document_dictionary,term)
                if term is None :
                    continue
                # if term[0].isupper() :
                #     if term.lower() in self.indexing_temp :
                #         term1 = term.lower()
                #         if term1 in document_dictionary :
                #             document_dictionary[term1] = document_dictionary[term1] + document_dictionary.pop(term)
                #         if term1 not in document_dictionary :
                #             document_dictionary[term1] = document_dictionary.pop(term)
                #         if term in self.indexing_temp :
                #             self.indexing_temp[term1] = self.indexing_temp[term1] + self.indexing_temp.pop(term)
                #         term = term1
                #
                #     else :
                #         term2 = term.upper()
                #         if term2 in document_dictionary :
                #             document_dictionary[term2] = document_dictionary[term2] + document_dictionary.pop(term)
                #         if term2 not in document_dictionary :
                #             document_dictionary[term2] = document_dictionary.pop(term)
                #         if term2 in self.indexing_temp and term in self.indexing_temp :
                #             self.indexing_temp[term2] = self.indexing_temp[term2] + self.indexing_temp.pop(term)
                #         if term2 not in self.indexing_temp and term in self.indexing_temp :
                #             self.indexing_temp[term2] = self.indexing_temp.pop(term)
                #         term = term2
                # print("--- %s seconds dict in---" % (time.time() - start_time))

                first = False
                if term not in self.posting_file :
                    self.posting_file[term] = []
                    first = True
                if term[0] not in self.AB_dict_posting :
                    self.AB_dict_posting[term[0]] = {}

                doc_pos_term = document.doc_pos.get(term.lower())
                self.posting_file[term].append(
                    (term , document.tweet_id , document.term_doc_dictionary[term] , doc_pos_term))
                if first :
                    self.AB_dict_posting[term[0]][term] = self.posting_file[term]

                # indices = self.AB_dict_posting[term[0]].index(term)

                # rx2 = re.compile(fr"(?i)\b{term}\b")
                # text0 = rx2.findall(document.full_text)
                # if text0:
                #     termInDoc = text0[0]

                if term not in self.dict_dictionary :
                    self.dict_dictionary[term] = (
                    self.indexing_temp[term] , len(self.AB_dict_posting[term[0]][term]) , term[0])

                # print("--- %s seconds dict out---" % (time.time() - start_time))


            except Exception as e :
                print(e)
                print('problem with the following key {}'.format(term[0]))
        # print("--- %s seconds documents in---" % (time.time() - start_time))

        try :
            max_tf = document.term_doc_dictionary[
                max(document.term_doc_dictionary , key=document.term_doc_dictionary.get)]
            unique_num_value = len(set(document.full_text.split()))
            # unique_num = 0

            # for key, value in document_dictionary.items():
            #     if value == unique_num_value:
            #         unique_num = unique_num + 1

            self.documents_info[document.tweet_id] = {'max_tf' : max_tf , 'unique_num' : unique_num_value ,
                                                      'tweet_length' : document.doc_length}
        except :
            print('problem with {}'.format(document_dictionary))






