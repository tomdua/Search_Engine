
class Indexer:

    def __init__(self, config):
        self.indexing_temp = {}
        self.indexing_temp_with_stemming = {}
        self.entity_temp = {}

        self.config = config
        self.documents_info = {}

        self.AB_dict_posting = {}
        self.AB_dict_posting_with_stemming = {}

        self.dict_dictionary = {}
        self.dict_dictionary_with_stemming = {}

    def small_big_letters(self, entity_in, indexing_temp_in, document_dictionary_in, term_in, stemm):
        try:
            if term_in in entity_in:
                if entity_in[term_in] == 1:
                    document_dictionary_in.pop(term_in)
                    entity_in.pop(term_in)
                    term_in = None
                    return term_in
                else:
                    return term_in

            if term_in[0].isupper() and not stemm:
                if term_in.lower() in indexing_temp_in:
                    term1 = term_in.lower()
                    if term1 in document_dictionary_in:
                        document_dictionary_in[term1] = document_dictionary_in[term1] + document_dictionary_in.pop(term_in)
                    if term1 not in document_dictionary_in:
                        document_dictionary_in[term1] = document_dictionary_in.pop(term_in)

                    if term_in in indexing_temp_in:
                        indexing_temp_in[term1] = indexing_temp_in[term1] + indexing_temp_in.pop(term_in)
                    term_in = term1

                else:
                    term2 = term_in.upper()
                    if term2 in document_dictionary_in:
                        document_dictionary_in[term2] = document_dictionary_in[term2] + document_dictionary_in.pop(term_in)
                    if term2 not in document_dictionary_in:
                        document_dictionary_in[term2] = document_dictionary_in.pop(term_in)

                    if term2 in indexing_temp_in and term_in in indexing_temp_in and term2!=term_in:
                        indexing_temp_in[term2] = indexing_temp_in[term2] + indexing_temp_in.pop(term_in)

                    if term2 not in indexing_temp_in and term_in in indexing_temp_in:
                        indexing_temp_in[term2] = indexing_temp_in.pop(term_in)
                    term_in = term2
                return term_in
            else:
                return term_in

        except Exception as e:
            print(e)

    def add_new_doc(self, document):
        """
        This function perform indexing process for a document object.
        Saved information is captures via two dictionaries ('inverted index' and 'posting')
        :param document: a document need to be indexed.
        :return: -
        """

        document_dictionary = document.term_doc_dictionary
        # Go over each term in the doc
        if len(document_dictionary) > 0:

            max_tf = document_dictionary[max(document_dictionary, key=document_dictionary.get)]
            for term in dict(document_dictionary):
                try:
                    if term in self.indexing_temp:
                        tf = document_dictionary[term]
                        term = self.small_big_letters(self.entity_temp, self.indexing_temp, document_dictionary, term,False)
                        if term is None:
                            continue

                        if term[0] not in self.AB_dict_posting:
                            self.AB_dict_posting[term[0]] = {}
                        if term not in self.AB_dict_posting[term[0]]:
                            self.AB_dict_posting[term[0]][term] = {}
                        if document.tweet_id not in self.AB_dict_posting[term[0]][term]:
                            self.AB_dict_posting[term[0]][term][document.tweet_id] = ((tf, tf / max_tf))


                        self.dict_dictionary[term]=(self.indexing_temp[term],len(self.AB_dict_posting[term[0]][term]), term[0])

                except Exception as e:
                    print(e)
                    print('problem with the following key {}'.format(term[0]))

            if len(document_dictionary) > 0:
                try:
                    unique_num_value = len(document_dictionary)

                    self.documents_info[document.tweet_id] = {'max_tf': max_tf, 'unique_num': unique_num_value,
                                                              'tweet_length': document.doc_length}
                except Exception as e:
                    print(e)
                    print('problem with {}'.format(document_dictionary))

        ############################ stemming ##############################################################
        document_dictionary = document.term_dict_with_stemming
        # Go over each term in the doc
        if len(document_dictionary) > 0:

            max_tf = document_dictionary[max(document_dictionary, key=document_dictionary.get)]

            for term in dict(document_dictionary):
                try:
                    if term in self.indexing_temp_with_stemming:
                        tf = document_dictionary[term]

                        if term[0] not in self.AB_dict_posting_with_stemming:
                            self.AB_dict_posting_with_stemming[term[0]] = {}
                        if term not in self.AB_dict_posting_with_stemming[term[0]]:
                            self.AB_dict_posting_with_stemming[term[0]][term] = {}
                        if document.tweet_id not in self.AB_dict_posting_with_stemming[term[0]][term]:
                            self.AB_dict_posting_with_stemming[term[0]][term][document.tweet_id] = ((tf, tf / max_tf))

                        self.dict_dictionary_with_stemming[term] = (self.indexing_temp_with_stemming[term], len(self.AB_dict_posting_with_stemming[term[0]][term]),term[0])


                except Exception as e:
                    print(e)
                    print('problem with the following key {}'.format(term[0]))


