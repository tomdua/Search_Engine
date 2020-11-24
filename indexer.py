import collections
import re
import time


class Indexer:

    def __init__(self, config):
        self.indexing_temp = {}
        self.indexing_temp_with_stemming ={}
        self.entity_temp = {}
        self.posting_file = {}
        self.posting_file_with_stemming = {}

        self.config = config
        self.documents_info = {}
        self.documents_info_with_stemming = {}

        self.AB_dict_posting = {}
        self.AB_dict_posting_with_stemming = {}

        self.dict_dictionary = {}
        self.dict_dictionary_with_stemming = {}

    def small_big_letters(self, entity, indexing_temp, document_dictionary, term , stemm):
        try:
            if term in entity:
                if entity[term] == 1:
                    document_dictionary.pop(term)
                    term = None
                    return entity, document_dictionary, term

            if term[0].isupper() and not stemm:
                if term.lower() in indexing_temp:
                    term1 = term.lower()
                    if term1 in document_dictionary:
                        document_dictionary[term1] = document_dictionary[term1] + document_dictionary.pop(term)
                    if term1 not in document_dictionary:
                        document_dictionary[term1] = document_dictionary.pop(term)
                    if term in indexing_temp:
                        indexing_temp[term1] = indexing_temp[term1] + indexing_temp.pop(term)
                    term = term1

                else:
                    term2 = term.upper()
                    if term2 in document_dictionary:
                        document_dictionary[term2] = document_dictionary[term2] + document_dictionary.pop(term)
                    if term2 not in document_dictionary:
                        document_dictionary[term2] = document_dictionary.pop(term)
                    if term2 in indexing_temp and term in indexing_temp:
                        indexing_temp[term2] = indexing_temp[term2] + indexing_temp.pop(term)
                    if term2 not in indexing_temp and term in indexing_temp:
                        indexing_temp[term2] = indexing_temp.pop(term)
                    term = term2
                return entity, document_dictionary, term
            else:
                return entity, document_dictionary, term
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
        # id = document.tweet_id
        document_dictionary = document.term_doc_dictionary
        # Go over each term in the doc
        if len(document_dictionary)>0:
            for term in dict(document_dictionary):
                try:


                    self.entity_temp, document_dictionary, term = self.small_big_letters(self.entity_temp,
                                                                                        self.indexing_temp,
                                                                                        document_dictionary, term , False)
                    if term is None:
                        continue

                    first = False
                    if term not in self.posting_file:
                        self.posting_file[term] = []
                        first = True
                    if term[0] not in self.AB_dict_posting:
                        self.AB_dict_posting[term[0]] = {}

                    doc_pos_term = document.doc_pos.get(term.lower())
                    self.posting_file[term].append(
                        (document.tweet_id, document.term_doc_dictionary[term], doc_pos_term))
                    if first:
                        self.AB_dict_posting[term[0]][term] = self.posting_file[term]


                    # rx2 = re.compile(fr"(?i)\b{term}\b")
                    # text0 = rx2.findall(document.full_text)
                    # if text0:
                    #     termInDoc = text0[0]

                    self.dict_dictionary[term] = (self.indexing_temp[term], len(self.AB_dict_posting[term[0]][term]), term[0])

                except Exception as e:
                    print(e)
                    print('problem with the following key {}'.format(term[0]))
                # print("--- %s seconds documents in---" % (time.time() - start_time))


            try:
                max_tf = document_dictionary[max(document_dictionary, key=document_dictionary.get)]
                unique_num_value = len(document_dictionary)
                # TODO# unique_num = 0

                self.documents_info[document.tweet_id] = {'max_tf': max_tf, 'unique_num': unique_num_value,
                                                          'tweet_length': document.doc_length}
            except Exception as e:
                print(e)
                print('problem with {}'.format(document_dictionary))

        ############################ stemming ##############################################################
        document_dictionary = document.term_dict_with_stemming
        # Go over each term in the doc
        if len(document_dictionary)>0:
            for term in dict(document_dictionary):
                try:
                    self.entity_temp, document_dictionary, term = self.small_big_letters(self.entity_temp,
                                                                                         self.indexing_temp,
                                                                                         document_dictionary, term , True)
                    if term is None:
                        continue


                    first = False
                    if term not in self.posting_file_with_stemming:
                        self.posting_file_with_stemming[term] = []
                        first = True
                    if term[0] not in self.AB_dict_posting_with_stemming:
                        self.AB_dict_posting_with_stemming[term[0]] = {}

                    doc_pos_term = document.doc_pos.get(term.lower())
                    self.posting_file_with_stemming[term].append(
                        (document.tweet_id, document_dictionary[term], doc_pos_term))
                    if first:
                        self.AB_dict_posting_with_stemming[term[0]][term] = self.posting_file_with_stemming[term]

                    # rx2 = re.compile(fr"(?i)\b{term}\b")
                    # text0 = rx2.findall(document.full_text)
                    # if text0:
                    #     termInDoc = text0[0]

                    self.dict_dictionary_with_stemming[term] = (self.indexing_temp_with_stemming[term], len(self.AB_dict_posting_with_stemming[term[0]][term]), term[0])

                    # print("--- %s seconds dict out---" % (time.time() - start_time))



                except Exception as e:
                    print(e)
                    print('problem with the following key {}'.format(term[0]))

            # document.full_text_with_stemming = new_text
            if len(document_dictionary)>0:
                try:
                    max_tf = document_dictionary[max(document_dictionary, key=document_dictionary.get)]
                    unique_num_value = len(document_dictionary)
                    # TODO# unique_num = 0

                    self.documents_info_with_stemming[document.tweet_id] = {'max_tf': max_tf, 'unique_num': unique_num_value,
                                                              'tweet_length': document.doc_length}
                except Exception as e:
                    print(e)
                    print('problem with {}'.format(document_dictionary))


# '1280987673260425216' '1280976386019274762' '1280938379866226694' '1280946899038679043' '1280939220266356736'