import re

from inputUS.models import (
    US_Upload,
    UserStory_element,
    UserStory_What,
    UserStory_Who,
    UserStory_Why,
)

ROLE_DEL = "As an|As a|As"
ACTION_DEL = "I have to| I have| I need to| I need |I'm able to|I am able to|I want to|I want|I wish to|I can|I should be able to|I do not want|I don't want|I only want"
GOAL_DEL = "So that|so that|So|so|in order to"


def is_token_excluded(token):
    return bool(re.search(r"\bso\b", token, re.IGNORECASE))


def segmentation(obj_id):
    retrieve_UserStory_data = US_Upload.objects.get(id=obj_id)
    UserStories = retrieve_UserStory_data.US_File_Content

    for item in UserStories:
        m1_role = ""
        temp_role = ""
        action_id = ""
        action_usr = ""
        goal_id = ""
        goal_usr = ""

        m_role = re.search(ROLE_DEL, item)

        if m_role:
            m1_role = m_role.group(0)

            spl = re.split(ROLE_DEL, item)
            res = spl[1]
            if "," in res:
                split = res.split(",")
                temp_role = split[0]
                temp_role_1 = split[0]

            else:
                temp_role = res.split("I")[0]
                temp_role_1 = res.split("I")[0]

        else:
            m1_role = ""
            res = item

            find_action = re.search(ACTION_DEL, res)
            if find_action:
                temp_action_id = find_action.group(0)
                split = re.split(ACTION_DEL, res)
                temp_role = split[0]
                if temp_role.isalnum():
                    temp_role = temp_role
                else:
                    temp_role = split[0]
                    if temp_role is not None:
                        temp_role = temp_role
                    else:
                        temp_role = ""

            else:
                temp_role = ""

        role_id = m1_role
        role_act = temp_role
        who = role_id + role_act

        # find action
        m_action = re.search(ACTION_DEL, item)

        if m_action:
            goal_phrases = GOAL_DEL.split("|")
            pattern = (
                r"\b(?:"
                + "|".join(re.escape(phrase) for phrase in goal_phrases)
                + r")\b"
            )
            find_goal = re.findall(pattern, item, re.IGNORECASE)
            if find_goal:
                action_id = m_action.group(0)
                goal_id = find_goal[0]

                # Check if the item has more than one ACTION_DEL
                action_occurrences = re.findall(ACTION_DEL, item, re.IGNORECASE)
                # print("action_occurences:", action_occurrences)

                if len(action_occurrences) > 1:
                    item_split = re.split(ACTION_DEL, item, 1, re.IGNORECASE)
                    action_goal = item_split[1].strip()

                    split_goal = re.split(GOAL_DEL, action_goal, re.IGNORECASE)
                    # print("split_goal:", split_goal)
                    action_usr = split_goal[0]
                    goal_usr = split_goal[1]

                else:
                    spl_act = re.split(ACTION_DEL, item)
                    action_usr = spl_act[1].strip()
                    split_action = re.split(
                        re.escape(goal_id), action_usr, flags=re.IGNORECASE
                    )
                    action_usr = split_action[0]
                    goal_usr = split_action[1].strip() if len(split_action) > 1 else ""

            else:
                action_id = m_action.group(0)
                spl_act = re.split(ACTION_DEL, item)
                action_usr = spl_act[1].strip()
                goal_id = ""
                goal_usr = ""
                # print('goal does not found')
                # print()
        else:
            action_id = ""
            action_usr = ""
            goal_id = ""
            goal_usr = ""

        what = action_id + " " + action_usr

        why = goal_id + " " + goal_usr

        # print('item:', item)
        # print('role_id:', role_id)
        # print('role_usr:', role_act)
        # print('action_id:', action_id)
        # print('action_usr: ',action_usr)
        # print('goal_id:', goal_id)
        # print('goal_usr:', goal_usr)
        # print()

        userstory_obj_who, created = UserStory_Who.objects.get_or_create(
            Who_identifier=role_id,
            Who_action=role_act,
            Who_full=who,
            Element_type="Actor",
        )

        userstory_obj_who.save()

        userstory_obj_what, created = UserStory_What.objects.get_or_create(
            What_identifier=action_id,
            What_action=action_usr,
            What_full=what,
            Element_type="Action",
        )

        userstory_obj_what.save()

        userstory_obj_why, created = UserStory_Why.objects.get_or_create(
            Why_identifier=goal_id,
            Why_action=goal_usr,
            Why_full=why,
            Element_type="Goal",
        )

        userstory_obj_why.save()

        # print("retrieve_UserStory_data", retrieve_UserStory_data)
        userstory_obj, created = UserStory_element.objects.get_or_create(
            UserStory_Full_Text=item,
            Project_Name=retrieve_UserStory_data.US_Project_Domain,
            UserStory_File_ID=retrieve_UserStory_data,
        )

        if retrieve_UserStory_data.created_by:
            userstory_obj.created_by = retrieve_UserStory_data.created_by
        userstory_obj.Who_full = userstory_obj_who
        userstory_obj.What_full = userstory_obj_what
        userstory_obj.Why_full = userstory_obj_why
        userstory_obj.save()


def segmentation_edit_userstory(userstory_id, is_add=False):
    # userstory edit update spliting
    try:
        userstory_obj = UserStory_element.objects.get(id=userstory_id)
    except UserStory_element.DoesNotExist:
        pass
    else:
        item = userstory_obj.UserStory_Full_Text

        m1_role = ""
        temp_role = ""
        action_id = ""
        action_usr = ""
        goal_id = ""
        goal_usr = ""

        m_role = re.search(ROLE_DEL, item)
        if m_role:
            m1_role = m_role.group(0)

            spl = re.split(ROLE_DEL, item)
            res = spl[1]
            if "," in res:
                split = res.split(",")
                temp_role = split[0]
                temp_role_1 = split[0]

            else:
                temp_role = res.split("I")[0]
                temp_role_1 = res.split("I")[0]

        else:
            m1_role = ""
            res = item

            find_action = re.search(ACTION_DEL, res)
            if find_action:
                temp_action_id = find_action.group(0)
                split = re.split(ACTION_DEL, res)
                temp_role = split[0]
                if temp_role.isalnum():
                    temp_role = temp_role
                else:
                    temp_role = split[0]
                    if temp_role is not None:
                        temp_role = temp_role
                    else:
                        temp_role = ""

            else:
                temp_role = ""

        role_id = m1_role
        role_act = temp_role
        who = role_id + role_act

        # find action
        m_action = re.search(ACTION_DEL, item)

        if m_action:
            goal_phrases = GOAL_DEL.split("|")
            pattern = (
                r"\b(?:"
                + "|".join(re.escape(phrase) for phrase in goal_phrases)
                + r")\b"
            )
            find_goal = re.findall(pattern, item, re.IGNORECASE)
            if find_goal:
                action_id = m_action.group(0)
                goal_id = find_goal[0]

                # Check if the item has more than one ACTION_DEL
                action_occurrences = re.findall(ACTION_DEL, item, re.IGNORECASE)
                # print("action_occurences:", action_occurrences)

                if len(action_occurrences) > 1:
                    item_split = re.split(ACTION_DEL, item, 1, re.IGNORECASE)
                    action_goal = item_split[1].strip()

                    split_goal = re.split(GOAL_DEL, action_goal, re.IGNORECASE)
                    # print("split_goal:", split_goal)
                    action_usr = split_goal[0]
                    goal_usr = split_goal[1]

                else:
                    spl_act = re.split(ACTION_DEL, item)
                    action_usr = spl_act[1].strip()
                    split_action = re.split(
                        re.escape(goal_id), action_usr, flags=re.IGNORECASE
                    )
                    action_usr = split_action[0]
                    goal_usr = split_action[1].strip() if len(split_action) > 1 else ""

            else:
                action_id = m_action.group(0)
                spl_act = re.split(ACTION_DEL, item)
                action_usr = spl_act[1].strip()
                goal_id = ""
                goal_usr = ""
                # print('goal does not found')
                # print()
        else:
            action_id = ""
            action_usr = ""
            goal_id = ""
            goal_usr = ""

        what = action_id + " " + action_usr

        why = goal_id + " " + goal_usr

        if is_add:
            userstory_obj_who, created = UserStory_Who.objects.get_or_create(
                Who_identifier=role_id,
                Who_action=role_act,
                Who_full=who,
                Element_type="Actor",
            )

            userstory_obj_who.save()

            userstory_obj_what, created = UserStory_What.objects.get_or_create(
                What_identifier=action_id,
                What_action=action_usr,
                What_full=what,
                Element_type="Action",
            )

            userstory_obj_what.save()

            userstory_obj_why, created = UserStory_Why.objects.get_or_create(
                Why_identifier=goal_id,
                Why_action=goal_usr,
                Why_full=why,
                Element_type="Goal",
            )

            userstory_obj_why.save()
            userstory_obj.Who_full = userstory_obj_who
            userstory_obj.What_full = userstory_obj_what
            userstory_obj.Why_full = userstory_obj_why
            userstory_obj.save()
        else:
            if userstory_obj.Who_full:
                who_obj = userstory_obj.Who_full
                who_obj.Who_identifier = role_id
                who_obj.Who_action = role_act
                who_obj.Who_full = who
                who_obj.save()

            if userstory_obj.What_full:
                what_obj = userstory_obj.What_full
                what_obj.What_identifier = action_id
                what_obj.What_action = action_usr
                what_obj.What_full = what
                what_obj.save()

            if userstory_obj.Why_full:
                why_obj = userstory_obj.Why_full
                why_obj.Why_identifier = goal_id
                why_obj.Why_action = goal_usr
                why_obj.Why_full = why
                why_obj.save()
