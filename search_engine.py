import json

from numpy import asarray

import indexer
from reader import ReadFile
from configuration import ConfigClass
from parser_module import Parse
from stemmer import Stemmer
from indexer import Indexer
from searcher import Searcher
import utils
from collections import Counter
import time


def findInList(val, lis):
    ind = [(j, i, k) for j, x in enumerate(lis) for i, y in enumerate(x) \
           for k, z in enumerate(y) if z == val]
    return ind[0][0] if ind else None


def run_engine():
    """
    :return:
    """
    # inverted_idx={}
    # with open('inverted_idx.txt', 'r') as sample:
    #     for line in sample:
    #         inverted_idx.update(json.loads(line))
    #
    # posting_file = {}
    # with open('posting_file.txt', 'r') as sample:
    #     for line in sample:
    #         posting_file.update(json.loads(line))
    #
    # documents_info = {}
    # with open('documents_info.txt', 'r') as sample:
    #     for line in sample:
    #         documents_info.update(json.loads(line))
    config = ConfigClass()
    start_time = time.time()

    r = ReadFile(corpus_path=config.get__corpusPath())
    p = Parse()
    stemming = Stemmer()
    indexer = Indexer(config)
    documents_list = r.read_file("asd")
    documents_num = len(documents_list)

    documents_list_after_parse = []
    append = documents_list_after_parse.append
    number_of_documents = 0
    # usingStemming = input("You will want to use stemming?(yes/no): ")
    # if usingStemming == 'yes':
    #     p.stemming = stemming
    # import time
    # indexer.parse = p
    # documents_list = utils.load_obj("documents_list")
    # Iterate over every document in the file
    # count = 1
    # while documents_list:

    for idx, document in enumerate(documents_list, 1):
        if idx == 1:
            print("--- %s seconds parser start---" % (time.time() - start_time))
        # parse the document
        # document = documents_list.pop(0)
        parsed_document = p.parse_doc(document)
        append(parsed_document)
        print(idx)
        if idx % 50000 == 0 or idx == documents_num:
            print("to mem")
            # with open('inverted_idx_temp.txt', 'a') as file:
            #     file.write(json.dumps(p.inverted_idx))
            #     file.write('\n')
            # with open('entity_temp.txt', 'a') as file:
            #     file.write(json.dumps(p.entity_temp))
            #     file.write('\n')
            utils.save_obj(p.inverted_idx, "inverted_idx_afterParser")
            utils.save_obj(p.entity_temp, "entity_temp")
            p.entity_temp = {}
            p.inverted_id = {}

        if idx == documents_num:
            # p.entity_temp = {}
            # p.inverted_id = {}
            documents_list = []
            print("--- %s seconds parser end---" % (time.time() - start_time))

        # count += 1
        # documents_list.remove(document)

    for idx, document in enumerate(documents_list_after_parse, 1):

        if idx == 1:
            #indexing = utils.load_obj("inverted_idx_afterParser")
            # inverted_idx={}
            # with open('inverted_idx_temp.txt', 'r') as sample:
            #     for line in sample:
            #         indexer.indexing_temp.update(json.loads(line))
            entity_to_index = Counter()
            entityList = utils.load_obj("entity_temp")
            for entity in entityList:
                x = Counter(entity)
                entity_to_index = entity_to_index + x
                # entity_to_index.update(entity)
                # entityList.remove(entity)
            for k in list(entity_to_index):
                if entity_to_index[k] == 1:
                    del entity_to_index[k]
            indexer.entity_temp = entity_to_index
            entityList = []
            entity_to_index={}


            indexingList = utils.load_obj("inverted_idx_afterParser")
            indexing_to_index=Counter()
            for index in indexingList:
                x = Counter(index)
                indexing_to_index = indexing_to_index + x
                # indexingList.remove(index)
            indexer.indexing_temp=indexing_to_index
            indexingList = []
            indexing_to_index={}

            # with open('entity_temp.txt', 'r') as sample:
            #     for line in sample:
            #         indexer.entity_temp.update(json.loads(line))
            # indexer.entity_temp = entity_temp
            print("--- %s seconds index start---" % (time.time() - start_time))

        indexer.add_new_doc(document)
        # print(idx)
        # print("--- %s seconds in---" % (time.time() - start_time))
        print(idx)

        if idx % 50000 == 0 or idx == documents_num:
            # print("--- %s seconds out---" % (time.time() - start_time))

            # print('Finished parsing and indexing 1000 documents. Starting to export files')
            # print('Finished parsing and indexing. Starting to export files')
            #
            utils.save_obj(indexer.AB_dict_posting, "posting_file")
            indexer.AB_dict_posting = {}

            utils.save_obj(indexer.dict_dictionary, "inverted_idx")
            indexer.dict_dictionary = {}

            utils.save_obj(indexer.documents_info, "documents_info")
            indexer.documents_info = {}

            #
            print("to mem")
            # with open('inverted_idx.txt', 'a') as file:
            #     file.write(json.dumps(indexer.dict_dictionary))
            #     file.write('\n')
            # indexer.dict_dictionary={}
            # with open('posting_file.txt', 'a') as file:
            #     file.write(json.dumps(indexer.AB_dict_posting))
            #     file.write('\n')
            # indexer.AB_dict_posting={}
            # with open('documents_info.txt', 'a') as file:
            #     file.write(json.dumps(indexer.documents_info))
            #     file.write('\n')
            # indexer.documents_info={}
        # documents_list_after_parse.remove(document)


    indexer.indexing_temp={}
    indexer.entity_temp={}
    print("--- %s seconds index end ---" % (time.time() - start_time))
    test3=1


def load_index():
    print('Load inverted index')
    inverted_idx = {}
    with open('inverted_idx.txt', 'r') as sample:
        for line in sample:
            inverted_idx.update(json.loads(line))
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
    # query = input("Please enter a query: ")
    # k = int(input("Please enter number of docs to retrieve: "))
    # inverted_index = load_index()
    # # print(inverted_index)
    # for doc_tuple in search_and_rank_query(query, inverted_index, k):
    #     print('tweet id: {}, score (unique common words with query): {}'.format(doc_tuple[0], doc_tuple[1]))
