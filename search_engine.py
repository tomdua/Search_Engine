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

    # Iterate over every document in the file
    for idx, document in enumerate(documents_list):
        # parse the document
        parsed_document = p.parse_doc(document)
        number_of_documents += 1


    ###################### For small/big Capital letters ##################
    #     for term in parsed_document.term_doc_dictionary:
    #         if term not in term_dict.keys():
    #             term_dict[term] = 1
    #         else:
    #             term_dict[term] += 1
    #
    # for term in dict(sorted(term_dict.items())):
    #     if term[0].isupper():
    #         if term.lower() in term_dict:
    #             term_dict[term.lower()] += term_dict[term]
    #             del term_dict[term]
    #       #term_dict[term.lower()] += term_dict[term]
    #             #if not term.isupper():
    #                 #del term_dict[term]
    #     elif term[0].isupper() and term_dict[term] > 1:
    #         term_dict[term.upper()] += term_dict[term]
    #         del term_dict[term]
    ##############################################################
        # index the document data
        #indexer.add_new_doc(parsed_document)
    temp=p.tempDocuments
    print('Finished parsing and indexing. Starting to export files')
    utils.save_obj(indexer.inverted_idx, "inverted_idx")
    utils.save_obj(indexer.postingDict, "posting")


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
