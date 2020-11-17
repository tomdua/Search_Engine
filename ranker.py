import json

from numpy import asarray, zeros


class Ranker:
    def __init__(self):
        self.posting_file= {}
        self.inverted_idx= {}
        #pass

    #@staticmethod
    def rank_relevant_doc(self,relevant_doc):
        # corpus= []
        full_text_array= []

        with open('documents_info.txt') as json_file:
            documents_info = json.load(json_file)

        # # longest_sentence
        # for id in relevant_doc:
        #     max_lengh(documents_info[id])
        #
        # unique_words =len(self.inverted_idx)














        embeddings_dictionary = dict()
        glove_file = open('glove.twitter.27B.200d.txt', encoding="utf8")

        for line in glove_file:
            records = line.split()
            word = records[0]
            vector_dimensions = asarray(records[1:], dtype='float32')
            embeddings_dictionary[word] = vector_dimensions

        glove_file.close()

        embedding_matrix = zeros((len(self.inverted_idx), 100))
        for word, index in self.inverted_idx.word_index.items():
            embedding_vector = embeddings_dictionary.get(word)
            if embedding_vector is not None:
                embedding_matrix[index] = embedding_vector







        """
        This function provides rank for each relevant document and sorts them by their scores.
        The current score considers solely the number of terms shared by the tweet (full_text) and query.
        :param relevant_doc: dictionary of documents that contains at least one term from the query.
        :return: sorted list of documents by score
        """
        return sorted(relevant_doc.items(), key=lambda item: item[1], reverse=True)

    #@staticmethod
    def retrieve_top_k(self,sorted_relevant_doc, k=1):
        """
        return a list of top K tweets based on their ranking from highest to lowest
        :param sorted_relevant_doc: list of all candidates docs.
        :param k: Number of top document to return
        :return: list of relevant document
        """
        return sorted_relevant_doc[:k]
