import collections


class Indexer:

    def __init__(self, config):
        self.indexing_temp = {}
        self.entity_temp = {}
        self.posting_file = {}
        self.config = config
        self.documents_info = {}
        self.AB_dict_posting = {}
        self.dict_dictionary = {}

    def add_new_doc(self, document):
        """
        This function perform indexing process for a document object.
        Saved information is captures via two dictionaries ('inverted index' and 'posting')
        :param document: a document need to be indexed.
        :return: -
        """

        document_dictionary = document.term_doc_dictionary
        # Go over each term in the doc
        for term in dict(document_dictionary):
            try:
                #### for entities ######
                if term in dict(self.entity_temp):
                    if self.entity_temp[term] == 1:
                        del document.term_doc_dictionary[term]
                        del self.entity_temp[term]
                        continue

                ### for small/big capital letters ####
                if isinstance(term, str):
                    if term[0].isupper():
                        if term.lower() in self.indexing_temp:
                            term1 = term.lower()
                            if term1 not in self.indexing_temp:
                                self.indexing_temp[term1] = self.indexing_temp.pop(term)
                            document.term_doc_dictionary[term1] = document.term_doc_dictionary.pop(term)
                            term = term1

                        else:
                            term2 = term.upper()
                            if term2 not in self.indexing_temp:
                                self.indexing_temp[term2] = self.indexing_temp.pop(term)
                            document.term_doc_dictionary[term2] = document.term_doc_dictionary.pop(term)
                            term = term2

                if term not in self.posting_file:
                    self.posting_file[term] = []
                if term[0] not in self.AB_dict_posting:
                    self.AB_dict_posting[term[0]] = []

                doc_pos_term = document.doc_pos.get(term.lower())
                self.posting_file[term].append((term, document.tweet_id, document.term_doc_dictionary[term], doc_pos_term))
                self.AB_dict_posting[term[0]].append(self.posting_file[term])
                indices = self.findInList(term, self.AB_dict_posting[term[0]])
                if term not in self.dict_dictionary.keys():
                    self.dict_dictionary[term] = (self.indexing_temp[term], term[0], indices)



            except:
                print('problem with the following key {}'.format(term[0]))

        try:
            max_tf = document.term_doc_dictionary[max(document.term_doc_dictionary, key=document.term_doc_dictionary.get)]
            unique_num_value = len(set(document.full_text.split()))
            # unique_num = 0

            # for key, value in document_dictionary.items():
            #     if value == unique_num_value:
            #         unique_num = unique_num + 1

            self.documents_info[document.tweet_id] = {'max_tf': max_tf, 'unique_num': unique_num_value,
                                                      'tweet_length': document.doc_length}
        except:
            print('problem with {}'.format(document_dictionary))

    # def find_words(self, test_str, test_sub):
    #     res = [i for i in range(len(test_str)) if test_str.startswith(test_sub, i)]
    #     return res

    def findInList(self, val, lis):
        ind = [(j, i, k) for j, x in enumerate(lis) for i, y in enumerate(x) \
               for k, z in enumerate(y) if z == val]
        return ind[0][0] if ind else None
