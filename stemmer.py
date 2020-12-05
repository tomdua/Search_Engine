from nltk.stem import snowball
from nltk.stem.lancaster import LancasterStemmer


class Stemmer:
    def __init__(self):
        nltk_lancaster = LancasterStemmer
        self.stemmer = nltk_lancaster()

    def stem_term(self, token):
        """
        This function stem a token
        :param token: string of a token
        :return: stemmed token
        """
        return self.stemmer.stem(token)
