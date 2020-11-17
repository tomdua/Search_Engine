import json

from numpy import asarray

from reader import ReadFile
from configuration import ConfigClass
from parser_module import Parse
from stemmer import Stemmer
from indexer import Indexer
from searcher import Searcher
import utils
import time


def findInList(val, lis):
    ind = [(j, i, k) for j, x in enumerate(lis) for i, y in enumerate(x) \
           for k, z in enumerate(y) if z == val]
    return ind[0][0] if ind else None


def run_engine():
    """
    :return:
    """

    # with open('inverted_idx.txt') as json_file:
    #     inverted_idx = json.load(json_file)
    # with open('posting_file.txt') as json_file:
    #     posting_file = json.load(json_file)
    # with open('documents_info.txt') as json_file:
    #     documents_info = json.load(json_file)


    config = ConfigClass()
    r = ReadFile(corpus_path=config.get__corpusPath())
    p = Parse()
    stemming = Stemmer()
    indexer = Indexer(config)
    documents_list = r.read_file()
    number_of_documents = 0
    # usingStemming = input("You will want to use stemming?(yes/no): ")
    # if usingStemming == 'yes':
    #     p.stemming = stemming
    # import time
    start_time = time.time()
    # x=len(documents_list)
    # print("--- %s seconds ---" % start_time)
    # Iterate over every document in the file
    for idx, document in enumerate(documents_list, 1):
        # parse the document
        parsed_document = p.parse_doc(document)
        #number_of_documents += 1

        ####################### index the parses document data ##################################
        indexer.parse = p
         # to parse 1000 doc

        indexer.add_new_doc(parsed_document)
        print(idx)
        print("--- %s seconds in---" % (time.time() - start_time))

        if idx % 20000 == 0 or idx == len(documents_list):
            print("--- %s seconds out---" % (time.time() - start_time))

            # print('Finished parsing and indexing 1000 documents. Starting to export files')
            # print('Finished parsing and indexing. Starting to export files')
            # AB_dict_posting = {}
            # dict_dictionary = {}
            #
            # for term in indexer.inverted_idx.keys():
            #     if term not in dict_dictionary.keys():
            #         dict_dictionary[term] = []
            #     try:
            #         # Update inverted index and posting
            #         if term[0] not in AB_dict_posting.keys():
            #             AB_dict_posting[term[0]] = []
            #
            #         AB_dict_posting[term[0]].append(indexer.posting_file[term])
            #         indices = findInList(term, AB_dict_posting[term[0]])
            #         dict_dictionary[term] = (indexer.inverted_idx[term], term[0], indices)
            #         # test=1
            #     except:
            #         print("wrong")

            # f = open("dict.txt", "w")
            # f.write(str(dict_dictionary))
            # f.close()
            with open('inverted_idx1.txt', 'w') as file:
                file.write(json.dumps(indexer.dict_dictionary))
            with open('posting_file1.txt', 'w') as file:
                file.write(json.dumps(indexer.AB_dict_posting))
            with open('documents_info.txt1', 'w') as file:
                file.write(json.dumps(indexer.documents_info))
            # utils.save_obj(dict_dictionary, "inverted_idx")
            # utils.save_obj(AB_dict_posting, "posting_file")

    # my_data_file = open('file.txt', 'r')
    # with open('documents_info.txt1', 'w') as file:
    #     file.write(json.dumps(indexer.documents_info))
    # utils.save_obj(indexer.documents_info, "documents_info")
    print("--- %s seconds ---" % (time.time() - start_time))
    test3 = 1


def load_index():
    print('Load inverted index')
    with open('inverted_idx.txt') as json_file:
        inverted_idx = json.load(json_file)
    return inverted_idx


def search_and_rank_query(query, inverted_index, k):
    p = Parse()
    query_as_list = p.parse_sentence(query)
    searcher = Searcher(inverted_index)
    relevant_docs = searcher.relevant_docs_from_posting(query_as_list)
    ranked_docs = searcher.ranker.rank_relevant_doc(relevant_docs)
    return searcher.ranker.retrieve_top_k(ranked_docs, k)


def main():
    run_engine()
    query = input("Please enter a query: ")
    k = int(input("Please enter number of docs to retrieve: "))
    inverted_index = load_index()
    # print(inverted_index)
    for doc_tuple in search_and_rank_query(query, inverted_index, k):
        print('tweet id: {}, score (unique common words with query): {}'.format(doc_tuple[0], doc_tuple[1]))
