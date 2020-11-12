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
    number_of_documents = 0

    config = ConfigClass()
    r = ReadFile(corpus_path=config.get__corpusPath())
    p = Parse()
    stemming= Stemmer()
    indexer = Indexer(config)
    documents_list = r.read_file()
    term_dict = {}
    documents_list_afterParser=[]
    entity_dict_temp={}
    inverted_idx_for1000 = []
    postingDict_for1000 = []

    # Iterate over every document in the file
    for idx, document in enumerate(documents_list):
        # parse the document
        parsed_document = p.parse_doc(document)
        number_of_documents += 1
        documents_list_afterParser.append(parsed_document)

        #enter to temp entity dic
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
                if term[0].isupper():
                    if term.lower() in term_dict:
                        term1=term.lower()
                        document.term_doc_dictionary[term1] = document.term_doc_dictionary.pop(term)
                        #del document.term_doc_dictionary[term]
                    elif term.isupper():
                        continue
                    else:
                        term2=term.upper()
                        document.term_doc_dictionary[term2] = document.term_doc_dictionary.pop(term)
                        #del document.term_doc_dictionary[term]

    ########################################################################################

    ###################### For entities ####################################################

    for document in documents_list_afterParser:
        for term in document.term_doc_dictionary.copy():
            if term in entity_dict_temp:
                if entity_dict_temp[term]>1:
                    continue
                elif entity_dict_temp[term]==1:
                    del document.term_doc_dictionary[term]
            else:
                continue
    ########################################################################################

    ########################################################################################

    ####################### index the parse document data ##################################

    for count,document in enumerate(documents_list_afterParser,1):#to parse 1000 doc
        indexer.add_new_doc(document)
        inverted_idx_for1000.append(indexer.inverted_idx)
        postingDict_for1000.append(indexer.postingDict)
        if count%10==0:
            print('Finished parsing and indexing 1000 documents. Starting to export files')
            #print('Finished parsing and indexing. Starting to export files')
            utils.save_obj(inverted_idx_for1000, "inverted_idx")
            utils.save_obj(postingDict_for1000, "posting")

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
