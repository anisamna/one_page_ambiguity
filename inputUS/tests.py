from django.test import TestCase
from inputUS.models import Project, UserStory_element, Glossary, KeywordGlossary

# from functions.analysis_userstory import AnalysisData

# def test_analysis(project_id):
#     project_ = Project.objects.get(id=project_id)
#     userstory_list = UserStory_element.objects.filter(Project_Name=project_).values_list('id', flat=True)
#     story_list_id = list(set(userstory_list))
#     print(story_list_id)
#     AnalysisData(story_list_id).start()


def test_create_keyword():
    keywords = {
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

    for word_class, class_keywords in keywords.items():
        print(word_class, class_keywords)
        keyword, created = KeywordGlossary.objects.get_or_create(keyword=word_class)
        for item in class_keywords:
            print(item)
            glossary, created = Glossary.objects.get_or_create(Action_item=item)
            keyword.item_name.add(glossary)
            keyword.save()
