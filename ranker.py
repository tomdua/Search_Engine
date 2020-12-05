import gc
import numpy as np
import pickle
from numpy import dot
from numpy.linalg import norm


class Ranker:
    def __init__(self):
        pass


    def get_vector(self,model, term):
        try:
            return model[term]
        except:
            return np.zeros((25,))




    def rank_relevant_doc(self, relevant_doc, model, query_vector, stemming_bool):

        twitts_dict = []
        for id in relevant_doc:
            if stemming_bool:
                terms_doc = self.load_doc(id,0)
            else:
                terms_doc = self.load_doc(id,1)

            twitts_dict.append(terms_doc)

        sentence_vectors = []
        for dict in twitts_dict:
            if len(dict) != 0:
                v = sum([self.get_vector(model, w) for w in dict]) / (len(dict) + 0.001)
            else:
                v = np.zeros((25,))
            sentence_vectors.append(v)

        array_vectors = np.array(sentence_vectors)
        array_query = np.array(query_vector)

        scores = []

        for item in array_vectors:
            cos_sim = dot(item, array_query) / (norm(item) * norm(array_query))
            scores.append(cos_sim)

        ranked_result = sorted(((scores[i], i) for i, s in enumerate(relevant_doc)), reverse=True)

        relevant_doc_list = list(relevant_doc)
        relevant_doc=[]
        for i in ranked_result:
            doc_id=i[1]
            doc_rank=[i[0]]
            id=[relevant_doc_list[doc_id]]
            relevant_doc.append((id,doc_rank))

        """
        This function provides rank for each relevant document and sorts them by their scores.
        The current score considers solely the number of terms shared by the tweet (full_text) and query.
        :param relevant_doc: dictionary of documents that contains at least one term from the query.
        :return: sorted list of documents by score
        """
        return relevant_doc


    def load_doc(self, id,index):
        gc.disable()
        number_index = id[len(id) - 4:]
        with open('./posting/document_after_index/documents_after_index_{0}.pkl'.format(number_index), 'rb') as f:
            while 1:
                try:
                    ans = {}
                    objs = pickle.load(f)
                    if id in objs:
                        ans = objs[id][index]

                    if ans:
                        gc.enable()
                        f.close()
                        return ans

                except EOFError:
                    break

    def retrieve_top_k(self, sorted_relevant_doc, k):
        """
        return a list of top K tweets based on their ranking from highest to lowest
        :param sorted_relevant_doc: list of all candidates docs.
        :param k: Number of top document to return
        :return: list of relevant document
        """
        return sorted_relevant_doc[:k]
