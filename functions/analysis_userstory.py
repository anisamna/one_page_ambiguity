import gc
import os
import random
import re
import string
from collections import Counter, defaultdict

import bitermplus as btm
import numpy as np
import spacy
import torch
from nltk import Tree, pos_tag, word_tokenize
from nltk.corpus import stopwords, wordnet
from nltk.parse import CoreNLPParser
from nltk.stem import WordNetLemmatizer
from sentence_transformers import SentenceTransformer, util
from sklearn.cluster import DBSCAN
from sklearn.feature_extraction.text import TfidfVectorizer

from inputUS.models import (
    Glossary,
    KeywordGlossary,
    ReportTerms,
    ReportUserStory,
    Role,
    UserStory_element,
)


class AnalysisData:
    # 1. well-formed
    # 2. atomicity
    # 3. preciseness
    # 4. consistency / consistent
    # 5. conceptually sound
    # 6. uniqueness
    def __init__(
        self,
        userstory_list_id=[],
        eps=0.5,
        min_samples=2,
        terms_role=5,
        terms_action=7,
        topics=10,
        similarity=None,
        user=None,
    ):
        self.eps = float(eps) if eps else 0.5
        self.min_samples = float(min_samples) if min_samples else 2
        self.terms_role = float(terms_role) if terms_role else 5
        self.terms_action = float(terms_action) if terms_action else 7
        self.topics = int(topics) if topics else 10
        self.similarity = float(similarity) if similarity else None
        self.userstory_list = userstory_list_id
        self.user = user
        core_nlp_parser_url = os.environ.get("CORE_NLP_URL", "localhost")
        core_nlp_parser_port = os.environ.get("CORE_NLP_PORT", 9000)
        self.corenlp_parser = CoreNLPParser(
            url=f"http://{core_nlp_parser_url}:{core_nlp_parser_port}"
        )
        self.nlp = spacy.load("en_core_web_sm")
        # Precise criteria
        self.keywords = {
            "create": [
                "add",
                "insert",
                "create",
                "make",
                "build",
                "develop",
                "establish",
                "generate",
                "construct",
            ],
            "read": [
                "view",
                "read",
                "display",
                "show",
                "retrieve",
                "get",
                "access",
                "examine",
                "browse",
            ],
            "update": [
                "modify",
                "edit",
                "change",
                "update",
                "revise",
                "alter",
                "adjust",
                "adapt",
                "refine",
                "fix",
                "improve",
                "renew",
                "replace",
            ],
            "delete": [
                "remove",
                "delete",
                "erase",
                "clear",
                "eliminate",
                "exclude",
                "discard",
                "purge",
                "drop",
            ],
            "merge": ["bind", "export", "integrate", "invite", "link", "list", "offer"],
            "validate": ["check", "evaluate", "test", "verify"],
            "search": ["investigate", "inquire", "research", "search"],
        }

    def save_report(self, userstory, status, type, data={}, is_problem=False):
        # print(f'\n{userstory}')
        # print(status)
        # print(data)
        # print(is_problem)
        report, created = ReportUserStory.objects.get_or_create(
            userstory=userstory, status=status, type=type
        )
        for key, value in data.items():
            setattr(report, key, value)
        if self.user:
            report.created_by = self.user
        report.is_problem = is_problem
        report.save()

        if userstory:
            userstory.is_processed = True
            userstory.is_problem = is_problem
            userstory.save()
        return report

    def start(self):
        # 1. well-formed
        self.well_formed_data = self.well_formed()
        # print("well_formed", self.well_formed_data)
        for item in self.well_formed_data:
            self.save_report(
                item["userstory_obj"],
                item["status"],
                ReportUserStory.ANALYS_TYPE.WELL_FORMED,
                {
                    "recommendation": item["recommendation"],
                },
                item["is_problem"],
            )

        # # 2. atomicity
        self.atomic_data = self.atomicity_stat()
        for item in self.atomic_data:
            description = None
            userstory = item["userstory_obj"]
            childs = userstory.get_childrens()
            sbar_label = item.get("sbar_label", None)
            recommendation = item["atomicity_recommendation"]
            if sbar_label:
                if sbar_label == 1:
                    recommendation += f"\n\nSubordinate conjunction that could trigger semantic ambiguity: ** {item['sbar_text']} **"
            if childs.exists():
                description = ""
                for index, child in enumerate(childs):
                    description += (
                        f"User Story #{index+1}: {child.UserStory_Full_Text}\n\n"
                    )
            self.save_report(
                item["userstory_obj"],
                item["atomicity_status"],
                ReportUserStory.ANALYS_TYPE.ATOMICITY,
                {
                    "recommendation": recommendation,
                    "description": description,
                },
                item["atomicity_is_problem"],
            )

        # # 3. preciseness
        self.preciseness_data = self.running_preciseness()

        # # 4. consistency / consistent
        self.running_stat_consistency()

        # # 5. conceptually sound
        self.stat_conceptually_sound()

        # # 6. uniqueness
        self.stat_uniqueness_criteria()
        gc.collect()
        torch.cuda.empty_cache()

    # ============ Well Formed ============
    def well_formed(self):
        print("\n============ Start Well Formed ============\n")

        well_formed_res = []
        status = "Well-formed criteria is not achieved !"
        recommendation = None
        index = 0

        for userstory_id in self.userstory_list:
            index += 1
            try:
                userstory = UserStory_element.objects.get(id=userstory_id)
            except UserStory_element.DoesNotExist:
                pass
            else:
                # Role: Who
                # Action: What
                # Goal: Why
                # print(f'\n{userstory}')
                # print('userstory.Who_full', userstory.Who_full)
                # print('userstory.What_full', userstory.What_full)

                is_problem = False

                if userstory.Who_full and userstory.What_full:
                    Who_full = userstory.Who_full
                    What_full = userstory.What_full
                    if (
                        Who_full.Who_identifier != ""
                        and Who_full.Who_action != ""
                        and What_full.What_identifier != ""
                        and What_full.What_action != ""
                    ):
                        Who_identifier = Who_full.Who_identifier.lower()
                        What_identifier = What_full.What_identifier.lower()
                        if Who_identifier not in (
                            "as an",
                            "as a",
                            "as",
                        ) or What_identifier not in ("i want", "i want to"):
                            status = "Well-formed criteria is not achieved, anbiguity does not exist !"
                            is_problem = True
                        else:
                            status = (
                                "Well-formed criteria is achieved! User story is fine"
                            )
                    elif (
                        Who_full.Who_identifier == ""
                        and Who_full.Who_action == ""
                        and What_full.What_identifier != ""
                        and What_full.What_action != ""
                    ):
                        status = "Well-formed is not achieved ! WHO segment is not not found !"
                        recommendation = "Rewrite user story in Connextra format: *As a <role>, I want <action>, so that <goal>*"
                        is_problem = True
                    elif (
                        Who_full.Who_identifier == ""
                        and Who_full.Who_action != ""
                        and What_full.What_identifier != ""
                        and What_full.What_action != ""
                    ):
                        status = "Well-formed is achieved ! WHO segment is not complete. WHO identifier does not found !"
                        recommendation = "Rewrite user story in Connextra format: *As a <role>, I want <action>, so that <goal>*"
                        is_problem = True
                    elif (
                        Who_full.Who_identifier != ""
                        and Who_full.Who_action != ""
                        and What_full.What_identifier == ""
                        and What_full.What_action != ""
                    ):
                        status = "Well-formed is achieved ! WHAT segment is not complete. WHAT identifier does not found !"
                        recommendation = "Rewrite user story in Connextra format: *As a <role>, I want <action>, so that <goal>*"
                        is_problem = True
                    elif (
                        Who_full.Who_identifier != ""
                        and Who_full.Who_action != ""
                        and What_full.What_identifier == ""
                        and What_full.What_action == ""
                    ):
                        status = "Well-formed is not achieved ! WHAT segment is not not found !"
                        recommendation = "Rewrite user story in Connextra format: *As a <role>, I want <action>, so that <goal>*"
                        is_problem = True

                well_formed_result = {
                    "index": index,
                    "userstory_obj": userstory,
                    "userstory": userstory.UserStory_Full_Text,
                    "actor": userstory.Who_full,
                    "action": userstory.What_full,
                    "goal": userstory.Why_full,
                    "status": status,
                    "recommendation": recommendation,
                    "is_problem": is_problem,
                }
                well_formed_res.append(well_formed_result)
        return well_formed_res

    # ============ Atomicity ============
    def get_pos_label(self, token):
        pos_tags = pos_tag([token])
        return pos_tags[0][1]

    def cek_user_story(self):
        if len(self.well_formed_data) > 0:
            index = 0
            well_formed_res = []
            for well_formed in self.well_formed_data:
                index += 1
                # print(well_formed)
                actor = well_formed.get("actor", None)
                action = well_formed.get("action", None)
                goal = well_formed["goal"]
                text = well_formed["userstory"]
                if actor and action:
                    if (
                        actor.Who_identifier
                        and actor.Who_action
                        and action.What_identifier
                        and action.What_action
                    ):
                        if "so" in action.What_action:
                            # check if "so" is part of token
                            token = word_tokenize(action.What_action)
                            if "so" not in token:
                                pass
                            else:
                                status = "Goal is detected..."
                                s_action_user_part = s_action_user.split("so")
                                action_text = (
                                    "I want to " + s_action_user_part[0].strip()
                                )
                                s_action_user = s_action_user_part[1].strip()

                                # Update the corresponding rows in df_segment and df_element
                                # well_formed_res.append({
                                #     "index": index,
                                #     "userstory": text,
                                # })
                                # well_formed.update({
                                # })
                                action.What_action = s_action_user
                                action.What_full = action_text
                                action.save()

                                well_formed.update({"action": action})
                well_formed_res.append(well_formed)
            return well_formed_res

    def find_sbar(self):
        act_sbar = []
        if len(self.well_formed_data) > 0:
            index = 0
            for well_formed in self.well_formed_data:
                index += 1
                actor = well_formed["actor"]
                action = well_formed["action"]
                goal = well_formed["goal"]
                text = well_formed["userstory"]

                if actor and action:
                    if (
                        actor.Who_identifier
                        and actor.Who_action
                        and action.What_identifier
                        and action.What_action
                    ):
                        tokens_action = word_tokenize(action.What_action)
                        parsed_sentence_action = next(
                            self.corenlp_parser.parse(tokens_action)
                        )

                        root = None

                        # Accessing the dependencies
                        for subtree in parsed_sentence_action.subtrees():
                            if subtree.label() == "ROOT":
                                root = subtree
                                break

                        dependency_pairs = []
                        sbar_text = []

                        # detect SBAR
                        for subtree in parsed_sentence_action.subtrees():
                            if subtree.label() == "ROOT":
                                root = subtree
                            elif subtree.label() == "SBAR":
                                sbar_text = subtree.leaves()

                        for child in root:
                            if isinstance(child, Tree):
                                if child.label() != "PUNCT":
                                    dependency_pairs.append(
                                        (child[0], child.label(), root[0])
                                    )
                            else:
                                dependency_pairs.append((child, "punct", root[0]))

                        new_text = text
                        if sbar_text:
                            sbar_text_joined = " ".join(sbar_text)
                            sbar_start_index = text.find(sbar_text_joined)
                            if sbar_start_index >= 0:
                                sbar_end_index = sbar_start_index + len(
                                    sbar_text_joined
                                )
                                if sbar_end_index == len(text):
                                    new_text = text[:sbar_start_index].strip()
                                else:
                                    new_text = (
                                        text[:sbar_start_index] + text[sbar_end_index:]
                                    ).strip()

                        # Capture text after "I want to" or "I want" until the next comma
                        match = re.search(
                            r"I\s+want\s+to|I\s+want", new_text, re.IGNORECASE
                        )
                        # print(match)
                        captured_text = ""
                        if match:
                            start_index = match.end()
                            comma_index = new_text.find(",", start_index)
                            if comma_index != -1:
                                captured_text = new_text[start_index:comma_index]
                            else:
                                captured_text = new_text[start_index:]

                        # Remove whitespace and special characters from new_text
                        cleaned_text = re.sub(r"\s+|[^\w\s]", " ", captured_text)

                        # Check if the last token in new_text is a verb
                        pos_tags = pos_tag(word_tokenize(captured_text))
                        if pos_tags:
                            last_token, last_pos = pos_tags[-1]
                            is_last_token_verb = last_pos.startswith("VB")

                            if is_last_token_verb:
                                last_token_verb = "verb active"
                            elif last_pos == "VBD":
                                last_token_verb = "verb passive"
                            else:
                                last_token_verb = "not a verb"
                        else:
                            last_token, last_pos = None, None
                            is_last_token_verb = False
                            last_token_verb = "no tokens"

                        # define dic_atomicity
                        dic_conciseness = {
                            "index": index,
                            "text": text,
                            "userstory_obj": well_formed["userstory_obj"],
                            "action_user": action.What_action,
                            "sbar_text": " ".join(sbar_text),
                            "removable_sbar_text": new_text,
                            "captured_text": captured_text,
                            "is_last_token_a_verb": is_last_token_verb,
                        }
                        act_sbar.append(dic_conciseness)
        return act_sbar

    def find_cc(self, act_sbar):
        atomic = []
        for item in act_sbar:
            text = item["text"]
            action_user = item["action_user"]
            sbar_text = item["sbar_text"]
            text_tanpa_SBAR = item["removable_sbar_text"]
            capt_text = item["captured_text"]
            is_last_token_a_verb = item["is_last_token_a_verb"]

            cc_found = False
            ambiguous = False
            status = ""
            cc_stat = ""
            cc_label = ""
            sbar_stat = ""
            sbar_label = ""
            captured_text = ""

            if sbar_text == "":
                sbar_text = "No SBAR in this user story"
                text_tanpa_SBAR = "No SBAR in this user story"
                captured_text = "No SBAR in this user story"
                sbar_stat = "No SBAR in this user story"
                sbar_label = 0

                # cari CC di dalam token
                tokens = action_user.split()
                len_tokens = len(tokens)
                for token in tokens:
                    pos_label = self.get_pos_label(token)
                    if self.get_pos_label(token) == "CC":
                        cc_stat = "CC is found"
                        cc_label = 1
                        break
                    else:
                        cc_stat = "CC is not found"
                        cc_label = 0
            else:
                sbar_stat = "There is SBAR in this user story"
                sbar_label = 1

                # cari CC di dalam token
                tokens = capt_text.split()
                for token in tokens:
                    pos_label = self.get_pos_label(token)
                    if pos_label == "CC":
                        cc_stat = "CC is found"
                        cc_label = 1
                        break
                    else:
                        cc_stat = "CC is not found"
                        cc_label = 0
            # define dic_atomic
            dic_atomicity = {
                "text": text,
                "userstory_obj": item["userstory_obj"],
                "action_user": action_user,
                "sbar_text": sbar_text,
                "text_without_sbar": text_tanpa_SBAR,
                "new_text_wth_sbar": captured_text,
                "is_last_token_a_verb": is_last_token_a_verb,
                "cc_status": cc_stat,
                "sbar_status": sbar_stat,
                "cc_label": cc_label,
                "sbar_label": sbar_label,
            }
            atomic.append(dic_atomicity)
        return atomic

    def atomicity_stat(self):
        print("\n============ Start Atomicity ============\n")
        data = self.cek_user_story()
        self.well_formed_data = data
        act_sbar = self.find_sbar()
        atomic = self.find_cc(act_sbar)

        atomicity_ambiguity = []
        atomicity_amb_status = ""
        atomicity_amb_recommendation = ""

        for sbar_item in act_sbar:
            for atomic_item in atomic:
                atomicity_amb_is_problem = False
                if sbar_item["text"] == atomic_item["text"]:
                    if atomic_item["sbar_label"] == 0 and atomic_item["cc_label"] == 0:
                        # line kedua dijadikan recommendation
                        atomicity_amb_status = "User story meet conciseness and atomicity criteria and does not ambiguous."
                        atomicity_amb_recommendation = "User story is fine !"
                    elif (
                        atomic_item["sbar_label"] == 0 and atomic_item["cc_label"] == 1
                    ):
                        if sbar_item["is_last_token_a_verb"] == True:
                            # atomicity_amb_status = "User story meet conciseness but not atomicity criteria."
                            atomicity_amb_status = "User story meet conciseness but does not meet atomicity criteria."
                            atomicity_amb_recommendation = "User story is ambiguous. It is recommended to split user story !"
                            atomicity_amb_is_problem = True
                        else:
                            # atomicity_amb_status = "User story meet conciseness but not atomicity criteria."
                            atomicity_amb_status = "User story meet conciseness but does not meet atomicity criteria."
                            atomicity_amb_recommendation = "User story is not ambiguos ! However, it is recommended to split user story !"
                            atomicity_amb_is_problem = False
                    elif (
                        atomic_item["sbar_label"] == 1 and atomic_item["cc_label"] == 0
                    ):
                        atomicity_amb_status = "User story does not meet conciseness but meet atomicity criteria."
                        atomicity_amb_recommendation = "User story is not ambiguous ! However, it is recommended to remove subordinate conjunction !"
                        atomicity_amb_is_problem = True
                    elif (
                        atomic_item["sbar_label"] == 1 and atomic_item["cc_label"] == 1
                    ):
                        if sbar_item["is_last_token_a_verb"] == True:
                            atomicity_amb_status = "User story does not meet conciseness and atomicity criteria."
                            atomicity_amb_recommendation = "\nUser story is potentially ambiguous. It is recommended to change user story structure and split it !"
                            atomicity_amb_is_problem = True
                        else:
                            atomicity_amb_status = "User story does not meet conciseness and atomicity criteria."
                            atomicity_amb_recommendation = "User story is not ambiguous ! However, it is recommended to remove subordinate conjunction and split it !"
                            atomicity_amb_is_problem = True

                    atomic_item["atomicity_status"] = atomicity_amb_status
                    atomic_item[
                        "atomicity_recommendation"
                    ] = atomicity_amb_recommendation
                    atomic_item["atomicity_is_problem"] = atomicity_amb_is_problem
                    dic_atom_concise = {
                        "index": sbar_item["index"],
                        "userstory_obj": sbar_item["userstory_obj"],
                        "text": sbar_item["text"],
                        "action_user": sbar_item["action_user"],
                        "text_without_sbar": sbar_item["removable_sbar_text"],
                        "last_token_verb_or_not": sbar_item["is_last_token_a_verb"],
                        "sbar_text": sbar_item["sbar_text"],
                        "cc_label": atomic_item["cc_label"],
                        "sbar_label": atomic_item["sbar_label"],
                        "atomicity_status": atomic_item["atomicity_status"],
                        "atomicity_recommendation": atomic_item[
                            "atomicity_recommendation"
                        ],
                        "atomicity_is_problem": atomic_item["atomicity_is_problem"],
                    }
                    atomicity_ambiguity.append(dic_atom_concise)
        return atomicity_ambiguity

    # ============ Precise Criteria ============
    def get_word_class(self, word):
        # for word_class, class_keywords in self.keywords.items():
        #     if word.lower() in class_keywords:
        #         return word_class
        if word:
            keyword_list = KeywordGlossary.objects.filter(
                item_name__Action_item=word.lower()
            )
            return keyword_list.last()
        return None

    def get_synset_class(self, synset):
        # for word_class, class_keywords in self.keywords.items():
        #     for lemma in synset.lemma_names():
        #         if lemma.lower() in class_keywords:
        #             return word_class
        if synset:
            for lemma in synset.lemma_names():
                keyword_list = KeywordGlossary.objects.filter(
                    item_name__Action_item=lemma.lower()
                )
                return keyword_list.last()
        return None

    def actor_precise(self):
        role_s_values = []
        role_s_texts = []
        userstory_values = []

        # for index, row in df_segment.iterrows():
        #     text = row['UserStory']
        #     role = row['Role_user']
        #     role_s_texts.append(text)
        #     role_s_values.append(role)
        for item in self.well_formed_data:  # ganti menggunakan well formed data
            role_s_values.append(item["actor"].Who_action)
            role_s_texts.append(item["userstory"])
            userstory_values.append(item["userstory_obj"])

        # Vectorize the role_s values using TF-IDF
        vectorizer = TfidfVectorizer()
        X = vectorizer.fit_transform(role_s_values)

        # Apply DBSCAN clustering
        dbscan = DBSCAN(eps=self.eps, min_samples=int(self.min_samples))
        labels = dbscan.fit_predict(X)
        dic_sub = []
        # Group the role_s values and texts by their labels
        grouped_role_s = {}
        role_s_list = []
        for role_s, text, userstory, label in zip(
            role_s_values, role_s_texts, userstory_values, labels
        ):
            if label in grouped_role_s:
                grouped_role_s[label].append((role_s, text, userstory))
            else:
                grouped_role_s[label] = [(role_s, text, userstory)]
        # Print the cluster labels and grouped role_s values
        index = 0
        for label, role_s_text_list in grouped_role_s.items():
            for role_s, text, userstory in role_s_text_list:
                if label != -1 and role_s not in role_s_list:
                    role_s_list.append(role_s)  # Append role_s to the list
                dic_sub.append(
                    {
                        "index": index + 1,
                        "text": text,
                        "userstory": userstory,
                        "actor": role_s,
                        "cluster_label": label,
                        "role_s_list": role_s_list,  # Add role_s_list to the dictionary
                    }
                )
        return dic_sub

    def classify_sentence(self):
        sentence_classifications = []
        keyword_to_sentence_class = {}

        index = 0
        for item in self.well_formed_data:  # ganti menggunakan well form data
            text = item.get("userstory")
            action = item.get("action").What_action
            doc = self.nlp(action)
            sentence_class = set()
            keyword_words = set()
            for token in doc:
                if token.pos_ == "VERB":
                    word_class = self.get_word_class(token.text)
                    if word_class:
                        sentence_class.add(word_class.keyword)
                        keyword_words.add(token.text)
                        for keyword_word in keyword_words:
                            if keyword_word not in keyword_to_sentence_class:
                                keyword_to_sentence_class[keyword_word] = set()
                            keyword_to_sentence_class[keyword_word].add(
                                word_class.keyword
                            )
                    else:
                        synsets = wordnet.synsets(token.text)
                        for synset in synsets:
                            synset_class = self.get_synset_class(synset)
                            if synset_class:
                                sentence_class.add(synset_class.keyword)
                                keyword_words.add(token.text)
                                for keyword_word in keyword_words:
                                    if keyword_word not in keyword_to_sentence_class:
                                        keyword_to_sentence_class[keyword_word] = set()
                                    keyword_to_sentence_class[keyword_word].add(
                                        synset_class.keyword
                                    )

            labels = []
            sentence_classify = {
                "index": index + 1,
                "sentence": text,
                "act_action": action,
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

    def stat_preciseness(self):
        print("\n============ Start Precise Criteria ============\n")
        sentence_classifications = self.classify_sentence()
        dic_sub = self.actor_precise()

        cluster_texts = {}
        preciseness = []

        status = ""
        recommendation = ""
        for act in sentence_classifications:
            for sub in dic_sub:
                if act["sentence"] == sub["text"]:
                    is_problem = False
                    if sub["cluster_label"] == -1 and act["label"] == "":
                        status = (
                            "Preciseness criterion does not achieved."
                            "\nUser role and word of action are not precise."
                            "\nUser story is potentially ambiguous. Vagueness problem may occur!"
                        )
                        recommendation = "Change the user role and the action using the standard terminology"
                        is_problem = True
                    elif sub["cluster_label"] == -1 and act["label"] == "1":
                        status = (
                            "Preciseness criterion is not achieved."
                            "\nUser role is not precise. User story is potentially ambiguous!"
                        )
                        recommendation = (
                            "Change the user role using the standard terminology"
                        )
                        is_problem = True
                    elif sub["cluster_label"] == -1 and act["label"] == ">1":
                        status = (
                            "Preciseness criterion is not achieved."
                            "\nUser role and word of action are not precise."
                            "\nUser story is potentially ambiguous. Inconsistency problem may occur!"
                        )
                        recommendation = "Change the user role and word of action using the standard terminology."
                        is_problem = True
                    elif sub["cluster_label"] != -1 and act["label"] == "":
                        status = (
                            "Preciseness criterion does not achieved."
                            "\nWord of action is not precise."
                            "\nUser story is potentially ambiguous. Vagueness problem may occur!"
                        )
                        recommendation = (
                            "Change the action using the standard terminology"
                        )
                        is_problem = True
                    elif sub["cluster_label"] != -1 and act["label"] == "1":
                        status = (
                            "Preciseness criterion is achieved. User story is good."
                        )
                        recommendation = "pass"
                    elif sub["cluster_label"] != -1 and act["label"] == ">1":
                        status = (
                            "Preciseness criteria does not achieved."
                            "\nWord of action is not precise. User story is potentially ambiguous. Inconsistency problem may occur!"
                        )
                        recommendation = "Change the user role and the action using the standard terminology."
                        is_problem = True
                    sub["status"] = status
                    sub["recommendation"] = recommendation
                    sub["is_problem"] = is_problem

                    cluster_texts = {
                        "index": sub["index"],
                        "userstory": sub["userstory"],
                        "text": sub["text"],
                        "role_actor": sub.get("actor"),
                        "action_act": act.get("act_action"),
                        "role_label": sub["cluster_label"],
                        "std_role": sub["role_s_list"],
                        "std_term": act["keyword_words"],
                        "act_label": act["label"],
                        "status": sub["status"],
                        "recommendation": sub["recommendation"],
                        "is_problem": sub["is_problem"],
                    }

                    preciseness.append(cluster_texts)

        return preciseness, sentence_classifications, dic_sub

    def running_preciseness(self):
        print("\n== Preciseness criterion analysis - finding lexical ambiguity: ==")
        preciseness, sentence_classifications, dic_sub = self.stat_preciseness()
        for sc in preciseness:
            Text = sc["text"]
            userstory = sc["userstory"]
            is_problem = sc["is_problem"]
            # Finding the corresponding dictionary in "dic_sub" using "text" key
            matching_sub = next((sub for sub in dic_sub if sub["text"] == Text), None)
            matching_act = next(
                (act for act in sentence_classifications if act["sentence"] == Text),
                None,
            )
            if matching_sub or matching_act:
                if Text and userstory:
                    # Accessing "actor" key from the "matching_sub" dictionary in "dic_sub"
                    # print("Story #", matching_act["index"], ": ", Text)
                    # print("Role:", matching_sub["actor"])
                    # print("Action:", matching_act["act_action"])
                    # print("Status:", matching_sub["status"])
                    # print("Recommendation:", matching_sub["recommendation"])

                    description = f"""Role: {matching_sub["actor"]}
                                    Action: {matching_act["act_action"]}"""

                    recommendation = matching_sub["recommendation"]
                    recommendation_type = None

                    if (
                        matching_sub["cluster_label"] == -1
                        and matching_act["label"] != "1"
                    ):
                        # print("Recommended terms: ")
                        # Perubahan disini, identify problematic terms in role and action, give recommended terms for role and actions
                        # print("Problematic terms:")

                        recommendation += "\n\nProblematic terms:\n\n"

                        if (
                            matching_sub["cluster_label"] == -1
                            and matching_act["label"] == ""
                        ):
                            # print(
                            #     "Recommendation for the user are:",
                            #     matching_sub["role_s_list"],
                            # )
                            # print(
                            #     "Recommendation for the action are: Sorry. We do not have recommendation for the action. The action is too vague."
                            # )
                            # recommendation += f"""Recommendation for the user are:
                            #     {matching_sub["role_s_list"]}
                            #     Recommendation for the action are: Sorry. We do not have recommendation for the action. The action is too vague.
                            # """
                            # ini untuk mengambil data role, bisa diambil dari Who_actor table Who
                            # print("Role:", matching_sub["actor"])
                            # ini diambil dari role_s_list, data disimpan di tabel baru (ato gausah disimpan?) dengan nama role
                            # print(
                            #     "Recommendation terms for the user:",
                            #     matching_sub["role_s_list"],
                            # )
                            # print(
                            #     "Recommendation terms for the action: Sorry. We do not have recommendation for the action. The action is too vague."
                            # )

                            if matching_sub["role_s_list"] and len(
                                matching_sub["role_s_list"]
                            ):
                                for role_item in matching_sub["role_s_list"]:
                                    role_key = role_item.strip().lower()
                                    role_, created = Role.objects.get_or_create(
                                        role_key=role_key,
                                        userstory=userstory,
                                        status=ReportUserStory.ANALYS_TYPE.PRECISE,
                                    )
                                    role_.role = role_item
                                    role_.save()

                            recommendation += f"""Role: {matching_sub["actor"]}\n
                            Recommendation terms for the user: {matching_sub["role_s_list"]}\n
                            Recommendation terms for the action: Sorry. We do not have recommendation for the action. The action is too vague.\n
                            """
                            recommendation_type = (
                                ReportUserStory.RECOMENDATION_TYPE.ROLE
                            )
                        elif (
                            matching_sub["cluster_label"] == -1
                            and matching_act["label"] == ">1"
                        ):
                            # print(
                            #     "Recommendation for the user are:",
                            #     matching_sub["role_s_list"],
                            # )
                            # print(
                            #     "Recommendation for the action are:",
                            #     matching_act["keyword_words"],
                            # )
                            # recommendation += f"""Recommendation for the user are:
                            #     {matching_sub["role_s_list"]}
                            #     Recommendation for the action are:
                            #     {matching_act["keyword_words"]}
                            # """
                            # perubahan disini, get key values from dic matching_act["keyword_word"]
                            # to identify problematic terms and the recommended actions
                            data_act = matching_act["keyword_words"]
                            key_act = next(iter(data_act))
                            values_act = data_act[key_act]
                            # ini untuk mengambil data role, bisa diambil dari Who_actor table Who
                            # print("Role:", matching_sub["actor"])
                            # ini untuk mengambil data action -have-, diambil dari key_act,
                            # disimpan sebagai tambahan anggota di tabel keyword glossary
                            # print("Action:", key_act)
                            # print(
                            #     "Recommendation terms for the user:",
                            #     matching_sub["role_s_list"],
                            # )
                            # ini tidak disimpan, harusnya indexnya sudah ada di tabel keyword glossary -CRUD...-
                            # print("Recommendation terms for the action:", values_act)

                            if key_act:
                                terms_obj, created = ReportTerms.objects.get_or_create(
                                    userstory=userstory,
                                    type=ReportUserStory.ANALYS_TYPE.PRECISE,
                                )
                                terms_obj.action = key_act
                                if len(values_act):
                                    terms_obj.terms_actions = values_act
                                terms_obj.save()

                            #     keyword_obj, created = KeywordGlossary.objects.get_or_create(
                            #         keyword=key_act
                            #     )
                            #     terms_obj.keyword = keyword_obj

                            #     if len(values_act):
                            #         for act in values_act:
                            #             glossary_obj, created = Glossary.objects.get_or_create(
                            #                 Action_item=act
                            #             )
                            #             terms_obj.glossarys.add(glossary_obj)
                            #             keyword_obj.item_name.add(glossary_obj)
                            #             keyword_obj.save()
                            #     terms_obj.save()

                            recommendation += f"""Role: {matching_sub["actor"]}\n
                            Action: {key_act}\n
                            Recommendation terms for the user: {matching_sub["role_s_list"]}\n
                            Recommendation terms for the action: {values_act}\n
                            """
                            recommendation_type = (
                                ReportUserStory.RECOMENDATION_TYPE.ACTION_ROLE
                            )
                    elif (
                        matching_sub["cluster_label"] == -1
                        and matching_act["label"] == "1"
                    ):
                        # print("Recommended terms: ")
                        # print(
                        #     "Recommendation for the user are:",
                        #     matching_sub["role_s_list"],
                        # )
                        # recommendation += f"""Recommendation for the user are:
                        #     {matching_sub["role_s_list"]}
                        # """
                        # Perubahan disini, identify problematic terms in role and action, give recommended terms for role and actions
                        # print("Problematic terms:")
                        # print("Role:", matching_sub["actor"])
                        # print(
                        #     "Recommendation terms for the user:",
                        #     matching_sub["role_s_list"],
                        # )
                        if matching_sub["role_s_list"] and len(
                            matching_sub["role_s_list"]
                        ):
                            for role_item in matching_sub["role_s_list"]:
                                role_key = role_item.strip().lower()
                                role_, created = Role.objects.get_or_create(
                                    role_key=role_key,
                                    userstory=userstory,
                                    status=ReportUserStory.ANALYS_TYPE.PRECISE,
                                )
                                role_.role=role_item
                                role_.save()
                        recommendation += f"""\n\nProblematic terms:\n\n Role: {matching_sub["actor"]}\n
                        Recommendation terms for the user: {matching_sub["role_s_list"]}\n
                        """
                        recommendation_type = ReportUserStory.RECOMENDATION_TYPE.ROLE
                    elif (
                        matching_sub["cluster_label"] != -1
                        and matching_act["label"] != "1"
                    ):
                        # print("Recommended terms: ")
                        if (
                            matching_sub["cluster_label"] != -1
                            and matching_act["label"] == ""
                        ):
                            # print(
                            #     "Recommendation for the action are: Sorry. We do not have recommendation for the action. The action is too vague."
                            # )
                            # recommendation += "Recommendation for the action are: Sorry. We do not have recommendation for the action. The action is too vague."
                            # print(
                            #     "Recommendation terms for the action: Sorry. We do not have recommendation for the action. The action is too vague."
                            # )
                            recommendation += "\n\nRecommendation terms for the action: Sorry. We do not have recommendation for the action. The action is too vague."
                        elif (
                            matching_sub["cluster_label"] != -1
                            and matching_act["label"] == ">1"
                        ):
                            # print(
                            #     "Recommendation for the action are:",
                            #     matching_act["keyword_words"],
                            # )
                            # recommendation += f"""Recommendation for the user are:
                            #     {matching_act["keyword_words"]}
                            # """
                            # perubahan disini, get key values from dic matching_act["keyword_word"]
                            # to identify problematic terms and the recommended actions
                            data_act = matching_act["keyword_words"]
                            key_act = next(iter(data_act))
                            values_act = data_act[key_act]
                            # print("Problematic terms:")
                            # print("Action:", key_act)
                            # print("Recommendation terms for the action:", values_act)
                            terms_obj, created = ReportTerms.objects.get_or_create(
                                userstory=userstory,
                                type=ReportUserStory.ANALYS_TYPE.PRECISE,
                            )
                            terms_obj.action = key_act
                            if len(values_act):
                                terms_obj.terms_actions = values_act
                            terms_obj.save()
                            recommendation += f"""\n\nProblematic terms:\n\n Action: {key_act}\n
                            Recommendation terms for the action: {values_act}\n
                            """
                            recommendation_type = (
                                ReportUserStory.RECOMENDATION_TYPE.ACTION
                            )
                    self.save_report(
                        userstory,
                        matching_sub["status"],
                        ReportUserStory.ANALYS_TYPE.PRECISE,
                        {
                            "recommendation": recommendation,
                            "description": description,
                            "recommendation_type": recommendation_type,
                        },
                        is_problem,
                    )
            else:
                print("Role: Not Found")

    # ============ Consistent Criteria ============
    def get_top_terms_role(self, dic_role, num_terms):
        noun = ["NN", "NNS", "NNP", "NNPS"]
        excluded_words = ["as", "am", "i", "is", "and", "or", "&", "/"]

        # Create a dictionary to store the top terms for each act_cluster_label
        top_terms_dict = {}

        # NOTE: Old Version
        # for item in dic_role:
        #     role = item["actor"]
        #     role_cluster_label = item["role_cluster_label"]
        #     terms = [
        #         term
        #         for term, pos in pos_tag(word_tokenize(role))
        #         if pos in noun and term not in excluded_words
        #     ]
        #     if role_cluster_label != -1:
        #         if role_cluster_label not in top_terms_dict:
        #             top_terms_dict[role_cluster_label] = []
        #         top_terms_dict[role_cluster_label].extend(terms)
        # top_terms_role = {}
        # for label, terms in top_terms_dict.items():
        #     term_counts = Counter(terms)
        #     top_terms_role[label] = [
        #         term for term, count in term_counts.most_common(num_terms)
        #     ]

        # Iterate over the dic_action dictionary
        for item in dic_role:
            role = item["actor"]
            role_cluster_label = item["role_cluster_label"]

            # Get the list of terms for the current action
            # Update the top terms for the corresponding act_cluster_label
            if role_cluster_label != -1:
                if role_cluster_label not in top_terms_dict:
                    top_terms_dict[role_cluster_label] = []
                top_terms_dict[role_cluster_label].extend(role)

        # Calculate the top terms for each act_cluster_label
        top_terms_role = {}
        for label, item in top_terms_dict.items():
            term_counts = Counter(item)
            top_terms_role[label] = [
                item for item, count in term_counts.most_common(num_terms)
            ]
        return top_terms_role

    def get_top_terms_act(self, dic_action, num_terms):
        noun_verbs = ["VB", "VBD", "VBG", "VBN", "VBP", "VBZ"]
        excluded_words = [
            "be",
            "am",
            "i",
            "is",
            "are",
            "was",
            "were",
            "been",
            "being",
            "do",
            "does",
            "did",
            "done",
            "doing",
            "have",
            "has",
            "had",
            "having",
            "can",
            "could",
            "may",
            "might",
            "must",
            "shall",
            "should",
            "will",
            "would",
        ]

        # Create a dictionary to store the top terms for each act_cluster_label
        top_terms_dict = {}

        # Iterate over the dic_action dictionary
        for item in dic_action:
            action = item["action"]
            act_cluster_label = item["act_cluster_label"]

            # Get the list of terms for the current action
            terms = [
                term
                for term, pos in pos_tag(word_tokenize(action))
                if pos in noun_verbs and term not in excluded_words
            ]

            # Update the top terms for the corresponding act_cluster_label
            if act_cluster_label not in top_terms_dict:
                top_terms_dict[act_cluster_label] = []
            top_terms_dict[act_cluster_label].extend(terms)

        # Calculate the top terms for each act_cluster_label
        top_terms_act = {}
        for label, terms in top_terms_dict.items():
            term_counts = Counter(terms)
            top_terms_act[label] = term_counts.most_common(num_terms)

        return top_terms_act

    def who_consistency(self):
        # Collect all the subject values
        txt = []
        r_txt = []
        a_txt = []
        dic_role = []
        userstory_list = []

        for item in self.well_formed_data:
            text = item["userstory"]
            userstory = item["userstory_obj"]
            role = item["actor"].Who_action
            action = item["action"].What_action
            txt.append(text)
            r_txt.append(role)
            a_txt.append(action)
            userstory_list.append(userstory)

        # Vectorize the role_s values using TF-IDF
        vectorizer = TfidfVectorizer()
        X = vectorizer.fit_transform(r_txt)

        # Apply DBSCAN clustering
        dbscan = DBSCAN(eps=self.eps, min_samples=int(self.min_samples))
        labels = dbscan.fit_predict(X)

        # Get unique cluster labels
        unique_labels = np.unique(labels)

        # Group the role_s values and texts by their labels
        grouped_role_s = defaultdict(list)  # Use defaultdict to simplify groupings
        role_s_lists = defaultdict(list)  # Store top terms for each cluster label

        for role, text, label, userstory in zip(r_txt, txt, labels, userstory_list):
            grouped_role_s[label].append((role, text, userstory))

        # Iterate over cluster labels and their corresponding role_s values
        for label, role_s_text_list in grouped_role_s.items():
            role_s_list = []  # Reset role_s_list for each cluster label
            for role, text, userstory in role_s_text_list:
                if role not in role_s_list:
                    role_s_list.append(role)
            role_s_lists[
                label
            ] = role_s_list  # Store the role_s_list for each cluster label

            if label == -1:  # Check if the cluster label is not -1
                # Append the dictionary to dic_role
                for role, text, userstory in role_s_text_list:
                    dic_role.append(
                        {
                            # "index": index+1,
                            "userstory": userstory,
                            "text": text,
                            "actor": role,
                            "role_cluster_label": label,
                        }
                    )
            else:
                # Append the dictionary to dic_role
                for role, text, userstory in role_s_text_list:
                    dic_role.append(
                        {
                            "userstory": userstory,
                            "text": text,
                            "actor": role,
                            "role_cluster_label": label,
                        }
                    )
        return dic_role

    def what_consistency(self):
        # Collect all the subject values
        txt = []
        r_txt = []
        a_txt = []
        dic_action = []
        # remove stopwords, punctuations, and apply lemmatization
        stop_words = set(stopwords.words("english"))
        lemmatizer = WordNetLemmatizer()

        index = 0
        for item in self.well_formed_data:
            userstory = item["userstory_obj"]
            text = item["userstory"]
            role = item["actor"].Who_action
            action = item["action"].What_action

            # Remove punctuation from action
            action = action.translate(str.maketrans("", "", string.punctuation))

            # Tokenize the action into individual words
            words = word_tokenize(action)

            # Lemmatize each word and join them back into a sentence
            lemmatized_sentence = " ".join(lemmatizer.lemmatize(word) for word in words)

            # Vectorize the role_s values using TF-IDF
            vectorizer = TfidfVectorizer()
            X = vectorizer.fit_transform([lemmatized_sentence])

            # Apply DBSCAN clustering
            dbscan = DBSCAN(eps=self.eps, min_samples=int(self.min_samples))
            labels = dbscan.fit_predict(X)

            # Add the text, action, and cluster label to the dictionary
            status = "consistent" if labels[0] != -1 else "inconsistent"
            dic_action.append(
                {
                    "index": index + 1,
                    "userstory": userstory,
                    "text": text,
                    "action": lemmatized_sentence,
                    "act_cluster_label": labels[0],
                    "status": status,
                }
            )

        # Get the top terms for each act_cluster_label
        # isian pertama, what is your preferred number of terms to be displayed in each class, jika tidak diisi gunakan default ini
        top_terms_act = self.get_top_terms_act(dic_action, int(self.terms_action))

        # Update dic_action with the top terms
        for item in dic_action:
            act_cluster_label = item["act_cluster_label"]
            if act_cluster_label in top_terms_act:
                item["top_terms"] = top_terms_act[act_cluster_label]
            else:
                item["top_terms"] = []

        return dic_action

    def stat_consistency(self, dic_role, dic_action):
        cons_texts = {}
        consistency = []
        top_terms_role = []
        top_terms_act = []

        status = ""
        recommendation = ""
        is_problem = False
        for act in dic_action:
            for sub in dic_role:
                if act["text"] == sub["text"]:
                    if (
                        sub["role_cluster_label"] == -1
                    ):  # and act["act_cluster_label"] != -1:
                        status = (
                            "Consistency criterion is not achieved. User role is not consistent."
                            "\nUser story is potentially ambiguous!"
                        )
                        recommendation = (
                            "Change the user role using the same terminology."
                        )
                        is_problem = True
                    else:
                        status = (
                            "Consistency criterion is achieved. User story is good."
                        )
                        recommendation = "pass"
                        is_problem = False

                    sub["status"] = status
                    sub["recommendation"] = recommendation
                    sub["is_problem"] = is_problem
                    sub["top_terms_role"] = top_terms_role
                    act["top_terms_act"] = top_terms_act

                    cons_texts = {
                        "text": sub["text"],
                        "role_actor": sub.get("actor"),
                        "action_act": act.get("action"),
                        "role_label": sub["role_cluster_label"],
                        "act_label": act["act_cluster_label"],
                        "status": sub["status"],
                        "recommendation": sub["recommendation"],
                        "is_problem": sub["is_problem"],
                    }
                    consistency.append(cons_texts)
        return consistency

    def running_stat_consistency(self):
        dic_role = self.who_consistency()
        dic_action = self.what_consistency()
        consistency = self.stat_consistency(dic_role, dic_action)

        print("== Consistent criterion analysis - finding lexical ambiguity: ==")
        for sc in consistency:
            Text = sc["text"]
            is_problem = sc["is_problem"]
            # default the preferred number of top terms to be displayed in each class (1), preferred number of top terms bisa diubah

            top_terms_role = self.get_top_terms_role(dic_role, int(self.terms_role))
            top_terms_act = self.get_top_terms_act(dic_action, int(self.terms_action))

            # Finding the corresponding dictionary in "dic_sub" using "text" key
            matching_sub = next((sub for sub in dic_role if sub["text"] == Text), None)
            matching_act = next(
                (act for act in dic_action if act["text"] == Text), None
            )

            if matching_sub or matching_act:
                if Text:
                    # Accessing "actor" key from the "matching_sub" dictionary in "dic_sub"
                    userstory = None
                    if matching_sub.get("userstory", None):
                        userstory = matching_sub["userstory"]
                    if matching_act.get("userstory", None):
                        userstory = matching_act["userstory"]

                    # print(f'\n{userstory}')
                    # print("Story #", matching_act["index"], ": ", Text)
                    # print("Role:", matching_sub["actor"])
                    # print("Action:", matching_act["action"])
                    # print("Status:", matching_sub["status"])
                    # print("Recommendation:", matching_sub["recommendation"])

                    description = f'Role: {matching_sub["actor"]}\n\nAction: {matching_act["action"]}'
                    recommendation = matching_sub["recommendation"]
                    # is_problem = False
                    recommendation_type = None
                    if matching_sub["role_cluster_label"] == -1:
                        recommendation = f"""\n\n
                        Problematic terms: {matching_sub["actor"]}\n\n
                        Recommendation terms: 
                        Terms for role: {str(top_terms_role)}
                        """
                        for key, value in top_terms_role.items():
                            for role_term in value:
                                # term = role_term.strip()
                                role_key = role_term.strip().lower()
                                role_, created = Role.objects.get_or_create(
                                    role_key=role_key,
                                    userstory=userstory,
                                    status=ReportUserStory.ANALYS_TYPE.CONSISTENT,
                                )
                                role_.role=role_term
                                role_.save()
                        recommendation_type = ReportUserStory.RECOMENDATION_TYPE.ROLE

                    self.save_report(
                        userstory,
                        matching_sub["status"],
                        ReportUserStory.ANALYS_TYPE.CONSISTENT,
                        {
                            "recommendation": recommendation,
                            "description": description,
                            "recommendation_type": recommendation_type,
                        },
                        is_problem,
                    )
            else:
                print("Role: Not Found")
        return consistency

    # ============ Conceptually Sound ============

    def extract_subject_object_predicate(self):
        sentence_dependency = []
        dic_sent = {}
        for item in self.well_formed_data:
            userstory = item["userstory_obj"]
            text = item["userstory"]
            role = item["actor"].Who_action if item["actor"] else None
            action = item["action"].What_action if item["action"] else None
            goal = item["goal"]
            index = item["index"]

            doc = self.nlp(action)

            subject = None
            predicate = None
            obj = None

            skip_next_token = False
            skip_next_verb = False

            for token in doc:
                if skip_next_token:
                    skip_next_token = False
                    continue

                if token.text.lower() == "want to" or token.text.lower() == "want":
                    skip_next_token = True
                    continue

                if skip_next_verb and token.pos_ == "VERB":
                    skip_next_verb = False
                    continue

                if "subj" in token.dep_:
                    subject = token.text
                elif "obj" in token.dep_ and (
                    token.pos_ == "PROPN" or token.pos_ == "NOUN"
                ):
                    obj = token.text
                    if list(
                        doc[token.left_edge.i : token.right_edge.i + 1].noun_chunks
                    ):
                        obj = " ".join(
                            chunk.text
                            for chunk in doc[
                                token.left_edge.i : token.right_edge.i + 1
                            ].noun_chunks
                        )
                elif token.pos_ == "VERB":
                    if predicate is None:
                        predicate = token.text
                    else:
                        predicate += " " + token.text
                    skip_next_verb = True
                    if token.subtree:
                        predicate = " ".join(t.text for t in token.subtree)
            # Exclude "obj" from the predicate
            predicate = predicate.replace(obj, "") if obj and predicate else predicate
            dic_sent = {
                "index": index + 1,
                "userstory": userstory,
                "sentence": text,
                "subject": role,
                "predicate": predicate,
                "object": obj,
            }
            sentence_dependency.append(dic_sent)
        return sentence_dependency

    def classify_topic(self, sentence_dependency):
        topic_btm = []
        new_docs = []
        for dic_sent in sentence_dependency:
            index1 = dic_sent["index"]
            sent = dic_sent["sentence"]
            subject = dic_sent["subject"]
            predicate = dic_sent["predicate"] if dic_sent["predicate"] else ""
            obj = dic_sent["object"]
            new_doc = "".join(predicate)

            new_docs.append(new_doc)
        X, vocabulary, vocab_dict = btm.get_words_freqs(new_docs)
        docs_vec = btm.get_vectorized_docs(new_docs, vocabulary)
        biterms = btm.get_biterms(docs_vec)

        # running model
        # the preferred number of topics (T) dapat diubah (2). T = 10 adalah default topic number
        model = btm.BTM(X, vocabulary, T=self.topics, M=20, alpha=50 / 7, beta=0.01)
        model.fit(biterms, iterations=100)

        p_zd = model.fit_transform(
            docs_vec, biterms, infer_type="sum_b", iterations=100
        )

        # print text and topic number
        result = btm.get_docs_top_topic(new_docs, p_zd)

        topic_vectors = []

        for index, doc_topic_dist in enumerate(p_zd):
            text = new_docs[index]
            cluster_topic = max(
                range(len(doc_topic_dist)), key=doc_topic_dist.__getitem__
            )

            # Get the top terms for the cluster topic
            top_words = btm.get_top_topic_words(
                model, words_num=10, topics_idx=[cluster_topic]
            )

            # Extract the column name dynamically
            word_column = top_words.columns[0]

            # Extract the cluster words from the top_words DataFrame
            cluster_words = top_words[word_column].tolist()

            # Shuffle the cluster words to add randomness
            random.shuffle(cluster_words)

            # Random sentence generation
            sentence_length = min(5, len(cluster_words))
            sentence = random.sample(cluster_words, sentence_length)

            # Combine the words in the sentence
            cluster_sentence = " ".join(sentence)

            for dic_sent in sentence_dependency:
                if dic_sent["predicate"] == text:
                    # Create a dictionary with the document's information
                    doc_info = {
                        "index": dic_sent["index"],
                        "userstory": dic_sent["userstory"],
                        "text": dic_sent["sentence"],
                        "subject": dic_sent["subject"],
                        "predicate": dic_sent["predicate"],
                        "object": dic_sent["object"],
                        "cluster_topic": cluster_topic,
                        "terms_in_cluster_topic": cluster_words,
                        "cluster_sentence": cluster_sentence,
                    }

                    topic_btm.append(doc_info)
        return topic_btm

    def topic_conceptually(self, topic_btm):
        sent_concept = []
        keyword_to_sentence_class = {}
        for top in topic_btm:
            index = top["index"]
            userstory = top["userstory"]
            sent = top["text"]
            subject = top["subject"]
            predicate = top["predicate"]
            ob_ject = top["object"]
            cluster_topic = top["cluster_topic"]
            terms_in_cluster_topic = top["terms_in_cluster_topic"]
            cluster_sentence = top["cluster_sentence"]

            doc = self.nlp(predicate)

            sentence_class = set()

            keyword_words = set()

            for token in doc:
                if token.pos_ == "VERB":
                    word_class = self.get_word_class(token.text)

                    if word_class:
                        sentence_class.add(word_class.keyword)
                        keyword_words.add(token.text)

                        for keyword_word in keyword_words:
                            if keyword_word not in keyword_to_sentence_class:
                                keyword_to_sentence_class[keyword_word] = set()
                            keyword_to_sentence_class[keyword_word].add(
                                word_class.keyword
                            )
                    else:
                        synsets = wordnet.synsets(token.text)
                        for synset in synsets:
                            synset_class = self.get_synset_class(synset)
                            if synset_class:
                                sentence_class.add(synset_class.keyword)
                                keyword_words.add(token.text)
                                for keyword_word in keyword_words:
                                    if keyword_word not in keyword_to_sentence_class:
                                        keyword_to_sentence_class[keyword_word] = set()
                                    keyword_to_sentence_class[keyword_word].add(
                                        synset_class.keyword
                                    )
            labels = []
            sentence_classify = {
                "index": index,
                "userstory": userstory,
                "sentence": sent,
                "subject": subject,
                "predicate": predicate,
                "object": ob_ject,
                "cluster_topic": cluster_topic,
                "terms_in_cluster_topic": terms_in_cluster_topic,
                "cluster_sentence": cluster_sentence,
                "sentence_class": list(sentence_class),
                "keyword_words": {
                    keyword_word: list(keyword_to_sentence_class[keyword_word])
                    for keyword_word in keyword_words
                },
            }

            for key, value in sentence_classify["keyword_words"].items():
                num_items = len(value)

                if not num_items:
                    sentence_classify["label"] = "0"
                elif num_items > 1:
                    sentence_classify["label"] = ">1"
                elif num_items == 1:
                    sentence_classify["label"] = "1"

            sent_concept.append(sentence_classify)
        return sent_concept

    def stat_conceptually_sound(self):
        sentence_dependency = self.extract_subject_object_predicate()
        topic_btm = self.classify_topic(sentence_dependency)
        sent_concept = self.topic_conceptually(topic_btm)
        # print("\n============ Start Conceptually Sound ============\n")
        # print("== Conceptually sound analysis - identify semantic ambiguity ==")
        for item in sent_concept:
            # print("\nStory #", item["index"], ":", item["sentence"])
            # print(f'{item["userstory"]}')
            # print("Subject:", item["subject"])
            # print("Predicate:", item["predicate"])
            # print("Object:", item["object"])

            # print("Topic #", item["cluster_topic"])
            # print("Top terms: ", item["terms_in_cluster_topic"])
            # print("Action terms: ", item["keyword_words"])
            subject = item["subject"]
            predicate = item["predicate"]

            description = f"""Subject: {subject}
            Predicate: {predicate}
            Object: {item.get('object', '')}
            """
            status = None
            recommendation = None
            is_problem = False
            recommendation_type = None
            if not item["sentence_class"] or item["object"] == None:
                # print("Status: The user story is potentially ambiguous. It might be underspecified.")
                # print("Recommendation: Rewrite the predicate or the object ! ")
                status = "The user story is potentially ambiguous. It might be underspecified."
                recommendation = "Recommendation: Rewrite the predicate !"
                is_problem = True
                recommendation_type = ReportUserStory.RECOMENDATION_TYPE.ACTION_MANUAL
            elif len(item["sentence_class"]) > 1 or item["object"] == None:
                # print(
                #     "Status: The user story is potentially ambiguous. It might be wrongly decode."
                # )
                # print(
                #     "Recommendation: Rewrite the predicate using one of these term : ",
                #     item["sentence_class"],
                # )
                # perubahan disini, identify problematic terms in user story
                data_act = item["keyword_words"]
                key_act = next(iter(data_act))
                values_act = data_act[key_act]

                if key_act:
                    terms_obj, created = ReportTerms.objects.get_or_create(
                        userstory=item["userstory"],
                        type=ReportUserStory.ANALYS_TYPE.CONCEPTUALLY,
                    )
                    terms_obj.action = key_act
                    if len(values_act):
                        terms_obj.terms_actions = values_act
                    terms_obj.save()
                # print("Problematic terms:", key_act)
                status = "The user story is potentially ambiguous. It might be wrongly decode."
                recommendation = f'Recommendation: Rewrite the predicate using one of these term :\n{item["sentence_class"]}'
                recommendation_type = ReportUserStory.RECOMENDATION_TYPE.ACTION
                is_problem = True
            elif len(item["sentence_class"]) == 1 and item["object"] == None:
                # print("Status: The user story is potentially ambiguous. The object is not exist.")
                # print("Recommendation: Rewrite the user story !")
                status = (
                    "The user story is potentially ambiguous. The object is not exist."
                )
                recommendation = "Rewrite the user story !"
            elif len(item["sentence_class"]) == 1:
                # print("Status: user story is fine !")
                status = "user story is fine !"

            if status or recommendation:
                self.save_report(
                    item["userstory"],
                    status,
                    ReportUserStory.ANALYS_TYPE.CONCEPTUALLY,
                    {
                        "recommendation": recommendation,
                        "description": description,
                        "recommendation_type": recommendation_type,
                        "subject": subject,
                        "predicate": predicate,
                    },
                    is_problem,
                )
        return sent_concept

    # ============ Uniqueness Criteria ============

    def stat_uniqueness_criteria(self):
        model_st = SentenceTransformer("all-MiniLM-L6-v2")
        pair_role = []
        pair_action = []
        pair_goal = []
        tot_score = []

        stat_sim = ""
        sol_sim = ""

        role_user = []
        action_user = []
        goal_user = []
        userstory_list = []
        for item in self.well_formed_data:
            role_user.append(item["actor"].Who_action if item["actor"] else None)
            action_user.append(item["action"].What_action if item["action"] else None)
            goal_user.append(item["goal"].Why_action if item["goal"] else None)
            userstory_list.append(item["userstory_obj"])

        # # text=df_element['UserStory']
        # # role=df_element['Role']
        # # action=df_element['Action']
        # # role_user = df_segment["Role_user"]
        # # action_user = df_segment['Action_user']
        # # goal_user = df_segment["Goal_user"]
        # # goal=df_element['Goal']

        # if not role.empty and not action.empty:
        role_embeddings = model_st.encode(role_user)
        # action_embeddings=model.encode(df_element['Action'].values)
        action_embeddings = model_st.encode(action_user)
        goal_embeddings = model_st.encode(goal_user)
        # print(action_embeddings)

        score_role = util.cos_sim(role_embeddings, role_embeddings)
        score_action = util.cos_sim(action_embeddings, action_embeddings)
        score_goal = util.cos_sim(goal_embeddings, goal_embeddings)

        # bandingkan role ke-i dan ke -(i+1)
        for i in range(len(score_role) - 1):
            for j in range(i + 1, len(score_role)):
                pair_role.append({"index": [i, j], "sim_score_role": score_role[i][j]})

        # bandingkan action ke-i dan ke-(i+1)
        for i in range(len(score_action) - 1):
            for j in range(i + 1, len(score_action)):
                pair_action.append(
                    {"index": [i, j], "sim_score_action": score_action[i][j]}
                )

        # bandingkan goal ke-i dan ke-(i+1)
        for i in range(len(score_goal) - 1):
            for j in range(i + 1, len(score_goal)):
                pair_goal.append({"index": [i, j], "sim_score_goal": score_goal[i][j]})

        if len(goal_user) <= 0:
            for i in range(len(score_action) - 1):
                tot_score.append(
                    {
                        "index": [i, j],
                        "sim_score_tot": (score_role[i][j] + score_action[i][j]) / 2,
                    }
                )
        else:
            for i in range(len(score_action) - 1):
                tot_score.append(
                    {
                        "index": [i, j],
                        "sim_score_tot": (
                            score_role[i][j] + score_action[i][j] + score_goal[i][j]
                        )
                        / 3,
                    }
                )

        result = list(zip(pair_role, pair_action, pair_goal, tot_score))
        result = sorted(result, key=lambda x: x[3]["sim_score_tot"], reverse=True)

        print("== Uniqueness analysis - for semantic duplication - ==")
        for pr_role, pr_act, pr_goal, tot in result:
            i, j = pr_role["index"]
            pr_act.update({"index": (i, j)})
            tot.update({"index": (i, j)})

            role_score = float(pr_role["sim_score_role"])
            role_score = round(role_score, 4)

            action_score = float(pr_act["sim_score_action"])
            action_score = round(action_score, 4)

            goal_score = float(pr_goal["sim_score_goal"])
            goal_score = round(goal_score, 4)

            sim_score = float(tot["sim_score_tot"])
            sim_score = round(sim_score, 4)

            # maximum level of similarity, role (who), action (what), and goal (why).
            # semua variabel (who, what, why) disamakan similaritynya. nilai default = 0.6 (untuk who/role dan what/action), 0.5 (untuk why/goal)
            is_problem = False
            who_score, what_score, why_score = 0.6, 0.6, 0.5
            if self.similarity:
                who_score, what_score, why_score = (
                    self.similarity,
                    self.similarity,
                    self.similarity,
                )

            if (
                (role_score > who_score)
                and (action_score > what_score)
                and (goal_score > why_score)
            ):
                stat_sim = "Status: Uniqueness is not achieved. User stories might be ambiguous !"
                sol_sim = "Recommendation: Delete one user story!"
                is_problem = True

            elif (
                (role_score < who_score)
                and (action_score > what_score)
                and (goal_score > why_score)
            ):
                stat_sim = "Result: Conflict-free may not be achieved. User stories might be ambiguous !"
                sol_sim = "Recommendation: Need manual confirmation from the user"
                is_problem = True
            elif (
                (role_score > who_score)
                and (action_score < what_score)
                and (goal_score > why_score)
            ):
                stat_sim = "Result: Uniqueness is achieved !"
                sol_sim = "User story is fine !"

            elif (
                (role_score > who_score)
                and (action_score > what_score)
                and (goal_score < why_score)
            ):
                stat_sim = "Result: Uniqueness is achieved !"
                sol_sim = "User story is fine !"

            elif (
                (role_score < who_score)
                and (action_score < what_score)
                and (goal_score > why_score)
            ):
                stat_sim = "Result: Uniqueness is achieved !"
                sol_sim = "User story is fine !"

            elif (
                (role_score < who_score)
                and (action_score < what_score)
                and (goal_score < why_score)
            ):
                stat_sim = "Result: Conflict-free is achieved, Uniqueness is achieved !"
                sol_sim = "User story is fine !"

            elif (role_score < who_score) and (
                (action_score > what_score) or (goal_score > why_score)
            ):
                stat_sim = "Result: Conflict-free is achieved !"
                sol_sim = "User story is fine !"
            else:
                stat_sim = "Result: Uniqueness is achieved !"
                sol_sim = "User story is fine !"

            story_a_id = userstory_list[i].id if userstory_list[i] else ""
            story_b_id = userstory_list[j].id if userstory_list[j] else ""

            description = f"""Story #{story_a_id}: {userstory_list[i]}
            Story #{story_b_id}: {userstory_list[j]}\n
            Role 1: {role_user[i]}
            Role 2: {role_user[j]}
            Similarity score in role: {role_score}\n
            Action 1: {action_user[i]}
            Action 2: {action_user[j]}
            Similarity score in action: {action_score}\n
            Goal 1: {goal_user[i]}
            Goal 2: {goal_user[j]}
            Similarity score in goal: {goal_score}\n
            Total similarity score:  {sim_score}
            {stat_sim}
            {sol_sim}
            """

            self.save_report(
                userstory_list[i],
                stat_sim,
                ReportUserStory.ANALYS_TYPE.UNIQUENESS,
                {"recommendation": sol_sim, "description": description},
                is_problem,
            )
