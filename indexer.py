class Indexer:

    def __init__(self, config):
        self.dictionaryTerms = {}
        self.postingTerms = {}
        self.config = config

    def add_new_doc(self, document):
        """
        This function perform indexing process for a document object.
        Saved information is captures via two dictionaries ('inverted index' and 'posting')
        :param document: a document need to be indexed.
        :return: -
        """

        document_dictionary = document.term_doc_dictionary
        # Go over each term in the doc
        for term in document_dictionary.keys():
            try:
                # Update inverted index and posting
                if term not in self.dictionaryTerms.keys():
                    self.dictionaryTerms[term] = 1
                    self.postingTerms[term] = []
                else:
                    self.dictionaryTerms[term] += 1

                self.postingTerms[term].append((document.tweet_id, document_dictionary[term]))

            except:
                print('problem with the following key {}'.format(term[0]))
