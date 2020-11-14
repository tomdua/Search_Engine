import collections

from reader import ReadFile
from configuration import ConfigClass
from parser_module import Parse
from stemmer import Stemmer
from indexer import Indexer
from searcher import Searcher
import utils


def run_engine():
    """

    :return:
    """
    AB_dict_test2 = utils.load_obj("posting_file")
    AB_posting=collections.OrderedDict(sorted(AB_dict_test2[len(AB_dict_test2)-1].items()))
    dict=utils.load_obj("inverted_idx")
    AB_dict=collections.OrderedDict(sorted(dict[len(dict)-1].items()))
    test=AB_posting['#']
    def find(val, lis):
        ind = [(j, i, k) for j, x in enumerate(lis) for i, y in enumerate(x) \
               for k, z in enumerate(y) if z == val]
        return ind[0][0] if ind else None
    #indices = find('#1',test)

    config = ConfigClass()
    r = ReadFile(corpus_path=config.get__corpusPath())
    p = Parse()
    stemming = Stemmer()
    indexer = Indexer(config)
    documents_list = r.read_file()
    term_dict = {}
    documents_list_afterParser = []
    entity_dict_temp = {}
    number_of_documents = 0
    usingStemming =input("You will want to use stemming?(yes/no): ")
    if usingStemming=='yes':
        usingStemming=True
        p.stemming=stemming
    else:
        usingStemming=False

    # Iterate over every document in the file
    for idx, document in enumerate(documents_list):
        # parse the document
        parsed_document = p.parse_doc(document)
        number_of_documents += 1
        documents_list_afterParser.append(parsed_document)

        # enter to temp entity dic
        for entity in p.entity_temp:
            if entity not in entity_dict_temp.keys():
                entity_dict_temp[entity] = 1
            else:
                entity_dict_temp[entity] += 1

    ###################### For small/big Capital letters ##################################
    for document in documents_list_afterParser:
        for term in document.term_doc_dictionary:
            if term not in term_dict.keys():
                term_dict[term] = 1
            else:
                term_dict[term] += 1

    for document in documents_list_afterParser:
        for term in document.term_doc_dictionary.copy():
            if isinstance(term, str):
                try:
                    if term[0].isupper():
                        if term.lower() in term_dict:
                            term1 = term.lower()
                            document.term_doc_dictionary[term1] = document.term_doc_dictionary.pop(term)
                            # del document.term_doc_dictionary[term]
                        elif term.isupper():
                            continue
                        else:
                            term2 = term.upper()
                            document.term_doc_dictionary[term2] = document.term_doc_dictionary.pop(term)
                            # del document.term_doc_dictionary[term]
                except:
                    print('as')
    ########################################################################################

    ###################### For entities ####################################################

    for document in documents_list_afterParser:
        for term in document.term_doc_dictionary.copy():
            if term in entity_dict_temp:
                if entity_dict_temp[term] > 1:
                    continue
                elif entity_dict_temp[term] == 1:
                    del document.term_doc_dictionary[term]
            else:
                continue
    ########################################################################################

    ####################### index the parse document data ##################################

    for count, document in enumerate(documents_list_afterParser, 1):  # to parse 1000 doc

        indexer.add_new_doc(document)

        if count % 10 == 0:
            # print('Finished parsing and indexing 1000 documents. Starting to export files')
            # print('Finished parsing and indexing. Starting to export files')
            AB_dict = {}

            for term in indexer.inverted_idx.keys():
                try:
                    # Update inverted index and posting
                    if term[0] not in AB_dict.keys():
                        AB_dict[term[0]] = []

                    AB_dict[term[0]].append(indexer.posting_file[term])
                except:
                    print("wrong")

            test1 = AB_dict
            utils.save_obj(AB_dict, "posting_file")
            utils.save_obj(indexer.inverted_idx, "inverted_idx")
            #AB_dict_test2 = utils.load_obj("AB_dict")
            #AB_dict_test2

    # dict=utils.load_obj("dictionary_Terms")
    test3 = 1



def load_index():
    print('Load inverted index')
    inverted_index = utils.load_obj("inverted_idx")
    return inverted_index


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
    print(inverted_index)
    for doc_tuple in search_and_rank_query(query, inverted_index, k):
        print('tweet id: {}, score (unique common words with query): {}'.format(doc_tuple[0], doc_tuple[1]))
