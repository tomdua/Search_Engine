import re
import unicodedata
import pandas as pd

import nltk
from nltk.tag import StanfordNERTagger
from nltk import regexp_tokenize, TweetTokenizer
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize, regexp
from document import Document


class Parse:

    def __init__(self):
        self.stop_words = stopwords.words('english')
        self.tempDocuments = []

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

            ########## for fruction ##########
            rx2 = re.compile(r"[-+]?\d*\s\d+\/\d*")
            text1 = rx2.findall(text)
            if text1:
              for w in text1:
                  text=text.replace(w, '',1)
            ###############################

            ############ for numbers with point ########
            rx2 = re.compile(r'[-+]?\d+[\d.-]+\d+')
            text3 = rx2.findall(text)
            text3_new= []
            if text3:
                text3_new = [e for e in text3 if '%' not in e and e.count('.')==1]
            if text3_new:
              for w in text3_new:
                  text=text.replace(w, '',1)
            text3_new=[self.change_format(float(w)) for w in text3_new]
            ###############################################

            ############ for numbers with comma ##########
            rx2 = re.compile(r"[-+]?\d+\,*\d+\,*\d+\,*\d+")
            text2 = rx2.findall(text)
            if text2:
              for w in text2:
                  text=text.replace(w, '',1)
            text2=[self.change_format(int(w.replace(',', ''))) for w in text2]
            ###############################################

            #################### parse url #########################
            rx2 = re.compile(r'(https?://[^\s]+)')
            text4 = rx2.findall(text)
            text4_correct=[]
            if text4:
                for w in text4:
                    text = text.replace(w, '', 1)
                    text4_correct=text4_correct+self.parser_url(w)
            #######################################################


            #test=[w for w in text if any(c for c in w if unicodedata.category(c) == 'So')]

            #################### parse emoji #########################
            #rx2 = re.compile(r'[^\w\s,]')
            text5 = [w for w in text if any(c for c in w if unicodedata.category(c) == 'So')]
            text6 = [w for w in text if '\n' not in w and any(c for c in w if unicodedata.name(c).startswith("EMOJI MODIFIER"))]
            #text5_new=[]
            if text5:
                for w in text5:
                    text = text.replace(w, '', 1)
            if text6:
                for w in text6:
                    text = text.replace(w, '', 1)

                    #text4_correct = text4_correct + self.parser_url(w)
            #######################################################

            #################### hashtags ########################
            tokinzed_hatags = self.parse_hashtag(text)
            rx2 = re.compile(r'(#[^\s]+)')
            text7 = rx2.findall(text)
            #text4_correct = []
            if text7:
                for w in text7:
                    text = text.replace(w, '', 1)
            #######################################################

            #################### mentions #########################
            tokinzed_mentions = self.parse_mentions(text)
            #rx2 = re.compile(r'(@[^\s]+)')
            #text8 = rx2.findall(text)
            # text4_correct = []
            if tokinzed_mentions:
                for w in tokinzed_mentions:
                    text = text.replace(w, '', 1)
            #######################################################


            #text_tokens1 = word_tokenize(text)
            text_tokens=regexp_tokenize(text, pattern=r"\s|[\.,;']\d+\.\d+", gaps=True)
            text_tokens=text_tokens+text1+text3_new+text2+text4_correct+text5+tokinzed_hatags+tokinzed_mentions
        else:
            return
        text_tokens_without_stopwords = [w for w in text_tokens if w not in self.stop_words]
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
        # num= " #stayAtHome SectionsSEARCHSkip to contentSkip to site indexPoliticsSubscribeLog InSubscribeLog InToday's byF.B.I. Agent , in Texts, Is FiredImagePeter Strzok, a top counterintelligence agent who was taken off the special counsel investigation after his disparaging texts about President were uncovered, was fired. for and . , — , the senior counterintelligence agent who disparaged President in inflammatory text messages and helped oversee the email and investigations, has been fired for violating bureau policies, Mr. ’s lawyer said .Mr. Trump and his allies seized on the texts — exchanged during the campaign with a former lawyer, assailing the investigation"
        # full_text = full_text + num
        tokenized_text = self.parse_sentence(full_text)
        # tokinzed_hatags = self.parse_hashtag(full_text)
        # tokinzed_mentions=self.parse_mentions(full_text)
        tokinzed_queae=self.parse_queae(full_text)
        #tokinzed_entity=self.parser_entity(full_text)

        # entities = []
        # labels = []

        # sentence = nltk.sent_tokenize(full_text)
        # for sent in sentence:
        #     for chunk in nltk.ne_chunk(nltk.pos_tag(nltk.word_tokenize(sent)), binary=False):
        #         if hasattr(chunk, 'label'):
        #             entities.append(' '.join(c[0] for c in chunk))
        #             labels.append(chunk.label())
        # entities_labels = list(set(zip(entities, labels)))

        # model = 'C:/english.all.3class.distsim.crf.ser'
        # jar = 'C:/stanford-ner'
        # st = StanfordNERTagger(model, jar, encoding='utf-8')
        # tokenized_text = nltk.word_tokenize(full_text)
        # classified_text = st.tag(tokenized_text)

        # netagged_words = classified_text

        # entities = []
        # labels = []
        #
        # from itertools import groupby
        # for tag, chunk in groupby(classified_text, lambda x: x[1]):
        #     if tag != "O":
        #         entities.append(' '.join(w for w, t in chunk))
        #         labels.append(tag)


        tokenized_text=tokenized_text+tokinzed_queae

        doc_length = len(tokenized_text)
        for term in tokenized_text:
            if term not in term_dict.keys():
                term_dict[term] = 1
            else:
                term_dict[term] += 1

        document = Document(tweet_id, tweet_date, full_text, url, retweet_text, retweet_url, quote_text,
                            quote_url, term_dict, doc_length)
        self.tempDocuments=self.tempDocuments+document
        return document

    ############ private func ##############################

    def change_format(self,num):
        if num>999:
            magnitude = 0
            while abs(num) >= 1000:
                magnitude += 1
                num /= 1000.0
            # add more suffixes if you need them
            return '%.3f%s' % (num, ['', 'K', 'M', 'B', 'T', 'P'][magnitude])
        else:
            return num



    def parse_queae(self,text):
        matches = re.findall(r'\"(.+?)\"', text)
        return matches


    # def parse_phones(self,text):
    #     parse_trem=[]
    #     phones = re.findall('(?:\+ *)?\d[\d\- ]{7,}\d', text)
    #     parse_trem= ([phone.replace('-', '').replace(' ', '') for phone in phones])
    #     return parse_trem
    #
    #     # tokenize = word_tokenize(text)
    #     # smile_trem=[]
    #     # a = '1,000,000.52'
    #     # tom =  int(a.replace(',', ''))
    #     # for i in range(len(tokenize)):
    #     #     tom =re.split('[ ]', tokenize[i])
    #     #     if tokenize[i] is unicode(u"\U0001F621") or tokenize[i] is unicode(u"\U0001F620")or tokenize[i] is unicode(u"\U0001F622"):
    #     #         smile_trem.append(tokenize[i])
    #     #
    #     # return smile_trem
    #
    #     # d = r'\d{4}-\d?\d-\d?\d (?:2[0-3]|[01]?[0-9]):[0-5]?[0-9]:[0-5]?[0-9]'
    #     # print(re.findall(r'{0}.*?(?=\s*{0}|$)'.format(d), text, re.DOTALL))


    def parse_mentions (self,text):
        mentions_trem=[]
        tokenize = word_tokenize(text)
        for i in range(len(tokenize)-1):
            if tokenize[i] is '@':
                mentions_trem.append('@'+tokenize[i+1])
        return mentions_trem

    def parse_hashtag(self,text):
        hashtags = []
        hashtags_trem=[]
        patterns = '([A-Z][a-z]+)'
        tokenize = word_tokenize(text)
        for i in range(len(tokenize)-1):
            to=tokenize[i]
            if tokenize[i] is '#':
                word = tokenize[i+1]
                hashtags.append(word)

        for i in range(len(hashtags)):
            hashtags_trem.append(('#' + hashtags[i].lower()))

        for token in range(len(hashtags)):
            if '_' in hashtags[token]:
                split = hashtags[token].split('_')
                hashtags_trem.extend(word.lower() for word in split)

            else:
                split = re.sub(patterns, r' \1', re.sub('([A-Z]+)', r' \1', hashtags[token])).split()
                hashtags_trem.extend(word.lower() for word in split)


        return hashtags_trem


    """
    split and fix the terms in url
    @param terms array, temp array that insert all the word_tokenize excepet few sign
    @param tokenize
    @return array of terms from the url
    """
    def parser_url(self, url):
        terms = []
        url_terms=[]
        tokenize = word_tokenize(url)

        for token in range(len(tokenize)):
                new_token= re.split('[/\=:#?(www\.)]', tokenize[token])
                terms.extend(new_token)

        for token in range(len(terms)):
            if terms[token] is not "" and terms[token] is not '{' and terms[token] is not '}':
                url_terms.append(terms[token])
        return url_terms


    def parser_entity(self,text):
        words = nltk.word_tokenize(text)
        pos_tags = nltk.pos_tag(words)
        chunks = nltk.ne_chunk(pos_tags, binary=False)  # either NE or not NE
        entities = []
        labels = []
        mylist=[]
        for chunk in chunks:
            if hasattr(chunk, 'label'):
                # print(chunk)
                entities.append(' '.join(c[0] for c in chunk))
                labels.append(chunk.label())

        entities_labels = list(set(zip(entities, labels)))
        entities_df = pd.DataFrame(entities_labels)
        if len(entities_df) > 0 :
            entities_df.columns = ["Entities", "Labels"]
            mylist=list(dict.fromkeys(entities_df["Entities"]))

        return mylist
