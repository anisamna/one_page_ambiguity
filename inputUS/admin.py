from django.contrib import admin

# Register your models here.
from inputUS.models import (  # Well_Formed,; N_gram,; Parser,; ParsingDetail,; Concise_for_brackets,; Conceptual,; Coherence_lex,
    Glossary,
    KeywordGlossary,
    Project,
    ReportUserStory,
    Role,
    Similarity_Analysis,
    US_Upload,
    UserStory_element,
    UserStory_What,
    UserStory_Who,
    UserStory_Why,
    WordNet_classification,
)

admin.site.register(US_Upload)
# admin.site.register(Well_Formed)
# admin.site.register(N_gram)
# admin.site.register(Concise_for_brackets)
# admin.site.register(Conceptual)
# admin.site.register(Coherence_lex)


class ParserAdmin(admin.ModelAdmin):
    list_display = ("id", "results", "well_formed", "Solution_Name", "Action_Name")


# admin.site.register(Parser, ParserAdmin)
# admin.site.register(ParsingDetail)


class GlossaryAdmin(admin.ModelAdmin):
    list_display = ("id", "Action_item")
    search_fields = ("Action_item",)


admin.site.register(Glossary, GlossaryAdmin)


class KeywordGlossaryAdmin(admin.ModelAdmin):
    list_display = ("id", "keyword")
    fieldsets = (
        (
            None,
            {
                "fields": (
                    "keyword",
                    "item_name",
                ),
            },
        ),
    )


admin.site.register(KeywordGlossary, KeywordGlossaryAdmin)


class WordNet_classificationAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "well_formed",
        # "WordNet_element_type",
        "get_Keyword_Glossary",
        "Item_Glossary_name",
        "Status_Name",
        "Recommendation_Name",
    )

    def get_Keyword_Glossary(self, obj):
        data_list = []
        if obj.Keyword_Glossary.all().exists():
            for item in obj.Keyword_Glossary.all():
                data_list.append(item.keyword)
        return ", ".join(data_list)

    get_Keyword_Glossary.short_description = "Keyword_Glossary"


admin.site.register(WordNet_classification, WordNet_classificationAdmin)


class ProjectAdmin(admin.ModelAdmin):
    list_display = ("id", "Project_Name", "Project_Desc")


admin.site.register(Project, ProjectAdmin)


class UserStory_WhoAdmin(admin.ModelAdmin):
    list_display = ("id", "Who_identifier", "Who_action", "Who_full", "Element_type")


admin.site.register(UserStory_Who, UserStory_WhoAdmin)


class UserStory_WhatAdmin(admin.ModelAdmin):
    list_display = ("id", "What_identifier", "What_action", "What_full", "Element_type")


admin.site.register(UserStory_What, UserStory_WhatAdmin)


class UserStory_WhyAdmin(admin.ModelAdmin):
    list_display = ("id", "Why_identifier", "Why_action", "Why_full", "Element_type")


admin.site.register(UserStory_Why, UserStory_WhyAdmin)


class UserStory_elementAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "UserStory_Full_Text",
        "Who_full",
        "What_full",
        "Why_full",
        "Project_Name",
        "UserStory_File_ID",
        "parent",
    )


admin.site.register(UserStory_element, UserStory_elementAdmin)


class Similarity_AnalysisAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "Well_Formed_1",
        "Well_Formed_2",
        "Actor_Who_1",
        "Actor_Who_2",
        "Action_What_1",
        "Action_What_2",
        "sim_Score_Actor_who",
        "sim_Score_Action_what",
        "sim_Score_Sum",
        "min_threshold",
    )


admin.site.register(Similarity_Analysis, Similarity_AnalysisAdmin)


@admin.register(ReportUserStory)
class ReportUserStoryAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "userstory",
        "status",
        "recommendation",
        "description",
        "type",
    )
    list_filter = ("userstory__Project_Name", "type")
    search_fields = ("userstory__UserStory_Full_Text", "status", "recommendation")


@admin.register(Role)
class RoleAdmin(admin.ModelAdmin):
    list_display = ("id", "role")
