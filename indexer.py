from statistics import mode
import collections

import utils


class Indexer:

    def __init__(self, config):
        self.inverted_idx = {}
        self.parse = None
        self.posting_file = {}
        self.config = config
        self.documents_info = {}

    def add_new_doc(self, document):
        """
        This function perform indexing process for a document object.
        Saved information is captures via two dictionaries ('inverted index' and 'posting')
        :param document: a document need to be indexed.
        :return: -
        """

        document_dictionary = document.term_doc_dictionary
        # Go over each term in the doc
        for term in document_dictionary.copy():
            try:
                first= False
                if term in self.parse.entity_temp :
                    if self.parse.entity_temp[term] == 1 :
                        del document.term_doc_dictionary[term]
                        continue
                # Update inverted index and posting
                if term not in self.inverted_idx.keys():
                    self.inverted_idx[term] = 1
                    first = True
                    self.posting_file[term] = []
                    # self.inverted_idx_temp[term] = []
                if not first:
                    self.inverted_idx[term] += 1
                ### for small/big capital letters ####
                if isinstance(term, str):
                    if term[0].isupper():
                        if term.lower() in self.inverted_idx:
                            term1 = term.lower()
                            self.inverted_idx[term1] = self.inverted_idx.pop(term)
                            self.posting_file[term1] = self.posting_file.pop(term)
                            document.term_doc_dictionary[term1] = document.term_doc_dictionary.pop(term)
                            term = term1
                            # del document.term_doc_dictionary[term]
                        # elif term.isupper():
                        #     continue
                        else:
                            term2 = term.upper()
                            self.inverted_idx[term2] = self.inverted_idx.pop(term)
                            self.posting_file[term2] = self.posting_file.pop(term)
                            document.term_doc_dictionary[term2] = document.term_doc_dictionary.pop(term)
                            term = term2


                            # document.term_doc_dictionary[term2] = document.term_doc_dictionary.pop(term)
                            # del document.term_doc_dictionary[term]
                doc_pos_term=document.doc_pos.get(term.lower())
                self.posting_file[term].append((term, document.tweet_id, document_dictionary[term],doc_pos_term))
            except:
                print('problem with the following key {}'.format(term[0]))

        max_tf = document_dictionary[max(document_dictionary, key=document_dictionary.get)]
        unique_num_value = collections.Counter(document_dictionary.values()).most_common()[-1][0]
        unique_num = 0
        for key, value in document_dictionary.items():
            if value == unique_num_value:
                unique_num = unique_num + 1

        self.documents_info[document.tweet_id] = {'max_tf': max_tf, 'unique_instances': unique_num,
                                                  'tweet_length': document.doc_length}
