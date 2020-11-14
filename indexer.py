from statistics import mode
import collections

import utils


class Indexer:

    def __init__(self, config):
        self.inverted_idx = {}
        self.posting_file = {}
        self.config = config
        self.document_info = {}

    def add_new_doc(self, document):
        """
        This function perform indexing process for a document object.
        Saved information is captures via two dictionaries ('inverted index' and 'posting')
        :param document: a document need to be indexed.
        :return: -
        """

        document_dictionary = document.term_doc_dictionary
        # Go over each term in the doc
        # self.document_info[tw]
        for term in document_dictionary.keys():
            try:
                # Update inverted index and posting
                if term not in self.inverted_idx.keys():
                    self.inverted_idx[term] = 1
                    self.posting_file[term] = []
                    if document_dictionary[term] >= 2:
                        index_in_twitter = self.find_words(document.full_text, term)
                    else:
                        index_in_twitter = document.full_text.find(term)
                else:
                    self.inverted_idx[term] += 1
                    if document_dictionary[term] >= 2:
                        index_in_twitter = self.find_words(document.full_text, term)
                    else:
                        index_in_twitter = document.full_text.find(term)


                self.posting_file[term].append((term, document.tweet_id, document_dictionary[term],index_in_twitter))

            except:
                print('problem with the following key {}'.format(term[0]))

        max_tf = document_dictionary[max(document_dictionary, key=document_dictionary.get)]
        unique_num_value = collections.Counter(document_dictionary.values()).most_common()[-1][0]
        unique_num = 0
        for key, value in document_dictionary.items():
            if value == unique_num_value:
                unique_num = unique_num + 1

        self.document_info[document.tweet_id] = {'max_tf': max_tf, 'unique_num': unique_num,
                                                 'tweet_length': document.doc_length}

    def find_words(self, test_str, test_sub):
        res = [i for i in range(len(test_str)) if test_str.startswith(test_sub, i)]
        return res