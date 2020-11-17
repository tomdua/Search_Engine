import json

from parser_module import Parse
from ranker import Ranker
import utils


class Searcher:

    def __init__(self, inverted_index):
        """
        :param inverted_index: dictionary of inverted index
        """
        self.parser = Parse()
        self.ranker = Ranker()
        self.inverted_index = inverted_index

    def relevant_docs_from_posting(self, query):
        """
        This function loads the posting list and count the amount of relevant documents per term.
        :param query: query
        :return: dictionary of relevant documents.
        """
        with open('posting_file.txt') as json_file:
            posting_file = json.load(json_file)
        relevant_docs = {}
        for term in query:
            try: # an example of checks that you have to do
                if term in self.inverted_index.keys():
                    indexes_in_posting=[self.inverted_index[term][1],self.inverted_index[term][2]]
                    #list_in_posting = posting_file[indexes_in_posting[0],indexes_in_posting[1]]
                    x = indexes_in_posting[0]
                    y = indexes_in_posting[1]
                    #test= posting_file['s'][135]
                    list_in_posting = posting_file[x][y]
                    for item in list_in_posting:
                        if item[1] not in relevant_docs.keys():
                            relevant_docs[item[1]] = 1
                        else:
                            relevant_docs[item[1]] += 1
            except:
                print('term {} not found in posting'.format(term))
        return relevant_docs
