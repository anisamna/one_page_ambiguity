import difflib
import math
import os
import re
import string
from collections import Counter
from difflib import SequenceMatcher
from string import punctuation

import bitermplus as btm
import matplotlib.pyplot as plt
import nltk
import numpy as np
import pandas as pd
import spacy
from gensim.parsing.preprocessing import remove_stopwords
from nltk import pos_tag
from nltk.corpus import stopwords, wordnet
from nltk.parse import CoreNLPParser
from nltk.parse.corenlp import CoreNLPParser, CoreNLPServer
from nltk.stem import WordNetLemmatizer
from nltk.tokenize import TreebankWordTokenizer, sent_tokenize, word_tokenize
from nltk.tree import Tree
from numpy.linalg import norm
from scipy.sparse import csc_matrix, spdiags
from sentence_transformers import SentenceTransformer, util
from sklearn.cluster import DBSCAN
from sklearn.feature_extraction.text import CountVectorizer, TfidfVectorizer
from sklearn.metrics import euclidean_distances
from sklearn.metrics.pairwise import cosine_similarity

from inputUS.models import (
    KeywordGlossary,
    Result,
    Similarity_Analysis,
    US_Upload,
    UserStory_element,
    UserStory_What,
    UserStory_Who,
    UserStory_Why,
)

ROLE_DEL = "As an|As a|As"
ACTION_DEL = "I have to| I have| I need to| I need |I'm able to|I am able to|I want to|I want|I wish to|I can|I should be able to|I do not want|I don't want|I only want"
GOAL_DEL = "So that|so that|So|so|in order to"

CONJUNCTIONS = [" and ", "&", "\+", " or ", ">", "<", "/", "\\"]
PUNCTUATIONS = [".", ";", ":", "‒", "–", "—", "―", "‐", "-", "?", "*"]
BRACKETS = [["(", ")"], ["[", "]"], ["{", "}"], ["⟨", "⟩"]]


nlp = spacy.load("en_core_web_sm")

# Well-formed criterion


def well_formed_an(obj_id):
    well_formed_res = []

    get_UserStory_data = UserStory_element.objects.get(id=obj_id)

    status = "Well-formed criteria is not achieved !"
    # status = None
    recommendation = None
    index = 0

    if get_UserStory_data:
        index = index + 1
        # if not get_UserStory_data.Who_full and get_UserStory_data.Who_full.Who_full != '':
        if get_UserStory_data.Who_full and get_UserStory_data.Who_full.Who_full == "":
            status = "Well-formed criterion is not achieved !"
            recommendation = "Role does not found. Add role !"

        # elif not get_UserStory_data.What_full and get_UserStory_data.What_full.What_full:
        elif (
            get_UserStory_data.What_full
            and get_UserStory_data.What_full.What_full == ""
        ):
            status = "Well-formed criterion is not achieved !"
            recommendation = "Action does not found. Add action !"
        elif get_UserStory_data.Who_full and get_UserStory_data.What_full:
            if (
                get_UserStory_data.Who_full.Who_full != ""
                and get_UserStory_data.What_full.What_full != ""
            ):
                if get_UserStory_data.UserStory_Who.Who_identifier not in (
                    "As a",
                    "As an",
                    "As",
                ) or get_UserStory_data.UserStory_What.What_identifier not in (
                    "I want",
                    "I want to",
                ):
                    status = "Well-formed criterion is not achieved, potential ambiguity is not occurred !"
                else:
                    # status = 'Well-formed criterion is achieved !'
                    # recommendation = ''
                    pass

        well_formed_result = {
            "index": index,
            "userstory": get_UserStory_data.UserStory_Full_Text,
            "actor": get_UserStory_data.Who_full,
            "action": get_UserStory_data.What_full,
            "goal": get_UserStory_data.Why_full,
            "status": status,
            "recommendation": recommendation,
        }
        well_formed_res.append(well_formed_result)

    return well_formed_res


# Precise and conceptually sound criteria (use conceptually sound --> semantic)


# get word_class and the synsets for each token
def get_word_class(word):
    # for word_class, class_keywords in KeywordGlossary.items():
    # print('word', word)
    keyword_list = KeywordGlossary.objects.all()
    for keyword in keyword_list:
        for item in keyword.item_name.all():
            if word.lower() in item.Action_item:
                return item
    return None


def get_synset_class(synset):
    # for word_class, class_keywords in KeywordGlossary.items():
    #     for lemma in synset.lemma_names():
    #         if lemma.lower() in class_keywords:
    #             return word_class
    keyword_list = KeywordGlossary.objects.all()
    for keyword in keyword_list:
        for item in keyword.item_name.all():
            for lemma in synset.lemma_names():
                print("lemma", lemma)
                if lemma.lower() in item.Action_item:
                    return keyword
    return None


# additional function_check_actor_preciseness
# get data from well_formed (change this function)
def actor_precise(well_formed_res):
    role_s_values = []
    role_s_texts = []

    for well_formed in well_formed_res:
        role = well_formed["actor"]
        text = well_formed["userstory"]
        role_s_texts.append(text)
        role_s_values.append(role)

    # Vectorize the role_s values using TF-IDF
    vectorizer = TfidfVectorizer()
    X = vectorizer.fit_transform(role_s_values)

    # Apply DBSCAN clustering
    dbscan = DBSCAN(eps=0.5, min_samples=2)
    labels = dbscan.fit_predict(X)

    dic_sub = []
    # Group the role_s values and texts by their labels
    grouped_role_s = {}
    role_s_list = []

    for role_s, text, label in zip(role_s_values, role_s_texts, labels):
        if label in grouped_role_s:
            grouped_role_s[label].append((role_s, text))
        else:
            grouped_role_s[label] = [(role_s, text)]

    # Print the cluster labels and grouped role_s values
    for label, role_s_text_list in grouped_role_s.items():
        for role_s, text in role_s_text_list:
            if label != -1 and role_s not in role_s_list:
                role_s_list.append(role_s)  # Append role_s to the list
            dic_sub.append(
                {
                    "index": well_formed_res["index"],
                    "userstory": text,
                    "actor": role_s,
                    "cluster_label": label,
                    "role_s_list": role_s_list,  # Add role_s_list to the dictionary
                }
            )
    return dic_sub


# def classify_sentence(well_formed_list=[], element_type="ACTION"):
def classify_sentence(well_formed_res):
    sentence_classifications = []
    keyword_to_sentence_class = {}

    for well_formed in well_formed_res:
        text = well_formed["userstory"]
        role = well_formed["actor"]
        action = well_formed["action"]

        doc = nlp(action)

        sentence_class = set()
        keyword_words = set()

        for token in doc:
            if token.pos_ == "VERB":
                word_class = get_word_class(token.text)
                if word_class:
                    sentence_class.add(word_class)
                    keyword_words.add(token.text)

                    for keyword_word in keyword_words:
                        if keyword_word not in keyword_to_sentence_class:
                            keyword_to_sentence_class[keyword_word] = set()
                        keyword_to_sentence_class[keyword_word].add(word_class)
                else:
                    synsets = wordnet.synsets(token.text)
                    for synset in synsets:
                        synset_class = get_synset_class(synset)

                        if synset_class:
                            sentence_class.add(synset_class)
                            keyword_words.add(token.text)

                            for keyword_word in keyword_words:
                                if keyword_word not in keyword_to_sentence_class:
                                    keyword_to_sentence_class[keyword_word] = set()
                                keyword_to_sentence_class[keyword_word].add(
                                    synset_class
                                )

        labels = []
        sentence_classify = {
            "index": well_formed_res["index"],
            "userstory": text,
            "role": role,
            "action": action,
            "sentence_class": list(sentence_class),
            "keyword_words": {
                keyword_word: list(keyword_to_sentence_class[keyword_word])
                for keyword_word in keyword_words
            },
            "label": "",
        }

        for key, value in sentence_classify["keyword_words"].items():
            num_items = len(value)

            if not num_items:
                sentence_classify["label"] = "0"
            elif num_items > 1:
                sentence_classify["label"] = ">1"
            elif num_items == 1:
                sentence_classify["label"] = "1"

        sentence_classifications.append((sentence_classify))
    return sentence_classifications


def stat_preciseness(dic_sub, sentence_classifications):
    cluster_texts = {}
    preciseness = []

    status = ""
    recommendation = ""

    for act in sentence_classifications:
        for sub in dic_sub:
            if act["userstory"] == sub["userstory"]:
                if sub["cluster_label"] == -1 and act["label"] == "":
                    status = "The user story lacks conceptual clarity which might result in vagueness problems. Please change the subject (role) and the predicate (word of action) !"
                    recommendation = "Change the subject (role) and the predicate (word of action) using the standard terminology"
                    recommendation_name_user = sub["role_s_list"]
                    recommendation_name_action = "Sorry. We dont have recommendation for the action. Try to rewrite user stories."
                elif sub["cluster_label"] == -1 and act["label"] == "1":
                    status = "The user story lacks conceptual clarity which might result in vagueness problems. Please change the subject (role) !"
                    recommendation = (
                        "Change the subject (role) using the standard terminology"
                    )
                    recommendation_name_user = sub["role_s_list"]
                    recommendation_name_action = ""
                elif sub["cluster_label"] == -1 and act["label"] == ">1":
                    status = "The user story lacks conceptual clarity which might result in inconsistency problems. Please change the subject (role) and the predicate (word of action) !"
                    recommendation = "Change the subject (role) and the predicate (word of action) using the standard terminology."
                    recommendation_name_user = sub["role_s_list"]
                    recommendation_name_action = act["keyword_words"]
                elif sub["cluster_label"] != -1 and act["label"] == "":
                    status = "The user story lacks conceptual clarity which might result in vagueness problems. Please change the predicate (word of action) !"
                    recommendation = "Change the predicate (word of action) using the standard terminology"
                    recommendation_name_user = ""
                    recommendation_name_action = "Sorry. We dont have recommendation for the action. Try to rewrite user stories."
                elif sub["cluster_label"] != -1 and act["label"] == "1":
                    # status = "Preciseness criterion is achieved. User story is good."
                    # recommendation = "pass"
                    continue
                elif sub["cluster_label"] != -1 and act["label"] == ">1":
                    status = "The user story lacks conceptual clarity which might result in inconsistency problems. Please change the subject (role) and the predicate (word of action) !"
                    recommendation = "Change the subject (role) and the predicate (word of action) using the standard terminology"
                    recommendation_name_user = ""
                    recommendation_name_action = act["keyword_words"]

                sub["status"] = status
                sub["recommendation"] = recommendation
                sub["recommendation_name_user"] = recommendation_name_user
                act["recommendation_name_action"] = recommendation_name_action

                cluster_texts = {
                    "index": sub["index"],
                    "text": sub["text"],
                    "role_actor": sub.get("actor"),
                    "action_act": act.get("act_action"),
                    "role_label": sub["cluster_label"],
                    "std_role": sub["role_s_list"],
                    "std_term": act["keyword_words"],
                    "act_label": act["label"],
                    "status": sub["status"],
                    "rekom": sub["recommendation"],
                    "rekom_for_actor": sub["recommendation_name_user"],
                    "rekom_for_action": act["recommendation_name_action"],
                }

                preciseness.append(cluster_texts)
    return preciseness
