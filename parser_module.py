import re

from nltk.corpus import stopwords
from document import Document


class Parse:

    def __init__(self):
        self.stop_words = stopwords.words('english')
        new_words = {"www", "https", "http", "status", "instagram.com", "twitter.com", "t.co", "rt", "RT",'instagram','facebook','twitter','co','com','web'}
        self.stop_words.extend(new_words)
        self.entity_temp = {}
        self.expandUrl = False
        self.stemming = None
        self.inverted_idx = {}
        self.inverted_idx_stemming = {}

    def replece_sign(self, text):
        """
        :param text: a full text from the twitter.
        :return: term witt correct sign.
        #20 percentage - 20%, 3 dollar - 3$
        """
        if 'percent' in text or 'percentage' in text or 'Thousand' in text or 'thousand' in text or 'Million' in text or 'million' in text or 'Billion' in text or 'billion' in text:
            if 'percentage' in text:
                text = text.replace(' percentage', '%')
            if 'percent' in text:
                text = text.replace(' percent', '%')
            if 'Thousand' in text:
                text = text.replace(' Thousand', 'K')
            if 'thousand' in text:
                text = text.replace(' thousand', 'K')
            if 'Million' in text:
                text = text.replace(' Million', 'M')
            if 'million' in text:
                text = text.replace(' million', 'M')
            if 'Billion' in text:
                text = text.replace(' Billion', '%')
            if 'billion' in text:
                text = text.replace(' billion', '%')
        return text




    def replece_covid(self, text):
        """
        :param text: a full text from the twitter.
        :return: change covid-19 to coronavirus
        #Covid-19 - coronavirus
        """
        if 'Covid-19' in text or 'COVID-19' in text or 'Covid' in text or 'COVID' in text or 'covid-19' in text or 'covid19' in text or 'Covid19' in text or 'COVID19' in text:
            if 'Covid-19' in text:
                text = text.replace('Covid-19', ' coronavirus')
            if 'COVID-19' in text:
                text = text.replace('COVID-19', ' coronavirus')
            if 'covid-19' in text:
                text = text.replace('covid-19', ' coronavirus')
            if 'Covid' in text:
                text = text.replace('Covid', ' coronavirus')
            if 'COVID' in text:
                text = text.replace('COVID', ' coronavirus')
            if 'covid19' in text:
                text = text.replace('covid19', ' coronavirus')
            if 'Covid19' in text:
                text = text.replace('Covid19', ' coronavirus')
            if 'COVID19' in text:
                text = text.replace('COVID19', ' coronavirus')

        return text




    def parse_sentence(self, text, doc, stemming):
        """
        This function tokenize, remove stop words and apply lower case for every word within the text
        :param text:
        :return:
        """
        q_text = text
        if text:
            text_tokens = []
            try:
                text = self.replece_sign(text)

                text = self.replece_covid(text)
                ########## for precent ##################################################

                rx2 = re.compile(r"[-+]?\d*\.?\d*\%")
                precent_parse = rx2.findall(text)
                if precent_parse:
                    text = rx2.sub("", text)
                #########################################################################


                ########## for fruction #################################################
                rx2 = re.compile(r"[-+]?\d+\s+\d+\/\d+|[-+]?\d+\/\d+")
                fruction_parse = rx2.findall(text)
                if fruction_parse:
                    text = rx2.sub("", text)

                #########################################################################

                ############ for numbers with point #####################################
                rx2 = re.compile(r'[-+]?\d+\.+\d+\.*\d*\.*\d*\.*\d*')
                point_number_temp = rx2.findall(text)
                point_number_parse = []
                if point_number_temp:
                    point_number_parse = [e for e in point_number_temp if '%' not in e and e.count('.') == 1]
                if point_number_parse:
                    text = rx2.sub("", text)
                    point_number_parse = [self.change_format(float(w)) for w in point_number_parse]

                #########################################################################

                ############ for numbers with comma #####################################
                rx2 = re.compile(r"[-+]?\d+\,+\d+\,*\d+\,*\d+")
                comma_number_parse = rx2.findall(text)
                if comma_number_parse:
                    comma_number_parse = [w for w in comma_number_parse if len(w) < 16]
                    text = rx2.sub("", text)
                    comma_number_parse = [self.change_format(int(w.replace(',', ''))) for w in comma_number_parse]

                #########################################################################

                #################### parse url #########################
                rx2 = re.compile(r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-./_#?=])+|wwww\.(?:[a-zA-Z]|[0-9]|[$-./_#?=])+')
                url_temp = rx2.findall(text)
                url_parse = []
                if url_temp:
                    text = rx2.sub("", text)
                    for url in url_temp:
                        url_parse = url_parse +self.parser_url(url)
                #######################################################

                #################### hashtags ########################
                hashtag_parse=[]
                if '#' in text:
                    hashtag_parse = self.parse_hashtag(text)
                if hashtag_parse:
                    for w in hashtag_parse:
                        if w[0] is '#':
                            text = text.replace(w, '', 1)

                rx2 = re.compile(r'#\w+')
                to_garbage = rx2.findall(text)
                if to_garbage:
                    text = rx2.sub("", text)
                #######################################################

                #################### mentions #########################
                rx2 = re.compile(r'(@+\w*)')
                mention_parse = rx2.findall(text)
                if mention_parse:
                    text = rx2.sub("", text)
                #######################################################


                #################### words with ` or 's or `s  ########
                rx2 = re.compile(r'\’s|\'s')
                end_with_s_to_garbage = rx2.findall(text)
                if end_with_s_to_garbage:
                    text = rx2.sub("", text)

                rx2 = re.compile(r'\w+\’\w+')
                with_delimeter_parse = rx2.findall(text)
                if with_delimeter_parse:
                    text = rx2.sub("", text)
                #######################################################


                #################### 1 numbers #########################
                # mention_parse = self.parse_mentions(text)
                rx2 = re.compile(r'\b\d{1}\b')
                single_number_parse = rx2.findall(text)
                if single_number_parse:
                    text = rx2.sub("", text)
                #######################################################


                ##########  extra words ################################

                rx2 = re.compile(r"[^a-zA-Z0-9]|\b\w{1}\b")
                to_garbage = rx2.findall(text)
                if to_garbage:
                    text = rx2.sub(" ", text)
                ########################################################

                text_tokens = text.split()
                text_tokens = text_tokens + precent_parse + fruction_parse + point_number_parse +url_parse+ comma_number_parse + with_delimeter_parse + hashtag_parse + mention_parse +single_number_parse
            except Exception as e:
                print(e)
                print("something wrong with {}", text)
        else:
            return

        if not doc:

            if stemming:
                text_tokens_with_stemming = self.words_stemming(text_tokens)
            tokinzed_entity = self.get_continuous_chunks(q_text)
            text_tokens = text_tokens + tokinzed_entity

            if stemming:
                text_tokens = text_tokens_with_stemming
                text_tokens = text_tokens  + tokinzed_entity
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
        term_dict_with_stemming = {}
        doc_pos = {}

        match = re.search(r'\bRT\b',full_text)
        match2 = re.search(r'\brt\b',full_text)

        if match or match2:
            return []

        try:
            rx2 = re.compile(r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-./_#?=])+|wwww\.(?:[a-zA-Z]|[0-9]|[$-./_#?=])+')
            url_external = rx2.findall(url)
            url_full_text = rx2.findall(full_text)

            ###############################################################
            if url_external:
                ########## Url of full text empty, but extrnal not#############
                if url_full_text:
                    if len(url_external) > 1:
                        full_text = self.reaplce_url(full_text, url_full_text, url_external)
                        for url in url_external[2:]:
                            full_text = full_text + ' ' + url
                    else:
                        full_text = self.reaplce_url(full_text, url_full_text, url_external)
                else:
                    for url in url_external:
                        full_text = full_text + ' ' + url


        except:
            print("something wrong with {}", tweet_id)



        ##################### stop-words #####################################
        pattern = re.compile(r'\b(' + r'|'.join(self.stop_words) + r')\b\s*',re.IGNORECASE)
        full_text = pattern.sub('', full_text)
        ########################################################################

        tokenized_text = self.parse_sentence(full_text, True, True)
        tokinzed_entity = self.get_continuous_chunks(full_text)
        if tokenized_text:
            tokenized_text_with_stemming = self.words_stemming(tokenized_text)
        else:
            return {}

        for entity in tokinzed_entity:
            if entity not in self.entity_temp:
                self.entity_temp[entity] = 1
            else:
                self.entity_temp[entity] += 1

        tokenized_text = tokenized_text + tokinzed_entity



        doc_length = len(full_text)
        for term in tokenized_text:
            if term not in term_dict:
                term_dict[term] = 1
            if term in term_dict:
                term_dict[term] += 1
            if term not in self.inverted_idx:
                self.inverted_idx[term] = 1
            if term in self.inverted_idx:
                self.inverted_idx[term] += 1

        ########## for stemming #########################################



        for term in tokenized_text_with_stemming:
            if term not in term_dict_with_stemming:
                term_dict_with_stemming[term] = 1
            if term in term_dict_with_stemming:
                term_dict_with_stemming[term] += 1
            if term not in self.inverted_idx_stemming:
                self.inverted_idx_stemming[term] = 1
            if term in self.inverted_idx_stemming:
                self.inverted_idx_stemming[term] += 1

        document = Document(tweet_id, tweet_date, full_text, url, retweet_text, retweet_url, quote_text,
                            quote_url, term_dict, term_dict_with_stemming, doc_length, doc_pos)
        return document

    ############ private func ##############################

    def to_stemming(self, tokenized_text):
        text_with_stemming = [self.stemming.stem_term(w) for w in tokenized_text]
        return text_with_stemming

    def words_stemming(self, tokenized_text):
        tokenized_text_with_stemming=[]
        try:
            tokenized_text_with_stemming = [self.stemming.stem_term(w) for w in tokenized_text]
        except:
            print('wrong in stemming')

        return tokenized_text_with_stemming

    def change_format(self, num):
        """
        :param: int/float - number
        :return: string- number
        """
        if abs(num) > 999:
            magnitude = 0
            while abs(num) >= 1000:
                magnitude += 1
                num /= 1000.0
            # add more suffixes if you need them
            return '%.3f%s' % (num, ['', 'K', 'M', 'B', 'T', 'P'][magnitude])
        else:
            return str(num)


    def parse_hashtag(self, text):
        """
        :param text: a full text from the twitter.
        :return: hashtags terms split from the text.
        #stayAtHome - stay, at, home, #stayathome
        """
        # rx2 = re.compile(r"[^a-zA-Z0-9\s]|\b\w{1}\b")
        # to_garbage = rx2.findall(text)
        hashtags_term = []
        hashtags_term_temp=[]
        # test = rx2.findall(text)
        tag = re.findall(r'#\w*', text)
        if tag:
            for term in tag:
                if not (re.match(r"[^\u0041-\u007A]",term[1:])) and len(term)!=1:
                    # if len(term) > 1:
                        if '_' in term:
                            temp_term = term
                            temp = term.lower().replace("#", "")
                            temp = temp.split('_')
                            for w in temp:
                                if w.isascii() and len(w)>1:
                                    hashtags_term.append(w)
                                hashtags_term.append(temp_term[0] + temp_term[1:].lower())
                            continue
                        else:
                            temp=term
                            term = term.replace("#", "")
                            rx2 = re.compile(r"[a-z]+?=[A-Z]|[A-Z][a-z]+")
                            to_add = [w.lower() for w in rx2.findall(term)]
                            to_add2 =rx2.sub("", term)
                            hashtags_term += hashtags_term_temp + to_add
                            if len(to_add2)>1:
                                hashtags_term.append(to_add2.lower())
                            hashtags_term.append(temp[0] + temp[1:].lower())
                else:
                    continue
        return hashtags_term

    def parser_url(self, url):
        url_parse=[]
        url_parse_new = []

        if len(url) > 2:
            url2 = url

            # rex = re.compile(r"https?://(www\.)?")
            url3 = re.findall(r'www|https?|\w+\.\w+', url)
            url_parse = re.sub(r"https?://|www.|\w+\.\w+", "", url2).split('/')
            rx2 = re.compile(r'([A-Za-z0-9]+)')
            for w in list(url_parse):
                if len(w)<2:
                    url_parse.remove(w)
                    continue
                w = rx2.findall(w)
                # url_parse.remove(w)
                if w:
                    if w not in url_parse:
                        url_parse_new=url_parse_new+w
            url_parse_new=url_parse_new+url3


        for url in list(url_parse_new):
            if re.match(r'(?:\d+[a-zA-Z]+|[a-zA-Z]+\d+)',url):
                url_parse_new.remove(url)

        return url_parse_new

    def get_continuous_chunks(self, text):

        rx2 = re.compile(r'[A-Z][-a-zA-Z]*(?:\s+[A-Z][-a-zA-Z]*)*')
        matches = rx2.findall(text)
        tokinzed_entity_new = [e for e in matches if len(e.split()) > 1]
        return tokinzed_entity_new


    def reaplce_url(self, full_text, url_full_text, url_external):
        for term in url_full_text:
            extrenal_idx = url_external[0]
            full_text = full_text.replace(term, extrenal_idx[0:len(extrenal_idx)])
        return full_text
