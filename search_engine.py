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
import psutil#TODO
import glob



def run_engine():
    """
    :return:
    """

    mem =  psutil.virtual_memory()
    mem1 = mem.total * 0.9
    #
    # files_list=[]
    # files = glob.glob('./pickles/*.pkl')
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
    # utils.save_obj(documents_list, "documents_list")
    print("--- %s seconds parser readStop---" % (time.time() - start_time))

    documents_list_after_parse = []
    append = documents_list_after_parse.append

    # usingStemming = input("You will want to use stemming?(yes/no): ")
    # if usingStemming == 'yes':
    #     p.stemming = stemming


    # Iterate over every document in the file
    for idx, document in enumerate(documents_list, 1):

        if idx == 1:
            print("--- %s seconds parser start---" % (time.time() - start_time))
        # parse the document
        parsed_document = p.parse_doc(document)
        append(parsed_document)

        # print(idx)

        if mem.used>=mem1:
            print('the idx is',idx)

        if idx == documents_num:

            documents_list = []
            print("--- %s seconds parser end---" % (time.time() - start_time))



    for idx, document in enumerate(documents_list_after_parse, 1):

        if idx == 1:


            indexer.entity_temp = p.entity_temp
            p.entity_temp = {}

            # indexing_to_index= dealing_with_upper_lower(p.inverted_idx)
            # indexing_to_index = Counter()
            # indexingList = utils.load_obj("inverted_idx_afterParser")
            # for index in documents_list_after_parse:
            #     x = Counter(index.term_doc_dictionary)
            #     indexing_to_index = indexing_to_index + x
            # indexingList.remove(index)

            #




            indexer.indexing_temp = p.inverted_idx
            p.inverted_idx = {}


            print("--- %s seconds index start---" % (time.time() - start_time))
        if document.term_doc_dictionary:
            indexer.add_new_doc(document)

        if mem.used>=mem1:
            print('the idx is {}',idx)

        #
        if idx == documents_num:

            # for letter in indexer.AB_dict_posting:
            #     with open('AB_dict_posting_{}.txt',letter, 'a') as file:
            #         file.write(json.dumps(letter))
            #         file.write('\n')
            # name = 'posting_file_' + str2
            # str1 = './pickles/' + name + '.pkl'


            count=0
            for letter in indexer.AB_dict_posting:
                try:
                    # if letter=='"':
                    #     letter='Ap'

                    string='posting_file_'+letter

                    if letter.isupper():
                        string = '/uppers/posting_file_' + letter
                    if letter.islower():
                        string = '/lowers/posting_file_' + letter
                    # if letter=='"':
                    #     string='posting_file_Ap'
                    utils.save_obj(indexer.AB_dict_posting[letter], string)
                except:

                    string = 'posting_file_A'+str(count)#TODO
                    utils.save_obj(indexer.AB_dict_posting[letter], string)

                    # print("something wrong with {}", string)
                    count+=1


            indexer.posting_file = {}
            indexer.AB_dict_posting = {}

            # for term in indexer.AB_dict_posting:
            #     utils.save_obj(indexer.AB_dict_posting[term[0]], "posting_file_{0}".format(term[0]))

        #     utils.save_obj(indexer.documents_info, "documents_info")
        #     indexer.documents_info = {}



    indexer.indexing_temp = {}
    indexer.entity_temp = {}
    print("--- %s seconds index end ---" % (time.time() - start_time))
    test3 = 1


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
