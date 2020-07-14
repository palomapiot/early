import gensim
from gensim.matutils import softcossim 
from gensim import corpora
import gensim.downloader as api
from gensim.utils import simple_preprocess
import os
import pandas as pd
import emoji
from emoji import UNICODE_EMOJI
import re

from collections import Counter, OrderedDict, defaultdict

import spacy
nlp = spacy.load('en_core_web_lg')

import nltk
from nltk.tokenize import sent_tokenize, word_tokenize, TweetTokenizer, casual_tokenize
from nltk.sentiment.vader import SentimentIntensityAnalyzer

nltk.download('punkt')
nltk.download('vader_lexicon')

import pyphen
PYPHEN_DIC = pyphen.Pyphen(lang='en')

# Download the FastText model
fasttext_model300 = api.load('fasttext-wiki-news-subwords-300')

def preprocess(author_id, comments):
    df = pd.DataFrame([[author_id, comments]], columns=['author_id', 'text'], index=[0]) 

    # cosine similarity
    documents = df['text'].iloc[0].split(":::") 
    avrg = cosine_similarity_score(documents)
    df['cosine_similarity'] = avrg

    # pos tags
    clean_text = df['text'].iloc[0].replace(':::', ' ') 
    pos = POS_tags(clean_text) 
    for i in range(len(pos_tags)):
      df[pos_tags[i]] = pos[i]
    
    ### Emojis ###
    df['face_smiling'] = face_smiling(clean_text)
    df['face_affection'] = face_affection(clean_text)
    df['face_tongue'] = face_tongue(clean_text)
    df['face_hand'] = face_hand(clean_text)
    df['face_neutral_skeptical'] = face_neutral_skeptical(clean_text)
    df['face_concerned'] = face_concerned(clean_text)
    df['monkey_face'] = monkey_face(clean_text)
    df['love'] = love(clean_text)
    df['emoji_count'] = count_emoji(clean_text)

    ### URLs / web links ###
    df['url_count'] = len(re.findall('http\S+', clean_text))

    ### Hashtag ###
    df['hash_count'] = len(re.findall('[#]', clean_text))

    ### Len of text ###
    df['text_length'] = len(clean_text)

    ### Semicolon ###
    df['semicolon_count'] = len(re.findall('[;]', clean_text))

    ### Ellipsis count ###
    df['ellipsis_count'] = len(re.findall('[...]', clean_text))

    ### SA: compound & neutral ###
    df['compound_sentiment_analysis'], df['neutral_sentiment_analysis'] = sentiment_analysis(clean_text)

    ### I, me, my ###
    df['i_me_my'] = i_me_my_count(clean_text)

    ### Word count ### 
    df['word_count'] = len(re.findall('[a-zA-Z]', clean_text))

    ### Third person pronouns & Articles ###
    df['third_person_pron_count'], df['article_count'] = articles_pron_count(clean_text)

    ### Puntuation ###
    df['space_count'] = len(re.findall(' ', clean_text))

    df['line_count'] = len(re.findall('\n', clean_text))

    df['capital_count'] = len(re.findall('[A-Z]', clean_text))

    df['digits_count'] = len(re.findall('[0-9]', clean_text))

    df['curly_brackets_count'] = len(re.findall('[\{\}]', clean_text))

    df['round_brackets_count'] = len(re.findall('[\(\)]', clean_text))

    df['square_brackets_count'] = len(re.findall('\[\]', clean_text))

    df['underscore_count'] = len(re.findall('[_]', clean_text))

    df['question_mark_count'] = len(re.findall('[?]', clean_text))

    df['exclamation_mark_count'] = len(re.findall('[!]', clean_text))

    df['dollar_mark_count'] = len(re.findall('[$]', clean_text))

    df['ampersand_mark_count'] = len(re.findall('[&]', clean_text))

    df['tag_count'] = len(re.findall('[@]', clean_text))

    df['slashes_count'] = len(re.findall('[/,\\\\]', clean_text))

    df['operator_count'] = len(re.findall('[+=\-*%<>^|]', clean_text))

    df['punc_count'] = len(re.findall('[\'\",.:;`]', clean_text))

    df['sentences_num'] = sentences_count(clean_text)

    df['repeated_alphabets'] = repeated_alphabets(clean_text)

    df['readability_score'] = readability(clean_text)

    df['word_len_mean'] = word_len_mean(clean_text)

    df['word_num_mean'] = word_num_mean(clean_text)

    return df

def cosine_similarity_score(documents):
  # Prepare a dictionary and a corpus.
  dictionary = corpora.Dictionary([simple_preprocess(doc) for doc in documents])

  # Prepare the similarity matrix
  similarity_matrix = fasttext_model300.similarity_matrix(dictionary, tfidf=None, threshold=0.0, exponent=2.0, nonzero_limit=100)

  sentences = []
  for doc in documents:
    sentences.append(dictionary.doc2bow(simple_preprocess(doc)))
  total_sum = 0
  for index, sent in enumerate(sentences):
    if (index < len(sentences) - 1):
      total_sum += softcossim(sentences[index], sentences[index + 1], similarity_matrix)
  avrg = total_sum / len(sentences)
  return avrg

all_pos_tags = ["NO_TAG", "ADJ", "ADP", "ADV","AUX", "CONJ","CCONJ","DET",
                      "INTJ","NOUN","NUM","PART","PRON","PROPN","PUNCT","SCONJ","SYM",
                      "VERB","X","EOL","SPACE"]

pos_tags = sorted(all_pos_tags)

def POS_tags(text):
    text = nlp(text)
    c = Counter()
    c.update({x:0 for x in all_pos_tags})
    pos_list = [token.pos_ for token in text]
    assert len(set(pos_list).difference(set(all_pos_tags))) == 0
    c.update(pos_list)
    c = OrderedDict(sorted(c.items(), key=lambda e: e[0]))
    return list(c.values())

### Emojis ###
def count_emoji(text):
    return len([c for c in text if c in UNICODE_EMOJI])


def face_smiling(text):
    return len([c for c in text if c in '😀😃😄😁😆😅🤣😂🙂🙃😉😊😇'])


def face_affection(text):
    return len([c for c in text if c in '🥰😍🤩😘😗☺😚😙'])


def face_tongue(text):
    return len([c for c in text if c in '😋😛😜🤪😝🤑'])


def face_hand(text):
    return len([c for c in text if c in '🤗🤭🤫🤔'])


def face_neutral_skeptical(text):
    return len([c for c in text if c in '🤐🤨😐😑😶😏😒🙄😬🤥'])


def face_concerned(text):
    return len([c for c in text if c in '😕😟🙁☹😮😯😲😳🥺😦😧😨😰😥😢😭😱😖😣😞'])


def monkey_face(text):
    return len([c for c in text if c in '🙈🙉🙊'])


def love(text):
    return len([c for c in text if c in '💋💌💘💝💖💗💓💞💕💟❣💔❤🧡💛💚💙💜🤎🖤'])

### SA ###
def sentiment_analysis(text):
  sid = SentimentIntensityAnalyzer()
  scores = sid.polarity_scores(text)
  return pd.Series([scores['compound'], scores['neu']])

def i_me_my_count(text):
  return len([c for c in text if c in ['i', 'I', 'me', 'my']])

def articles_pron_count(text):
  doc = nlp(text)
  prons = [token.lemma_ for token in doc if token.lemma_ == "-PRON-"]
  return pd.Series([len([c for c in prons if c in ['he', 'she', 'it', 'they', 
                                        'him', 'her', 'them', 
                                        'his', 'her', 'its', 'their',
                                        'hers', 'theirs',
                                        'himself', 'herself', 'itself', 'themselves', 'themself']]), 
                    len([token.lemma_ for token in doc if token.pos_ == "DET"])])

def sentences_count(tweet):
    sentences = sent_tokenize(tweet)
    return len(sentences)

def repeated_alphabets(text):
    tknzr = TweetTokenizer()
    tweet_words = tknzr.tokenize(text)
    floodings = 0
    regexpURL = re.compile(r'https?:\/\/.[^\s]*|www\.[^\s]*')
    for word in tweet_words:
        if not regexpURL.search(word) and len(re.findall(r'(\w)\1{2,}',word)) > 0: 
            floodings += 1
    return floodings

### Readability private method ###
def _words_count(tweet):
  tknzr = TweetTokenizer()
  tweet_words = tknzr.tokenize(tweet)
  return len(tweet_words), tweet_words

# Using Flesch-Kincaid readability tests (high score -> more easy to read)
def readability(text):
    totalSentences = float(sentences_count(text))
    totalTextWords, tweetWords = _words_count(text)
    totalTextWords = float(totalTextWords)
    regexpURL = re.compile(r'https?:\/\/.[^\s]*|www\.[^\s]*')
    totalSyllables = 0.0
    for word in tweetWords:
        if not regexpURL.search(word):
            hyphenated = PYPHEN_DIC.inserted(word)
            syllables = hyphenated.count("-") + 1 - hyphenated.count("--")
            totalSyllables += syllables
    if totalSentences > 0 and totalTextWords > 0:
        score = 206.835 - 1.015 * (totalTextWords/totalSentences) - 84.6 * (totalSyllables/totalTextWords)
    else:
        print("Readability issue")
        score = 0.0
    return score

def word_len_mean(text):
    words = text.split()
    return sum(len(word) for word in words) / len(words)

def word_num_mean(text):
  return sum([len(casual_tokenize(t)) for t in text]) * 1. / len(text)