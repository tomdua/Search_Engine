import os
import re
from reader import ReadFile
from configuration import ConfigClass
from parser_module import Parse
from stemmer import Stemmer
from indexer import Indexer
from searcher import Searcher
import utils
import time
import pandas as pd
import pickle

def run_engine(corpus_path,output_path):
    """
    :return:
    """
    # os.mkdir('./'+output_path)
    config = ConfigClass()
    r = ReadFile(corpus_path=config.get__corpusPath())
    p = Parse()
    stemming = Stemmer()
    indexer = Indexer(config)
    documents_list = r.read_file(corpus_path)

    documents_dict_after_parse = {}
    p.stemming = stemming
    # documents_list=parquets_files
    for idx, document in enumerate(documents_list,1):
        # parse the document
        parsed_document = p.parse_doc(document)
        if parsed_document:
            documents_dict_after_parse[parsed_document.tweet_id] = parsed_document
        document = []

        if idx % 500000 == 0 or len(documents_list) == idx:

            utils.save_obj(documents_dict_after_parse, output_path+'/documents_dict_after_parse')
            documents_dict_after_parse = {}

    documents_list=[]
    # print("--- parse end in %s seconds---" % (time.time() - start_time))
    indexer.indexing_temp= dict(filter(lambda elem: elem[1] != 1,p.inverted_idx.items()))
    p.inverted_idx = {}
    indexer.indexing_temp_with_stemming = dict(filter(lambda elem: elem[1] != 1, p.inverted_idx_stemming.items()))
    p.inverted_idx_stemming = {}
    indexer.entity_temp=p.entity_temp
    p.entity_temp = {}
    p = None

    obj_number = {}
    documents_after_index = {}

    try:
        # path0 = './'+output_path
        path1 = './'+output_path+'/uppers'
        path2 = './'+output_path+'/lowers'
        path3 = './'+output_path+'/others'
        path4 = './'+output_path+'/stemming'
        path5 = './'+output_path+'/stemming/uppers'
        path6 = './'+output_path+'/stemming/lowers'
        path7 = './'+output_path+'/stemming/others'
        path8 = './'+output_path+'/document_after_index'
        # os.mkdir(path0)
        os.mkdir(path1)
        os.mkdir(path2)
        os.mkdir(path3)
        os.mkdir(path4)
        os.mkdir(path5)
        os.mkdir(path6)
        os.mkdir(path7)
        os.mkdir(path8)
    except OSError as error:
        print(error)
    # print("--- %s seconds index start---" % (time.time() - start_time))
    with open('./'+output_path+'/documents_dict_after_parse.pkl', 'rb') as f:
        while 1:
            try:
                documents_dict = pickle.load(f)
                for idx, document in enumerate(documents_dict,1):
                    indexer.add_new_doc(documents_dict[document])
                    documents_after_index[documents_dict[document].tweet_id] = (list(documents_dict[document].term_doc_dictionary.keys()),list(documents_dict[document].term_dict_with_stemming.keys()))
                    id = documents_dict[document].tweet_id
                    number_index = id[len(id) - 4:]
                    if number_index in obj_number:
                        obj_number[number_index].update(documents_after_index)
                    else:
                        obj_number[number_index] = {}
                        obj_number[number_index] = documents_after_index
                    documents_after_index = {}
                    documents_dict[document] = {}

                    if idx % 500000 == 0 or idx==len(documents_dict):
                        count = 0
                        for letter in indexer.AB_dict_posting:
                            try:
                                string = 'posting_file_' + letter
                                if letter.isupper():
                                    string = output_path+'/uppers/posting_file_' + letter
                                elif letter.islower():
                                    string = output_path+'/lowers/posting_file_' + letter
                                else:
                                    string = output_path+'/others/posting_file_' + letter

                                utils.save_obj(indexer.AB_dict_posting[letter], string)
                            except:
                                string = output_path+'/posting_file_A' + str(count)  # TODO
                                utils.save_obj(indexer.AB_dict_posting[letter], string)
                                count += 1

                        indexer.AB_dict_posting = {}

                        count = 0
                        for letter in indexer.AB_dict_posting_with_stemming:
                            try:
                                string = 'posting_file_' + letter
                                if letter.isupper():
                                    string = output_path+'/stemming/uppers/posting_file_' + letter
                                elif letter.islower():
                                    string = output_path+'/stemming/lowers/posting_file_' + letter
                                else:
                                    string = output_path+'/stemming/others/posting_file_' + letter
                                utils.save_obj(indexer.AB_dict_posting_with_stemming[letter], string)
                            except:

                                string = output_path+'/stemming/posting_file_A' + str(count)  # TODO
                                utils.save_obj(indexer.AB_dict_posting_with_stemming[letter], string)
                                count += 1

                        indexer.AB_dict_posting_with_stemming = {}

                        for id, value in obj_number.items():
                            utils.save_obj(value, output_path+"/document_after_index/documents_after_index_{}".format(id))
                        obj_number = {}

                        utils.save_obj(indexer.documents_info, output_path+"/documents_info_after_index")
                        indexer.documents_info={}

            except EOFError:
                # print("--- %s seconds index end ---" % (time.time() - start_time))
                utils.save_obj(indexer.dict_dictionary,output_path+'/dict_dictionary_after_indexer')
                indexer.dict_dictionary={}
                utils.save_obj(indexer.dict_dictionary_with_stemming,output_path+'/dict_dictionary_with_stemming_after_indexer')
                indexer.dict_dictionary_with_stemming={}
                utils.save_obj(indexer.entity_temp,output_path+'/entity_temp_after_indexer')
                indexer.entity_temp={}
                indexer=None
                return



def load_index(output_path):


    dictionary = utils.load_obj(output_path+'/dict_dictionary_after_indexer')
    dictionary_with_stemming = utils.load_obj(output_path+'/dict_dictionary_with_stemming_after_indexer')
    entity_dict = utils.load_obj(output_path+'/entity_temp_after_indexer')

    return dictionary[0],dictionary_with_stemming[0],entity_dict[0]


def search_and_rank_query(searcher,query, k, stemming_bool,dictionary,dictionary_with_stemming,entity_dict):

    stemming = Stemmer()
    p = Parse()
    stopwords=p.stop_words
    config = ConfigClass()
    indxer = Indexer(config)
    p.stemming = stemming
    pattern = re.compile(r'\b(' + r'|'.join(stopwords) + r')\b\s*', re.IGNORECASE)
    query = pattern.sub('', query)
    query_as_list = p.parse_sentence(query, False, stemming_bool)
    query_as_dict = {}
    for w in query_as_list:
        if w in query_as_dict:
            query_as_dict[w] += 1
        else:
            query_as_dict[w] = 1
    if stemming_bool:
        dict_dictionary_to_send = dictionary_with_stemming
        # searcher = Searcher(dict_dictionary_to_send)
    else:
        dict_dictionary_to_send = dictionary
        for term in query_as_list:
            term = indxer.small_big_letters(entity_dict, dict_dictionary_to_send, query_as_dict, term,stemming_bool)
        # searcher = Searcher(dict_dictionary_to_send)


    relevant_docs, model, query_vec = searcher.relevant_docs_from_posting(query_as_dict, stemming_bool)
    dictionary_with_stemming={}
    dict_dictionary_to_send={}
    dictionary={}
    entity={}
    entity_dict={}

    ranked_docs = searcher.ranker.rank_relevant_doc(relevant_docs, model, query_vec, stemming_bool)
    return searcher.ranker.retrieve_top_k(ranked_docs, k)



def main(corpus_path="testData", output_path="posting", stemming=True, queries='', num_docs_to_retrieve=10):    #
    run_engine(corpus_path,output_path)
    dictionary, dictionary_with_stemming, entity_dict = load_index(output_path)
    # query = input("Please enter a query: ")
    # stem_from_user = input("You want to use stemming(y/n): ")
    # if stem_from_user == 'y':
    #     stemming = True
    # else:
    #     stemming = False
    # k = int(input("Please enter number of docs_after_parse to retrieve: "))
    searcher = Searcher()
    searcher.inverted_index=dictionary
    for query in queries:
        results = search_and_rank_query(searcher,query, num_docs_to_retrieve, stemming,dictionary,dictionary_with_stemming,entity_dict)
        for doc_tuple in results:
            print('Tweet id: {}, Score: {}'.format(doc_tuple[0], doc_tuple[1]))
