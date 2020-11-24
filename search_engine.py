import json
import os

from numpy import asarray

from reader import ReadFile
from configuration import ConfigClass
from parser_module import Parse
from stemmer import Stemmer
from indexer import Indexer
from searcher import Searcher
import utils
import time
import psutil  # TODO
import glob
import itertools

def run_engine():
    """
    :return:
    """

    mem = psutil.virtual_memory()
    mem1 = mem.total * 0.9

    # with open('file.json') as json_file:
    #
    #     # read json file line by line
    #     for line in json_file.readlines():
    #
    #         # create python dict from json object
    #         json_dict = json.loads(line)
    #         for key in json_dict:
    #             print(key)



    # files_list_stemming = []
    # files_stemming = glob.glob('./pickles/stemming/**/*.pkl')
    # for f in files_stemming:
    #     f = f.replace('./pickles/', '')
    #     f = f.replace('.pkl', '')
    #     to_arr = utils.load_obj(f)
    #     files_list_stemming.append(to_arr[0])
    # files_stemming = []
    #
    #
    # files_list=[]
    # files = glob.glob('./pickles/**/*.pkl')
    # for f in files:
    #     f=f.replace('./pickles\\', '')
    #     f=f.replace('.pkl', '')
    #     to_arr = utils.load_obj(f)
    #     files_list.append(to_arr[0])
    # files=[]

    config = ConfigClass()
    r = ReadFile(corpus_path=config.get__corpusPath())
    p = Parse()
    stemming = Stemmer()
    indexer = Indexer(config)
    start_time = time.time()

    documents_list = r.read_file("asd")
    documents_num = len(documents_list)
    print("--- %s seconds parser readStop---" % (time.time() - start_time))

    documents_dict_after_parse = {}
    p.stemming = stemming
    once = True
    # Iterate over every document in the file
    for idx, document in enumerate(documents_list, 1):

        if idx == 1:
            print("--- %s seconds parser start---" % (time.time() - start_time))
        # parse the document
        parsed_document = p.parse_doc(document)
        documents_dict_after_parse[parsed_document.tweet_id]=parsed_document


        if mem.used >= mem1:

            print('the idx is', idx)

        if idx == documents_num:
            documents_list = []
            print("--- %s seconds parser end---" % (time.time() - start_time))

    for idx, document in enumerate(documents_dict_after_parse, 1):

        if idx == 1:
            indexer.entity_temp = p.entity_temp
            p.entity_temp = {}
            indexer.indexing_temp_with_stemming = p.inverted_idx_stemming
            p.inverted_idx_stemming = {}
            indexer.indexing_temp = p.inverted_idx
            p.inverted_idx = {}
            print("--- %s seconds index start---" % (time.time() - start_time))

        indexer.add_new_doc(documents_dict_after_parse[document])
        obj = {}
        obj[documents_dict_after_parse[document].tweet_id] = (documents_dict_after_parse[document].term_doc_dictionary,documents_dict_after_parse[document].term_dict_with_stemming)
        with open('file.json', 'a') as outfile:
            outfile.write(json.dumps(obj))
            outfile.write('\n')
            outfile.close()


        if mem.used >= mem1:
            print('the idx is {}', idx)

        #
        if idx == documents_num:


            if once:
                try:
                    path1 = './pickles/uppers'
                    path2 = './pickles/lowers'
                    path3 = './pickles/others'
                    path4 = './pickles/stemming'
                    path5 = './pickles/stemming/uppers'
                    path6 = './pickles/stemming/lowers'
                    path7 = './pickles/stemming/others'
                    os.mkdir(path1)
                    os.mkdir(path2)
                    os.mkdir(path3)
                    os.mkdir(path4)
                    os.mkdir(path5)
                    os.mkdir(path6)
                    os.mkdir(path7)
                    once = False
                except OSError as error:
                    print(error)

            count = 0
            for letter in indexer.AB_dict_posting:
                try:
                    string = 'posting_file_' + letter
                    if letter.isupper():
                        string = '/uppers/posting_file_' + letter
                    elif letter.islower():
                        string = '/lowers/posting_file_' + letter
                    else:
                        string = '/others/posting_file_' + letter

                    utils.save_obj(indexer.AB_dict_posting[letter], string)
                except:

                    string = 'posting_file_A' + str(count)  # TODO
                    utils.save_obj(indexer.AB_dict_posting[letter], string)
                    count += 1


            indexer.posting_file = {}
            indexer.AB_dict_posting = {}
            # utils.save_obj(documents_dict_after_parse, "documents_after_parse")
            utils.save_obj(indexer.entity_temp, "entity_temp")
            utils.save_obj(indexer.dict_dictionary, "dict_dictionary")
            utils.save_obj(indexer.dict_dictionary_with_stemming, "dict_dictionary_with_stemming")
            utils.save_obj(indexer.documents_info, "documents_info")

            count = 0
            for letter in indexer.AB_dict_posting_with_stemming:
                try:
                    string = 'posting_file_' + letter
                    if letter.isupper():
                        string = 'stemming/uppers/posting_file_' + letter
                    elif letter.islower():
                        string = 'stemming/lowers/posting_file_' + letter
                    else:
                        string = 'stemming/others/posting_file_' + letter
                    utils.save_obj(indexer.AB_dict_posting_with_stemming[letter], string)
                except:

                    string = 'stemming/posting_file_A' + str(count)  # TODO
                    utils.save_obj(indexer.AB_dict_posting_with_stemming[letter], string)
                    count += 1

            indexer.posting_file_with_stemming = {}
            indexer.AB_dict_posting_with_stemming= {}

    documents_dict_after_parse = {}
    indexer.indexing_temp = {}
    indexer.indexing_temp_with_stemming = {}
    indexer.entity_temp = {}
    indexer.dict_dictionary_with_stemming ={}

    print("--- %s seconds index end ---" % (time.time() - start_time))
    test3 = 1

    # return p.entity_temp, indexer.dict_dictionary , indexer.dict_dictionary_with_stemming , indexer.documents_info


def load_index():
    print('Load inverted index')
    inverted_idx = {}
    # with open('inverted_idx.txt', 'r') as sample:
    #     for line in sample:
    #         inverted_idx.update(json.loads(line))
    return inverted_idx


def search_and_rank_query(query,dict_dictionary , dict_dictionary_with_stemming,documents_info, k,stemming_bool,entity):
    stemming = Stemmer()
    p = Parse()
    config = ConfigClass()
    indxer = Indexer(config)
    p.stemming = stemming
    query_as_list = p.parse_sentence(query, False,stemming_bool)
    query_as_dict = {}
    for w in query_as_list:
        if w in query_as_dict:
            query_as_dict[w] += 1
        else:
            query_as_dict[w] = 1
    if stemming_bool:
        dict_dictionary_to_send = dict_dictionary_with_stemming
        for term in query_as_list:
            entity, query_as_dict, term = indxer.small_big_letters(entity, dict_dictionary_to_send, query_as_dict, term , stemming_bool)
        searcher = Searcher(dict_dictionary_to_send)
    else:
        dict_dictionary_to_send= dict_dictionary
        for term in query_as_list:
            entity, query_as_dict, term = indxer.small_big_letters(entity, dict_dictionary_to_send, query_as_dict, term, stemming_bool)
        searcher = Searcher(dict_dictionary_to_send)

    # searcher = Searcher(inverted_index)
    relevant_docs = searcher.relevant_docs_from_posting(query_as_dict)
    # searcher.ranker.documents=docs_after_parse
    ranked_docs = searcher.ranker.rank_relevant_doc(relevant_docs,dict_dictionary_to_send, documents_info , stemming_bool)
    return searcher.ranker.retrieve_top_k(ranked_docs, k)


def main():
    run_engine()
    # docs_after_parse = utils.load_obj("documents_after_parse")
    dict_dictionary = utils.load_obj("dict_dictionary")
    dict_dictionary_with_stemming = utils.load_obj("dict_dictionary_with_stemming")
    documents_info = utils.load_obj("documents_info")
    entity = utils.load_obj("entity_temp")

    query = input("Please enter a query: ")
    stem_from_user = input("You want to use stemming(y/n): ")
    if stem_from_user=='y':
        stemming = True
    else:
        stemming = False
    k = int(input("Please enter number of docs_after_parse to retrieve: "))
    # inverted_index = load_index()
    # print(inverted_index)
    for doc_tuple in search_and_rank_query(query, dict_dictionary , dict_dictionary_with_stemming,documents_info, k,stemming,entity):
        print('tweet id: {}, score (unique common words with query): {}'.format(doc_tuple[0], doc_tuple[1]))
