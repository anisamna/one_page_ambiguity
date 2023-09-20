import re
from difflib import SequenceMatcher

import nltk
from django.db.models import F
from nltk import word_tokenize
from nltk.parse import CoreNLPParser
from sklearn.feature_extraction.text import CountVectorizer, TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

# from nltk.parse.chart import ChartParser
# from nltk.parse.chart import demo_grammar
from inputUS.models import Parser  # , Who, What, UserStory_joined
from inputUS.models import (ParsingDetail, Similarity_Analysis,
                            UserStory_element, UserStory_What, UserStory_Who,
                            Well_Formed)

ROLE_DEL = "As an|As a|As"
ACTION_DEL = (
    "I'm able to|I am able to|I want to|I want|I wish to|I can|I should be able to"
)
GOAL_DEL = "so that|so|in order to|in order"

CONJUNCTIONS = [" and ", "&", "\+", " or ", ">", "<", "/", "\\"]
PUNCTUATIONS = [".", ";", ":", "‒", "–", "—", "―", "‐", "-", "?", "*"]
BRACKETS = [["(", ")"], ["[", "]"], ["{", "}"], ["⟨", "⟩"]]


def well_formed_an(obj_id):
    get_UserStory_data = UserStory_element.objects.get(id=obj_id)

    status = "Well-formed criteria is not achieved !"
    # status = None
    recommendation = None

    if get_UserStory_data:
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
                    status = "Well-formed criterion is achieved !"
                    recommendation = ""

        well_formed_obj, created = Well_Formed.objects.get_or_create(
            UserStory_Segment_ID=get_UserStory_data,
        )

        well_formed_obj.result_desc = status
        # well_formed_obj.result_name = recommendation
        well_formed_obj.Action_Name = recommendation

        if status != "% not %":
            well_formed_obj.Solution_Name = "pass"
        else:
            well_formed_obj.Solution_Name = 'rewrite with the format, "As a <user_role>, I want to <action>, so that <benefit>"'

        well_formed_obj.save()
        get_UserStory_data.is_processed = True
        get_UserStory_data.save()
