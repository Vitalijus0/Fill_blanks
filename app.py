import streamlit as st


import json
import requests
import string
import re
import nltk
import string
import itertools
nltk.download('stopwords')
nltk.download('wordnet')
nltk.download('punkt')
from nltk.corpus import stopwords
from nltk.corpus import wordnet
import traceback
from nltk.tokenize import sent_tokenize
from flashtext import KeywordProcessor

import pke
import spacy


from IPython.core.display import display, HTML
import xml.etree.ElementTree as et
import random

#import en_core_web_sm
#lt_core_news_sm
#nlp =spacy.load('en_core_web_sm')
nlp =spacy.load('lt_core_news_sm')

def tokenize_sentences(text):
    sentences = sent_tokenize(text)
    sentences = [sentence.strip() for sentence in sentences if len(sentence) > 20]
    return sentences



def get_noun_adj_verb(text):
    out=[]
    try:
        extractor = pke.unsupervised.MultipartiteRank()
        extractor.load_document(input=text, language='lt', spacy_model=nlp)
        #    not contain punctuation marks or stopwords as candidates.
        pos = {'ADJ', 'NOUN'}
        stoplist = list(string.punctuation)
        stoplist += ['-lrb-', '-rrb-', '-lcb-', '-rcb-', '-lsb-', '-rsb-']
        stoplist += stopwords.words('english')
        extractor.candidate_selection(pos=pos, stoplist=stoplist)
        # 4. build the Multipartite graph and rank candidates using random walk,
        #    alpha controls the weight adjustment mechanism, see TopicRank for
        #    threshold/method parameters.
        extractor.candidate_weighting(alpha=2.3,
                                      threshold=1,
                                      method='average')
        keyphrases = extractor.get_n_best(n=50)
        

        for val in keyphrases:
            out.append(val[0])
    except:
        out = []
        traceback.print_exc()

    return out



from pprint import pprint
def get_sentences_for_keyword(keywords, sentences):
    keyword_processor = KeywordProcessor()
    keyword_sentences = {}
    for word in keywords:
        keyword_sentences[word] = []
        keyword_processor.add_keyword(word)
    for sentence in sentences:
        keywords_found = keyword_processor.extract_keywords(sentence)
        for key in keywords_found:
            keyword_sentences[key].append(sentence)

    for key in keyword_sentences.keys():
        values = keyword_sentences[key]
        values = sorted(values, key=len, reverse=True)
        keyword_sentences[key] = values
    return keyword_sentences

def get_fill_in_the_blanks(sentence_mapping):
    out={"title":"Fill in the blanks for these sentences with matching words at the top"}
    blank_sentences = []
    processed = []
    keys=[]
    for key in sentence_mapping:
        if len(sentence_mapping[key])>0:
            sent = sentence_mapping[key][0]
            # Compile a regular expression pattern into a regular expression object, which can be used for matching and other methods
            insensitive_sent = re.compile(re.escape(key), re.IGNORECASE)
            no_of_replacements =  len(re.findall(re.escape(key),sent,re.IGNORECASE))
            line = insensitive_sent.sub(' _________ ', sent)
            if (sentence_mapping[key][0] not in processed) and no_of_replacements<2:
                blank_sentences.append(line)
                processed.append(sentence_mapping[key][0])
                keys.append(key)
    out["sentences"]=blank_sentences[:10]
    out["keys"]=keys[:10]
    return out

def main():
    st.title(" „Įrašykite praleistą žodį“ užduočių kūrėjas")

    st.write('Norėdami pasiūlyti pagalbą besimokant iš įvairių tekstų, pasitelkėme dirbtinį intelektą. Yra daug būdų mokytis informaciją iš teksto, o vienas iš pasitikrinti – pabandyti įrašyti praleistus esminius žodžius. Tiek dirbtinis intelektas, tiek mes mokomės teisingai suprasti lietuvių kalbą ir pateikti prasmę turinčius sakinius su trūkstamais žodžiais. Nors tai gali pasirodyti paprasta – iš tikrųjų tai yra gan sudėtinga semantinė užduotis. Prašome jūsų pagalbos testuojant prototipą')

    menu = ["Įrašyti praleistą žodį", "About"]
    choice = st.sidebar.selectbox("Menu", menu)

    if choice == "Įrašyti praleistą žodį":
        #Text area

        text = st.text_area("Įkopijuokite tekstą į langą", height=300, max_chars=5048)

        if st.button("Sukurti sakinius su trūkstamais žodžiais"):
            sentences = tokenize_sentences(text)
            #print (sentences)
            noun_verbs_adj = get_noun_adj_verb(text)
            #print ("keywords: ",noun_verbs_adj)

            keyword_sentence_mapping_noun_verbs_adj = get_sentences_for_keyword(noun_verbs_adj, sentences)
            #pprint (keyword_sentence_mapping_noun_verbs_adj)

            fill_in_the_blanks = get_fill_in_the_blanks(keyword_sentence_mapping_noun_verbs_adj)


            st.write(fill_in_the_blanks['keys'])
            st.write(fill_in_the_blanks['sentences'])


if __name__ == "__main__":
    main()