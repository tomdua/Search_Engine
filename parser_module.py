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
        new_words = {"www", "^", "!", "?", "^", "&", "*", "#", "(", ")", ",", ";", ":", "{", "}", "--", "[", "]", "<",
                     ">", "|", "+", "`", "'", "."};
        for i in new_words:
            self.stop_words.append(i)
        self.entity_temp=[]
        # self.tempDocuments = []

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
        # num= " WASHINGTON -- In the wake of a string of abuses by New York police officers in the 1990s, Loretta E. Lynch, the top federal prosecutor in Brooklyn, spoke forcefully about the pain of a broken trust that African-Americans felt and said the responsibility for repairing generations of miscommunication and mistrust fell to law enforcement."
        # full_text = full_text + num
        tokenized_text = self.parse_sentence(full_text)
        # tokinzed_hatags = self.parse_hashtag(full_text)
        # tokinzed_mentions=self.parse_mentions(full_text)
        tokinzed_queae=self.parse_queae(full_text)
        #tokinzed_entity=self.parser_entity(full_text)

        tokinzed_entity=self.get_continuous_chunks(full_text)
        tokinzed_entity_new=[e for e in tokinzed_entity if len(e.split())>1]
        self.entity_temp=tokinzed_entity_new


        tokenized_text=tokenized_text+tokinzed_queae+tokinzed_entity_new

        doc_length = len(tokenized_text)
        for term in tokenized_text:
            if term not in term_dict.keys():
                term_dict[term] = 1
            else:
                term_dict[term] += 1

        document = Document(tweet_id, tweet_date, full_text, url, retweet_text, retweet_url, quote_text,
                            quote_url, term_dict, doc_length)
        # self.tempDocuments=self.tempDocuments+document
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

    def get_continuous_chunks(self,text):
        chunked = ne_chunk(pos_tag(word_tokenize(text)))
        continuous_chunk = []
        current_chunk = []
        for i in chunked:
            if type(i) == Tree:
                current_chunk.append(" ".join([token for token, pos in i.leaves()]))
            if current_chunk:
                named_entity = " ".join(current_chunk)
                if named_entity not in continuous_chunk:
                    continuous_chunk.append(named_entity)
                    current_chunk = []
            else:
                    continue
        return continuous_chunk
















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
