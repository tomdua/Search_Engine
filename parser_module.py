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


# def find_postion_2_indexs(test_str, test_sub):
#     if test_str.find(test_sub) != -1:
#         res = [i for i in range(len(test_str)) if test_str.startswith(test_sub, i)]
#     elif test_str.find(test_sub.upper()) != -1:
#         res = test_str.find(test_sub.upper())
#     else :
#         res = test_str.find(test_sub.title())
#     return res


def find_postion(full_text, term, more_than_one):
    if more_than_one is True:
        index = [i for i in range(len(full_text)) if full_text.startswith(term , i)]
    else:
        if full_text.find(term) != -1:
            index = full_text.find(term)
        elif full_text.find(term.upper()) != -1:
            index = full_text.find(term.upper())
        else:
            index = full_text.find(term.title())

    return index

class Parse:
    def __init__(self):
        self.stop_words = stopwords.words('english')
        new_stop_words = {"%","status","twitter.com","", "www", '', "https", "http", "^", "!", "?", "^", "&", "*", "#", "(", ")", ",", ";", ":", "{",
                     "}","_", "-", "[", "]", "<", ">", "|", "+", "`", "'", ".", "...", "..", "@", "’", "I", "“", "•",
                     "️", "⬇", "'s", "``", "''", "”", "@:", "_","++.pls","....","......",".....","=","—","status","instagram.com","twitter.com","t.co"}

        for i in new_stop_words:
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
            rx2 = re.compile(r"[-+]?\d*\.?\d*\%")
            text0 = rx2.findall(text)
            if text0:
                for w in text0:
                    text = text.replace(w, '', 1)
            #########################################################################

            ########## for fruction #################################################
            rx2 = re.compile(r"[-+]?\d+\s+\d+\/\d+|[-+]?\d+\/\d+")
            text1 = rx2.findall(text)
            if text1:
                for w in text1:
                    text = text.replace(w, '', 1)
            #########################################################################

            ############ for numbers with point #####################################
            rx2 = re.compile(r'[-+]?\d+\.+\d+\.*\d*\.*\d*\.*\d*')
            text3 = rx2.findall(text)
            text3_new = []
            if text3:
                text3_new = [e for e in text3 if '%' not in e and e.count('.') == 1]
            if text3_new:
                for w in text3_new:
                    text = text.replace(w, '', 1)
            text3_new = [self.change_format(float(w)) for w in text3_new]
            #########################################################################

            ############ for numbers with comma #####################################
            rx2 = re.compile(r"[-+]?\d+\,+\d+\,*\d+\,*\d+")
            text2 = rx2.findall(text)
            if text2:
                for w in text2:
                    text = text.replace(w, '', 1)
            text2 = [self.change_format(int(w.replace(',', ''))) for w in text2]
            #########################################################################

            #################### parse url #########################
            rx2 = re.compile(r'(https?://[^\s]+)')
            text4 = rx2.findall(text)
            text4_correct = []
            if text4:
                for w in text4:
                    text = text.replace(w, '', 1)
                    text4_correct = text4_correct + self.parser_url(w)
            #######################################################

            # test=[w for w in text if any(c for c in w if unicodedata.category(c) == 'So')]

            #################### parse emoji #########################
            text6=[]
            # rx2 = re.compile(r'[^\w\s,]')
            text5 = [w for w in text if any(c for c in w if unicodedata.category(c) == 'So')]
            try:
                text6 = [w for w in text if '\n' not in w and '🩸' not in w and any(
                    c for c in w if unicodedata.name(c).startswith("EMOJI MODIFIER"))]
            except:
                print("An exception occurred")

            # text5_new=[]
            if text5:
                for w in text5:
                    text = text.replace(w, '', 1)
            if text6:
                for w in text6:
                    text = text.replace(w, '', 1)

                    # text4_correct = text4_correct + self.parser_url(w)
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
            tokinzed_mentions = self.parse_mentions(text)
            # rx2 = re.compile(r'(@[^\s]+)')
            # text8 = rx2.findall(text)
            # text4_correct = []
            if tokinzed_mentions:
                for w in tokinzed_mentions:
                    text = text.replace(w, '', 1)
            #######################################################

            ########## for some other words ######################
            rx2 = re.compile(r"[-+]?\d*\w*\….?|\w*[/]\w*\-?\d*|\w*\'\w*")
            text8 = rx2.findall(text)
            if text8:
                for w in text8:
                    text = text.replace(w, '', 1)
            ################################################

            text_tokens = word_tokenize(text)
            # text_tokens=regexp_tokenize(text, pattern=r"\s|[\.,;']\d+\.\d+", gaps=True)
            text_tokens = text_tokens + text0 + text1 + text3_new + text2 + text5 + tokinzed_hatags + tokinzed_mentions
            if not self.expandUrl:
                text_tokens = text_tokens + text4_correct
        else:
            return
        text_tokens_without_stopwords = [w for w in text_tokens if w not in self.stop_words]
        if self.stemming:
            text_tokens_without_stopwords = [self.stemming.stem_term(w) for w in text_tokens_without_stopwords]
        return text_tokens_without_stopwords

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
        if url:
            self.expandUrl = True
        # num = ' don't '
        # full_text = full_text + num
        # s1 = 'Blue Berries'
        # pattern = 'blue berries'
        # for match in re.finditer(pattern, s1):
        #     s = match.start()
        #     e = match.end()
        #     test1=0
        'It would be terrible if this murderous bigot got a prolonged QT interval, I mean his risk for clots and ischemia is already way up now….Plaquenil has a pretty long half life too. Bottoms up, you fascist waste of space.'
        tokenized_text = self.parse_sentence(full_text)
        tokinzed_quote = self.parse_quotes(full_text)
        # if tokinzed_quote:
        #     test=1
        tokinzed_entity_new = self.get_continuous_chunks(full_text)

        #tokinzed_entity_new = [e for e in tokinzed_entity if len(e.split()) > 1]

        # enter to temp entity dic
        for entity in tokinzed_entity_new:
            if entity not in self.entity_temp.keys():
                self.entity_temp[entity] = 1
            else:
                self.entity_temp[entity] += 1

        tokenized_text = tokenized_text + tokinzed_quote + tokinzed_entity_new
        doc_pos = {}
        if self.expandUrl:
            tokinzed_url = self.parser_url(url)
            tokenized_text = tokenized_text + tokinzed_url
            # for term in tokinzed_url:
            #     doc_pos[term] = {3, url.find(term)}
            #     # list.append(term)
            #     tokenized_text.remove(term)

        ################################################################

        ########## insert the word postion and tf ######################
        doc_length = len(full_text)
        for term in tokenized_text:
            if term in tokinzed_url:
                if term not in term_dict.keys():
                    term_dict[term] = 1
                    doc_pos[term.lower()] = {3: find_postion(url,term,False)}
                else:
                    term_dict[term] += 1
                    doc_pos[term.lower()] = {3: find_postion(url,term,True)}

            else:
                if term not in term_dict.keys():
                    term_dict[term] = 1
                    doc_pos[term.lower()] = {2:find_postion(full_text,term, False)}

                else:
                    term_dict[term] += 1
                    doc_pos[term.lower()] = {2:find_postion(full_text , term, True)}

        # tokenized_text.append()
        document = Document(tweet_id, tweet_date, full_text, url, retweet_text, retweet_url, quote_text,
                            quote_url, term_dict, doc_length,doc_pos)
        # self.tempDocuments=self.tempDocuments+document
        return document

    ############ private func ##############################

    def change_format(self, num):
        """
        :param: int/float - number
        :return: string- number
        """
        if num > 999:
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

    def parse_mentions(self, text):
        """
        :param text: a full text from the twitter.
        :return: mentions terms split from the text.
        @stayAtHome - @stayAtHome
        """
        mentions_trem = []
        # tokenize = word_tokenize(text)
        mentions_trem=re.findall(r'(@+\w*)', text)
        # for i in range(len(tokenize) - 1):
        #     if tokenize[i] is '@':
        #         mentions_trem.append('@' + tokenize[i + 1])

        return mentions_trem


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
        if tag.__len__() >= 1:
            for term in tag:
                hashtags_trem.append(term[0] + term[1:].lower())
                hashtags_trem += [w.lower() for w in re.findall('[a-z|A-Z][^A-Z|_]*', term)]
        return hashtags_trem


    def parser_url(self, url):
        """
        :param url: a url from twitter.
        :return: url split according to the url laws.
        #https://www.instagram.com/p/CD7fAPWs3WM/?igshid=o9kf0ugp1l8x - https, www, instagram.com, p, CD7fAPWs3WM, igshid, o9kf0ugp1l8x
        """
        url_parse=[]
        if len(url)>2:
            # tokenize = word_tokenize(url)
            # i=0
            # for token in range(len(tokenize)):
            #     new_token = re.split('[/\=:#?]', tokenize[token])
            #     if new_token[i] not in self.stop_words:
            #         terms.extend(new_token)
            #     i=i+1
            terms = re.split('[\[/:"//?={"\]]' , url)
            url_parse = [w for w in terms if w not in self.stop_words]
        # url_parse = [w for w in terms if w not in self.stop_words]

        # terms = re.findall('https?://(?:[-\w.]|(?:%[\da-fA-F]{2}))+', url)
        # url_parse = [w for w in terms if w not in self.stop_words]
        return url_parse

    def get_continuous_chunks(self, text):
        """
            :param url: a full text from the twitter.
            :return: url the all entity
        """
        #
        # text = ("Madonna has a new album\n"
        #             "Paul Young has no new album\n"
        #             "Emmerson Lake-palmar is not here\n"
        #             "Emmerson Lake-Palmer-Tom is not here\n"
        #             "Emmerson Lake-Palmer Tom Matan Th this \n"
        #             "The Matan Duany\n"
        #             "Do you TOm Duany Matan gal \n")

        # list=[]
        # regex = r"[A-Z][-a-zA-Z]*(?:\s+[A-Z][-a-zA-Z]*)*((?:[A-Z][a-z]*))*"
        # matches = re.finditer(regex , text)
        # for matchNum , match in enumerate(matches , start=1) :
        #     if len(match[0].split())>1:
        #         list.append(match[0])
        #
        # list
        # text='Tom Duany fsafsafssd Tom Matan Duany'
        # rx2 = re.compile(regex)
        # tomy = re.findall((r'[A-Z][-a-zA-Z](?:\s+[A-Z][-a-zA-Z])'),text)
        # tom = rx2.findall(text)



        rx2 = re.compile(r'[A-Z][-a-zA-Z]*(?:\s+[A-Z][-a-zA-Z]*)*')
        matches = rx2.findall(text)
        tokinzed_entity_new = [e for e in matches if len(e.split()) > 1]

        return tokinzed_entity_new


        #
        # chunked = ne_chunk(pos_tag(word_tokenize(text)))
        # continuous_chunk = []
        # current_chunk = []
        # for i in chunked:
        #     if type(i) == Tree:
        #         current_chunk.append(" ".join([token for token, pos in i.leaves()]))
        #     if current_chunk:
        #         named_entity = " ".join(current_chunk)
        #         if named_entity not in continuous_chunk:
        #             continuous_chunk.append(named_entity)
        #             current_chunk = []
        #     else:
        #         continue
        # return continuous_chunk
