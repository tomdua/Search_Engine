import re
import unicodedata
import pandas as pd

import nltk
from nltk.tag import StanfordNERTagger
from nltk import regexp_tokenize, TweetTokenizer, ne_chunk, pos_tag
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize, regexp
from document import Document
from nltk.tree import Tree


class Parse:

    def __init__(self):
        self.stop_words = stopwords.words('english')
        new_words = {"", "www", '', "https", "http", "^", "!", "?", "^", "&", "*", "#", "(", ")", ",", ";", ":", "{",
                     "}", "-", "[", "]", "<", ">", "|", "+", "`", "'", ".", "...", "..", "@", "’", "I", "“", "•",
                     "️", "⬇", "'s", "``", "''", "”", "@:", "_", "++.pls", "....", "......", ".....", "=", "—",
                     "status", "instagram.com", "twitter.com", "t.co", "rt", "RT", "%","/", "…"}

        for i in new_words:
            self.stop_words.append(i)
        self.entity_temp = {}
        self.expandUrl = False
        self.stemming = None


    def parse_sentence(self, text):
        """
        This function tokenize, remove stop words and apply lower case for every word within the text
        :param text:
        :return:
        """

        if text:
            text_tokens=[]
            try:
                if '%' in text or 'percent' in text or 'percentage' in text or 'percentage' in text or 'Thousand' in text or 'Million' in text or 'Billion' in text:
                    if 'percentage' in text:
                        text = text.replace(' percentage', '%')
                    if 'percent' in text:
                        text = text.replace(' percent', '%')
                    if 'Thousand' in text:
                        text = text.replace(' Thousand', 'K')
                    if 'Million' in text:
                        text = text.replace(' Million', 'M')
                    if 'Billion' in text:
                        text = text.replace(' Billion', '%')

                ########## for precent ##################################################

                # text0=re.sub(r"[-+]?\d*\.?\d*\%","",text)
                rx2 = re.compile(r"[-+]?\d*\.?\d*\%")
                text0 = rx2.findall(text)
                if text0:
                    text = rx2.sub("", text)
                #         text = text.replace(w, '', 1)
                #########################################################################

                ########## for fruction #################################################
                rx2 = re.compile(r"[-+]?\d+\s+\d+\/\d+|[-+]?\d+\/\d+")
                text1 = rx2.findall(text)
                if text1:
                    text = rx2.sub("", text)

                #         text = text.replace(w, '', 1)
                #########################################################################

                ############ for numbers with point #####################################
                rx2 = re.compile(r'[-+]?\d+\.+\d+\.*\d*\.*\d*\.*\d*')
                text3 = rx2.findall(text)
                text3_new = []
                if text3:
                    text3_new = [e for e in text3 if '%' not in e and e.count('.') == 1]
                if text3_new:
                    text = rx2.sub("", text)
                    text3_new = [self.change_format(float(w)) for w in text3_new]
                #########################################################################

                ############ for numbers with comma #####################################
                rx2 = re.compile(r"[-+]?\d+\,+\d+\,*\d+\,*\d+")
                text2 = rx2.findall(text)
                if text2:
                    text2=[w for w in text2 if len(w)<16]
                    text = rx2.sub("", text)
                    text2 = [self.change_format(int(w.replace(',', ''))) for w in text2]
                #########################################################################

                #################### parse url #########################
                rx2 = re.compile(r'(https?://[^\s]+)')
                text4 = rx2.findall(text)
                text4_correct = []
                if text4:
                    text = rx2.sub("", text)
                    text4_correct = [self.parser_url(w) for w in text4]
                #######################################################

                #################### hashtags ########################
                tokinzed_hatags = self.parse_hashtag(text)
                # rx2 = re.compile(r'(#[^\s]+)')
                # text7 = rx2.findall(text)
                # text4_correct = []
                if tokinzed_hatags:
                    for w in tokinzed_hatags:
                        if w[0] is '#':
                            text = text.replace(w, '', 1)
                #######################################################

                #################### mentions #########################
                # tokinzed_mentions = self.parse_mentions(text)
                rx2 = re.compile(r'(@+\w*)')
                tokinzed_mentions = rx2.findall(text)
                if tokinzed_mentions:
                    text = rx2.sub("", text)
                #######################################################

                #################### parse emoji ######################

                rx2 = re.compile(r'[^\w\s,]')
                text5 = rx2.findall(text)

                if text5:
                    text = rx2.sub("", text)


                #############################################################

                ########## for some other words #############################

                rx2 = re.compile(r"[-+]?\d*\w*\….?|\w*[/]\w*\-?\d*|\w*\'\w*")
                text8 = rx2.findall(text)
                if text8:
                    text = rx2.sub("", text)

                #############################################################

                text_tokens = word_tokenize(text)
                # text_tokens=regexp_tokenize(text, pattern=r"\s|[\.,;']\d+\.\d+", gaps=True)
                text_tokens = text_tokens + text0 + text1 + text3_new + text2 + text5 + tokinzed_hatags + tokinzed_mentions
                if not self.expandUrl:
                    text_tokens = text_tokens + text4_correct
            except:
                print("something wrong with {}", text)
        else:
            return
        # text_tokens_without_stopwords = [w for w in text_tokens if w not in self.stop_words]
        # if self.stemming:
        #     text_tokens_without_stopwords = [self.stemming.stem_term(w) for w in text_tokens_without_stopwords]
        return text_tokens

    def parse_doc(self, doc_as_list):
        """
        This function takes a tweet document as list and break it into different fields
        :param doc_as_list: list re-preseting the tweet.
        :return: Document object with corresponding fields.
        """
        tweet_id = doc_as_list[0]
        tweet_date = doc_as_list[1]
        full_text = doc_as_list[2]
        url = doc_as_list[3]
        retweet_text = doc_as_list[4]
        retweet_url = doc_as_list[5]
        quote_text = doc_as_list[6]
        quote_url = doc_as_list[7]
        term_dict = {}
        doc_pos = {}

        if url:
            self.expandUrl = True
        line = " Call for work from home  https://t.co/fKiS5W3w2o"

        full_text = full_text + line
        tokenized_text = self.parse_sentence(full_text)
        tokinzed_quote = self.parse_quotes(full_text)
        tokinzed_entity = self.get_continuous_chunks(full_text)

        # enter to temp entity dic
        for entity in tokinzed_entity:
            if entity not in self.entity_temp.keys():
                self.entity_temp[entity] = 1
            else:
                self.entity_temp[entity] += 1

        tokenized_text = tokenized_text + tokinzed_quote + tokinzed_entity

        if self.expandUrl:
            tokinzed_url = self.parser_url(url)
            tokenized_text = tokenized_text + tokinzed_url

        # text_tokens = [w for w in tokenized_text if w not in self.stop_words]

        if self.stemming:
            text_tokens = [self.stemming.stem_term(w) for w in tokenized_text if
                           self.stemming.stem_term(w) not in self.stop_words]
        else:
            text_tokens = [w for w in tokenized_text if w not in self.stop_words]

        doc_length = len(full_text)
        for term in text_tokens:
            if term in tokinzed_url:
                if term not in term_dict.keys():
                    term_dict[term] = 1
                    doc_pos[term.lower()] = {3: self.find_postion(url, term, False)}
                else:
                    term_dict[term] += 1
                    doc_pos[term.lower()] = {3: self.find_postion(url, term, True)}

            else:
                if term not in term_dict.keys():
                    term_dict[term] = 1
                    doc_pos[term.lower()] = {2: self.find_postion(full_text, term, False)}

                else:
                    term_dict[term] += 1
                    doc_pos[term.lower()] = {2: self.find_postion(full_text, term, True)}

        document = Document(tweet_id, tweet_date, full_text, url, retweet_text, retweet_url, quote_text,
                            quote_url, term_dict, doc_length, doc_pos)
        # self.tempDocuments=self.tempDocuments+document
        return document

    ############ private func ##############################

    def change_format(self, num):
        """
        :param: int/float - number
        :return: string- number
        """
        if num > 999 and len(num)<11:
            magnitude = 0
            while abs(num) >= 1000:
                magnitude += 1
                num /= 1000.0
            # add more suffixes if you need them
            return '%.3f%s' % (num, ['', 'K', 'M', 'B', 'T', 'P'][magnitude])
        else:
            return str(num)

    def parse_quotes(self, text):
        """
        :param text: a full text from the twitter.
        :return: quotes terms.
        'The best beer in the world'
        """
        rx2 = re.compile(r'"(?:(?:(?!(?<!\\)").)*)"')
        matches = rx2.findall(text)
        return matches

    # def parse_mentions(self, text):
    #     mentions_trem = []
    #     tokenize = word_tokenize(text)
    #     for i in range(len(tokenize) - 1):
    #         if tokenize[i] is '@':
    #             mentions_trem.append('@' + tokenize[i + 1])
    #     return mentions_trem

    def parse_hashtag(self, text):
        """
        :param text: a full text from the twitter.
        :return: hashtags terms split from the text.
        #stayAtHome - stay, at, home, #stayathome
        """
        #text='#tom_matan'
        # text= "#TomMatanNoy dfsafasdfasfds #rrerretre trotro #Almog_Rotam_ew"
        hashtags_trem = []
        tag=re.findall(r'(#+\w*)', text)
        if tag:
            for term in tag:
                hashtags_trem.append(term[0] + term[1:].lower())
                hashtags_trem += [w.lower() for w in re.findall('[a-z|A-Z][^A-Z|_]*', term)]
        return hashtags_trem



    def parser_url(self, url):

        url_parse=[]
        if len(url)>2:
            url_parse = re.split('[\[/:"//?={"\]]' , url)
            # url_parse = [w for w in terms if w not in self.stop_words]
        return url_parse

    def get_continuous_chunks(self, text):

        rx2 = re.compile(r'[A-Z][-a-zA-Z]*(?:\s+[A-Z][-a-zA-Z]*)*')
        matches = rx2.findall(text)
        tokinzed_entity_new = [e for e in matches if len(e.split()) > 1]
        return tokinzed_entity_new

    def find_postion(self, full_text, term, more_than_one):

        if more_than_one is True:
            index = [i for i in range(len(full_text)) if full_text.startswith(term, i)]
        else:
            if full_text.find(term) != -1:
                index = full_text.find(term)
            elif full_text.find(term.upper()) != -1:
                index = full_text.find(term.upper())
            else:
                index = full_text.find(term.title())

        return index
