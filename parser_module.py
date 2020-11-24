import re

from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize, regexp
from document import Document


class Parse:

    def __init__(self):
        self.stop_words = stopwords.words('english')
        new_words = {"www", '', "https", "http", "^", "!", "?", "^", "&", "*", "#", "(", ")", ",", ";", ":", "{",
                     "}", "-", "[", "]", "<", ">", "|", "+", "`", "'", ".", "...", "..", "@", "’", "I", "“", "•",
                     "️", "⬇", "'s", "``", "''", "”", "@:", "_", "++.pls", "....", "......", ".....", "=", "—",
                     "status", "instagram.com", "twitter.com", "t.co", "rt", "RT", "%", "/", "…", '"', '་', '᠂', '$',
                     '":"', '\\', '__vfz', '_twitter', '_ツ_', '_____', '__', '______________', '_____________',
                     '__________', '___', '______________________', '_______', '________', '________________________',
                     '_______________________________', '______', '~', '~r', '~3', '=nd', '£', '​', '‍', '‐', '–', '‘',
                     '⁦', '🩸', '🦠', '🦖', '🥺', '🥰', '🇺', '🇹', '🇸', '🇷', '🇴', '🇳', '🇰', '🇮', '🇪', '🇩',
                     '🇨', '🇦', '⬇️', '✨', '♂', '☺', '▶', '⅕', '™', '£10bn', '⁦cheived', '™️', '☺️', '🇨🇦', '🇩🇰',
                     '🇩🇪', '🇮🇹', '🇳🇴', '🇷🇸', '🇸🇪', '🇺🇸', '🤭', '+%', '--', '🤦‍♂️', '🤪', 'à', 'ér', 'ò',
                     'θ', '==', '^^', '¯\\_', '¯', '·', '»', '½', '======', '====', '===================', '_source',
                     'i', 'ii', 'iii', '̶A̶t̶l̶a̶n̶t̶a̶', 'ł', 'łł', 'ʸ', 'θsir_type', 'μm', 'υ', 'через', 'ѵ', '¡¡¡',
                     '¡¡', '¡', '¡.§¿', '¥', '¨·.·¨', '¨Planning', '¨the', '©', '«', '³', '´flatearth', '´should', '´Д',
                     '¿', 'ˊˋ', '˙', '˚.˚o', '˚', '̩̩͙', 'Ć', 'Đ', 'Ɇ', 'İ', 'Ʉ', 'Ɏ', 'μ', 'ч', 'ѵ', 'ˡˢ', 'ʷʰʸ', 'ɴʏ'}

        self.stop_words.extend(new_words)
        self.entity_temp = {}
        self.expandUrl = False
        self.stemming = None
        self.inverted_idx = {}
        self.inverted_idx_stemming = {}

    def parse_sentence(self, text,doc ,stemming):
        """
        This function tokenize, remove stop words and apply lower case for every word within the text
        :param text:
        :return:
        """
        q_text = text
        if text:
            text_tokens = []
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
                    text2 = [w for w in text2 if len(w) < 16]
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

                # rx2 = re.compile(r'[^\w\s,]')
                rx2 = re.compile(
                    r'[\U0001F300-\U0001F5FF|\U0001F600-\U0001F64F|\U0001F680-\U0001F6FF|\u2600-\u26FF\u2700-\u27BF]')
                text5 = rx2.findall(text)

                if text5:
                    text = rx2.sub("", text)

                #############################################################

                ########## for some other words #############################

                rx2 = re.compile(r"[À-ÿ]|[^\u0000-\u05C0]|_*|_\w_|[^a-zA-Z0-9\s^]")

                # rx2 = re.compile(r"[-+]?\d*\w*….?|\w*[/]\w*-?\d*|\w*\'\w*|-\w*|[À-ÿ]|,\w*|=\w*|[^\u0000-\u05C0]|[^\w]|_*|_\w_")
                text8 = rx2.findall(text)
                if text8:
                    text = rx2.sub("", text)
                # "[^\u0000-\u05C0\u2100-\u214F]
                #############################################################

                text_tokens = word_tokenize(text)
                # text_tokens=regexp_tokenize(text, pattern=r"\s|[\.,;']\d+\.\d+", gaps=True)
                text_tokens = text_tokens + text0 + text1 + text3_new + text2 + text5 + tokinzed_hatags + tokinzed_mentions
                # if not self.expandUrl:
                if text4_correct:
                    for w in text4_correct:
                        text_tokens = text_tokens + w
            except Exception as e:
                print(e)
                print("something wrong with {}", text)
        else:
            return

        if not doc:
            # steming to query
            text_tokens,text_tokens_with_stemming = self.stop_words_and_stemming(text_tokens)
            tokinzed_quote = self.parse_quotes(q_text)
            tokinzed_entity = self.get_continuous_chunks(q_text)
            text_tokens = text_tokens + tokinzed_quote + tokinzed_entity
            if stemming:
                text_tokens = text_tokens_with_stemming
                text_tokens = text_tokens + tokinzed_quote + tokinzed_entity
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

        try:
            # url_external = re.findall('http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\(\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+|www.([a-zA-Z]|[0-9]|[$-_@.&+]|[!*\(\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+', url)
            # url_full_text = re.findall('http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\(\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+|www.([a-zA-Z]|[0-9]|[$-_@.&+]|[!*\(\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+', full_text)
            rx2 = re.compile(r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-./_#?=])+|wwww\.(?:[a-zA-Z]|[0-9]|[0-9]|[$-./_#?=])+')
            url_external = rx2.findall(url)
            url_full_text = rx2.findall(full_text)

            # if text4:
            #  print(text4)

            # '{"https://t.co/22Rm2mUcaw":"https://twitter.com/i/web/status/1290360950751715329"}'
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

                # ########## Url of full text and extrnal equal #################
                # if len(url_external) == len(url_full_text):
                #     i = 0
                #     full_text = self.reaplce_url(i, full_text, url_full_text, url_external)
                #
                # ########## extrnal is bigger ##################################
                # if (len(url_external) > len(url_full_text) and len(url_full_text) > 0):
                #     i = 0
                #     full_text = self.reaplce_url(i, full_text, url_full_text, url_external)
                #     i = len(url_external) - len(url_full_text)
                #     for i in range(len(url_external)):
                #         full_text += url_external[i]
                #
                # ########## url_full_text is bigger #############################
                # if (len(url_full_text) > len(url_external) and len(url_external) > 0):
                #     i = 0
                #     for term in url_external:
                #         url_full_text = url_external[i]
                #         full_text = full_text.replace(url_full_text, term[0:len(term) - 1])
                #         i += 1
        except:
            print("something wrong with {}", tweet_id)

        # test = ' covid-19'
        # full_text = full_text + test

        tokenized_text = self.parse_sentence(full_text,True,True)
        tokinzed_quote = self.parse_quotes(full_text)
        tokinzed_entity = self.get_continuous_chunks(full_text)

        tokenized_text,tokenized_text_with_stemming = self.stop_words_and_stemming(tokenized_text)


        # enter to temp entity dic
        for entity in tokinzed_entity:
            if entity not in self.entity_temp:
                self.entity_temp[entity] = 1
            else:
                self.entity_temp[entity] += 1

        tokenized_text_with_stemming = tokenized_text_with_stemming + tokinzed_quote + tokinzed_entity
        tokenized_text = tokenized_text + tokinzed_quote + tokinzed_entity

        firstInDoc = False
        firstInDict = False

        doc_length = len(full_text)

        for term in tokenized_text:
            if term not in term_dict:
                term_dict[term] = 1
                firstInDoc = True
                doc_pos[term.lower()] = self.find_postion(full_text, term, False)
            if not firstInDoc:
                term_dict[term] += 1
                doc_pos[term.lower()] = self.find_postion(full_text, term, False)
            if term not in self.inverted_idx:
                self.inverted_idx[term] = 1
                firstInDict = True
            if not firstInDict:
                self.inverted_idx[term] += 1

        firstInDoc = False
        firstInDict = False
        full_text_stemm = full_text
        full_text_stemm = full_text_stemm.split()
        full_text_stemm = ' '.join(self.to_stemming(full_text_stemm))
        for term in tokenized_text_with_stemming:
            if term not in term_dict_with_stemming:
                term_dict_with_stemming[term] = 1
                firstInDoc = True
                doc_pos[term] = self.find_postion(full_text_stemm, term, False)
            if not firstInDoc:
                term_dict_with_stemming[term] += 1
                doc_pos[term] = self.find_postion(full_text_stemm, term, False)
            if term not in self.inverted_idx_stemming:
                self.inverted_idx_stemming[term] = 1
                firstInDict = True
            if not firstInDict:
                self.inverted_idx_stemming[term] += 1

            # TODO


        document = Document(tweet_id, tweet_date, full_text, url, retweet_text, retweet_url, quote_text,
                            quote_url, term_dict,term_dict_with_stemming, doc_length, doc_pos)
        return document

    ############ private func ##############################

    def to_stemming(self, tokenized_text):
        text_with_stemming = [self.stemming.stem_term(w) for w in tokenized_text]
        return text_with_stemming


    def stop_words_and_stemming(self, tokenized_text):
        tokenized_text_with_stemming = [self.stemming.stem_term(w) for w in tokenized_text if
                                        self.stemming.stem_term(w) not in self.stop_words]

        tokenized_text = [w for w in tokenized_text if
                          w not in self.stop_words]

        return tokenized_text,tokenized_text_with_stemming


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

    def parse_quotes(self, text):
        """
        :param text: a full text from the twitter.
        :return: quotes terms.
        'The best beer in the world'
        """
        rx2 = re.compile(r'"(?:(?:(?!(?<!\\)").)*)"')
        matches = rx2.findall(text)
        return matches

    def parse_hashtag(self, text):
        """
        :param text: a full text from the twitter.
        :return: hashtags terms split from the text.
        #stayAtHome - stay, at, home, #stayathome
        """

        hashtags_trem = []
        tag = re.findall(r'(#+\w*)', text)
        if tag:
            for term in tag:
                hashtags_trem.append(term[0] + term[1:].lower())
                hashtags_trem += [w.lower() for w in re.findall('[a-z|A-Z][^A-Z|_]*', term)]
        return hashtags_trem

    def parser_url(self, url):
        rex = re.compile(r"https?://(www\.)?")
        url = rex.sub('', url).strip().strip('/')
        url_parse = []
        if len(url) > 2:
            url_parse = re.split('[\[/:"//?={"\]]', url)
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

    def reaplce_url(self, full_text, url_full_text, url_external):
        for term in url_full_text:
            extrenal_idx = url_external[0]
            full_text = full_text.replace(term, extrenal_idx[0:len(extrenal_idx)])
        return full_text
