from django.contrib.auth.models import User
from django.db import models
from django.db.models import JSONField
from django.db.models.signals import pre_delete
from django.dispatch import receiver


class MetaAttribute(models.Model):
    created_by = models.ForeignKey(
        User,
        related_name="%(app_label)s_%(class)s_create_by_user",
        verbose_name="Dibuat Oleh",
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
    )
    created_at = models.DateTimeField(auto_now_add=True, null=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


class Glossary(models.Model):
    # Action_keywords = models.ManyToManyField(Keyword, through="KeywordGlossary")
    Action_item = models.CharField(max_length=100)

    def __str__(self):
        return self.Action_item

    class Meta:
        verbose_name = "Glossary"
        verbose_name_plural = "Glossary"


class KeywordGlossary(models.Model):
    # keyword = models.ForeignKey(Keyword, on_delete=models.CASCADE)
    keyword = models.CharField(max_length=100)
    item_name = models.ManyToManyField(Glossary, blank=True)

    def __str__(self):
        return self.keyword

    class Meta:
        verbose_name = "Keyword_Glossary"
        verbose_name_plural = "Keyword_Glossary"


class Project(MetaAttribute):
    Project_Name = models.CharField(max_length=100)
    Project_Desc = models.CharField(max_length=500)

    def __str__(self):
        return self.Project_Name


class US_Upload(MetaAttribute):
    US_File_Name = models.CharField(max_length=100)
    US_File_Txt = models.FileField(upload_to="file/", null=True)
    US_File_Content = JSONField()
    US_File_DateCreated = models.DateTimeField(auto_now_add=True, null=True)
    US_Project_Domain = models.ForeignKey(Project, on_delete=models.CASCADE, null=True)
    is_show = models.BooleanField(default=True)

    def __str__(self):
        return self.US_File_Name

    class Meta:
        verbose_name = "Upload_UserStory"
        verbose_name_plural = "Upload_UserStory"


class UserStory_Who(models.Model):
    Who_identifier = models.CharField(max_length=100)
    Who_action = models.CharField(max_length=500)
    Who_full = models.CharField(max_length=800)
    Element_type = models.CharField(max_length=100)

    def __str__(self):
        return self.Who_full


class UserStory_What(models.Model):
    What_identifier = models.CharField(max_length=100)
    What_action = models.CharField(max_length=500)
    What_full = models.CharField(max_length=800)
    Element_type = models.CharField(max_length=100)

    def __str__(self):
        return self.What_full


class UserStory_Why(models.Model):
    Why_identifier = models.CharField(max_length=100)
    Why_action = models.CharField(max_length=500)
    Why_full = models.CharField(max_length=800)
    Element_type = models.CharField(max_length=100)

    def __str__(self):
        return self.Why_full


class UserStory_element(MetaAttribute):
    Who_full = models.ForeignKey(UserStory_Who, on_delete=models.SET_NULL, null=True)
    What_full = models.ForeignKey(UserStory_What, on_delete=models.SET_NULL, null=True)
    Why_full = models.ForeignKey(UserStory_Why, on_delete=models.SET_NULL, null=True)
    UserStory_Full_Text = models.CharField(max_length=800, null=True)
    old_userstory = models.CharField(max_length=800, null=True)
    Project_Name = models.ForeignKey(Project, on_delete=models.CASCADE, null=True)
    UserStory_File_ID = models.ForeignKey(
        US_Upload, on_delete=models.CASCADE, null=True
    )
    is_processed = models.BooleanField(default=False)
    is_problem = models.BooleanField(default=False)
    is_agree = models.BooleanField(default=False)
    parent = models.ForeignKey("self", on_delete=models.CASCADE, null=True, blank=True)

    def __str__(self):
        return self.UserStory_Full_Text

    def get_report_list(self):
        return self.reportuserstory_set.filter(userstory__is_processed=True).order_by(
            "userstory", "id"
        )

    def get_count_report(self):
        return self.get_report_list().count() + 1

    def get_childrens(self):
        return self.userstory_element_set.all()

    class Meta:
        verbose_name = "UserStory"
        verbose_name_plural = "UserStories"


# class US_SolutionAndAction_common(models.Model):
#     #Solution_Name = models.CharField(max_length=200, choices=US_Solution.choices, null=True)
#     Solution_Name = models.CharField(max_length=200, null=True)
#     Action_Name = models.CharField(max_length=200, null=True)

#     class Meta:
#         abstract = True


class Result(models.Model):  # deprecated
    UserStory_Segment_ID = models.ForeignKey(
        UserStory_element, on_delete=models.CASCADE, null=True
    )
    Status_Name = models.CharField(max_length=200, null=True)
    Recommendation_Name = models.CharField(max_length=200, null=True)
    Recommendation_Desc = models.CharField(max_length=200, null=True)
    # result_name = models.CharField(max_length=100)

    def __str__(self):
        if self.UserStory_Segment_ID:
            return str(self.UserStory_Segment_ID)
        return self.Recommendation_Desc

    class Meta:
        verbose_name = "Result"
        verbose_name_plural = "Results"


# class N_gram(models.Model):
#     UserStory_element_name = models.ForeignKey(UserStory_element, on_delete=models.CASCADE, null=True)
#     N_gram_method_name = models.BooleanField(default=False)
#     number_top_gram = models.IntegerField()
#     n_gram_result = JSONField()
#     n_gram_result_type = models.CharField(max_length=100)

#     class Meta:
#         verbose_name = 'N_gram'
#         verbose_name_plural = 'N_gram'


class Similarity_Analysis(models.Model):  # deprecated
    # UserStory_Segment_ID_1 = models.ForeignKey(UserStory_element, on_delete=models.CASCADE, null=True)
    Well_Formed_1 = models.ForeignKey(
        Result, on_delete=models.SET_NULL, null=True, related_name="well_formed_a_set"
    )
    Well_Formed_2 = models.ForeignKey(
        Result, on_delete=models.SET_NULL, null=True, related_name="well_formed_b_set"
    )
    Actor_Who_1 = models.CharField(max_length=100)
    Actor_Who_2 = models.CharField(max_length=100, null=True)
    Action_What_1 = models.CharField(max_length=500)
    Action_What_2 = models.CharField(max_length=500, null=True)
    sim_Score_Actor_who = models.FloatField(null=True, blank=True, default=None)
    sim_Score_Action_what = models.FloatField(null=True, blank=True, default=None)
    sim_Score_Sum = models.FloatField(null=True, blank=True, default=None)
    min_threshold = models.IntegerField(null=True, blank=True)
    Status_Name = models.CharField(max_length=200, null=True)
    Recommendation_Name = models.CharField(max_length=200, null=True)

    class Meta:
        verbose_name = "Similarity Analysis"
        verbose_name_plural = "Similarity Analysis"


# class Parser(US_SolutionAndAction_common):
#     Parsing_result = JSONField(null=True)
#     results = models.TextField(null=True)
#     image_result = models.CharField(null=True, max_length=255)
#     #Parsing_desc = models.CharField(max_length=200)
#     # UserStory_Segment_ID_fk = models.ForeignKey(UserStory_element, on_delete=models.CASCADE, null=True)
#     well_formed = models.ForeignKey(Well_Formed, on_delete=models.SET_NULL, null=True)
#     is_lock = models.BooleanField(default=False) # is lock digunakan untuk mengunci data parsing detail

#     def __str__(self):
#         if self.results:
#             return self.results
#         return str(self.id)

#     class Meta:
#         verbose_name = "Atomic_Parsing"
#         verbose_name_plural = "Atomic_Parsing"


# class ParsingDetail(models.Model):
#     Parsing_ID_fk = models.ForeignKey(Parser, on_delete=models.CASCADE, null=True)
#     Text_improvement = models.CharField(max_length=1000)
#     is_selected = models.BooleanField(default=False) # jika Parsing detail dipilih user
#     is_manual = models.BooleanField(default=False) # jika Parsing detail diinputkan secara manual

#     def __str__(self):
#         if self.Text_improvement:
#             return self.Text_improvement
#         return str(self.id)

#     class Meta:
#         verbose_name = 'Atomic_Parsing_Detail'
#         verbose_name_plural = 'Atomic_Parsing_Detail'


# class Concise_for_brackets(Parser):
#     Text_Improvement = models.CharField(max_length=10000)


# class Conceptual(US_SolutionAndAction_common):
#     well_formed = models.ForeignKey(Well_Formed, on_delete=models.SET_NULL, null=True)
#     subject = models.CharField(max_length=100, null=True)
#     predicate = models.CharField(max_length=500, null=True)
#     object = models.CharField(max_length=150, null=True)

# class Coherence_lex(US_SolutionAndAction_common):
#     well_formed = models.ForeignKey(Well_Formed, on_delete=models.SET_NULL, null=True)
#     result = models.JSONField(null=True)
#     coherence_score = models.JSONField(null=True)
#     documents = models.CharField(max_length=255, null=True)
#     label = models.IntegerField(null=True)


class WordNet_classification(models.Model):  # deprecated
    class Element_type(models.TextChoices):
        ROLE = "Role"
        ACTION = "Action"

        Element = [(ROLE, "role", "Who-"), (ACTION, "action", "What-")]

    # UserStory_Element_Name = models.ForeignKey(UserStory_element, on_delete=models.CASCADE, null=True)
    well_formed = models.ForeignKey(Result, on_delete=models.SET_NULL, null=True)
    # WordNet_element_type = models.CharField(max_length=100, choices=Element_type.choices, null=True)
    # Keyword_Glossary_ID = models.ForeignKey(KeywordGlossary, on_delete=models.CASCADE, null=True)
    Keyword_Glossary_name = models.CharField(max_length=100, null=True)
    Keyword_Glossary = models.ManyToManyField(KeywordGlossary, blank=True)
    Item_Glossary_name = models.CharField(max_length=100, null=True)
    Status_Name = models.CharField(max_length=200, null=True)
    Recommendation_Name = models.CharField(max_length=200, null=True)

    class Meta:
        verbose_name = "Precise_WordNet_Lexical"
        verbose_name_plural = "Precise_WordNet_Lexical"


# class TopicModeling(models.Model):
#     class Element_type(models.TextChoices):
#         ROLE = 'Role'
#         ACTION = 'Action'

#         Element = [
#             (ROLE, 'role', 'Who-'),
#             (ACTION, 'action', 'What-')
#         ]
#     #group_number = models.CharField(max_length=10)
#     #Coherence_score = models.FloatField()
#     UserStory_Segment_ID_fk = models.ForeignKey(UserStory_element, on_delete=models.CASCADE, null=True)
#     TopicModeling_element_name = models.CharField(max_length=100, choices=Element_type.choices, null=True)
#     result_model = JSONField(null=True)

#     class Meta:
#         verbose_name = "Conceptual_Topic_Modeling"
#         verbose_name_plural = "Conceptual_Topic_Modeling"


class ReportUserStory(MetaAttribute):
    class RECOMENDATION_TYPE(models.IntegerChoices):
        ACTION = 1, "Action"
        ROLE = 2, "Role"
        ACTION_ROLE = 3, "Action and Role"
        NONE = (
            4,
            "None",
        )
        ACTION_MANUAL = 5, "Action Manual"

    class ANALYS_TYPE(models.IntegerChoices):
        WELL_FORMED = 1, "Well-Formedness"
        ATOMICITY = 2, "Atomicity"
        CONCISENESS = 7, "Conciseness"
        PRECISE = 3, "Preciseness"
        CONSISTENT = 4, "Consistency"
        CONCEPTUALLY = 5, "Conceptually Sound"
        UNIQUENESS = 6, "Uniqueness"

    userstory = models.ForeignKey(UserStory_element, on_delete=models.CASCADE)
    status = models.CharField(max_length=500, null=True, blank=True)
    recommendation = models.TextField(null=True, blank=True)
    description = models.TextField(null=True, blank=True)
    type = models.IntegerField(choices=ANALYS_TYPE.choices, null=True)
    is_problem = models.BooleanField(default=False)
    recommendation_type = models.IntegerField(
        choices=RECOMENDATION_TYPE.choices, null=True
    )
    subject = models.CharField(max_length=500, null=True)
    predicate = models.CharField(max_length=500, null=True)
    classification = models.CharField(max_length=500, null=True)
    is_submited = models.BooleanField(default=False)
    is_agree = models.BooleanField(null=True)
    disagree_comment = models.CharField(max_length=500, null=True)

    def __str__(self):
        if self.userstory and self.status:
            return f"{str(self.userstory)} - {self.status}"
        return str(self.id)

    class Meta:
        verbose_name = "Report User Story"
        verbose_name_plural = "Report User Story"


class Role(models.Model):
    role = models.CharField(max_length=100, null=True)
    role_key = models.CharField(max_length=100, null=True)
    userstory = models.ForeignKey(
        UserStory_element, null=True, on_delete=models.CASCADE
    )
    status = models.IntegerField(choices=ReportUserStory.ANALYS_TYPE.choices, null=True)

    def __str__(self):
        return self.role

    class Meta:
        verbose_name = "Role"
        verbose_name_plural = "Role"


class ReportTerms(MetaAttribute):
    userstory = models.ForeignKey(
        UserStory_element, null=True, on_delete=models.CASCADE
    )
    type = models.IntegerField(choices=ReportUserStory.ANALYS_TYPE.choices, null=True)
    action = models.CharField(null=True, max_length=100)  # deprecated
    problem_action = models.JSONField(null=True)
    terms_actions = models.JSONField(null=True)
    sbar_text = models.CharField(null=True, max_length=200)

    class Meta:
        verbose_name = "Report Terms"
        verbose_name_plural = "Report Terms"


class ProcessBackground(MetaAttribute):  # deprecated
    userstorys = models.ManyToManyField(UserStory_element)
    percentage = models.CharField(max_length=7, null=True)
    is_process = models.BooleanField(default=False)
    is_done = models.BooleanField(default=False)
    eps_value = models.CharField(max_length=10, null=True)
    min_samples_value = models.CharField(max_length=10, null=True)
    terms_role_value = models.CharField(max_length=10, null=True)
    terms_action_value = models.CharField(max_length=10, null=True)
    topics_value = models.CharField(max_length=10, null=True)
    similarity_value = models.CharField(max_length=10, null=True)
    description = models.TextField(null=True)

    def get_userstory_text(self):
        userstorys = self.userstorys.all()
        if userstorys.exists():
            if userstorys.count() > 5:
                return f"{userstorys.count()} user stories"
            else:
                data = []
                for item in userstorys:
                    if item.UserStory_Full_Text:
                        data.append(item.UserStory_Full_Text)
                return ", ".join(data)
        return "-"

    class Meta:
        verbose_name = "Process Background"
        verbose_name_plural = "Process Background"


class AdjustedUserStory(MetaAttribute):
    userstory = models.ForeignKey(UserStory_element, on_delete=models.CASCADE)
    userstory_text = models.CharField(max_length=800, null=True)
    adjusted = models.CharField(max_length=800, null=True)
    status = models.IntegerField(choices=ReportUserStory.ANALYS_TYPE.choices, null=True)

    def save(self, *args, **kwargs):
        # self.userstory_text = self.userstory.UserStory_Full_Text if self.userstory else None
        super(AdjustedUserStory, self).save(*args, **kwargs)

    class Meta:
        verbose_name = "Adjusted User Story"
        verbose_name_plural = "Adjusted User Story"


@receiver(pre_delete, sender=UserStory_element)
def on_delete_userstory_handler(sender, instance, **kwargs):
    print("*** DELETE WHO, WHAT, WHY DATA ***")

    try:
        if instance.Who_full:
            instance.Who_full.delete()
    except:
        pass
    try:
        if instance.What_full:
            instance.What_full.delete()
    except:
        pass
    try:
        if instance.Why_full:
            instance.Why_full.delete()
    except:
        pass


class NameFileUsed(MetaAttribute):
    name_file = models.ForeignKey(US_Upload, on_delete=models.CASCADE)
    is_active = models.BooleanField(default=True)

    class Meta:
        verbose_name = "Name File Used"
        verbose_name_plural = "Name File Used"


class Personas(MetaAttribute):
    key_name = models.CharField(max_length=200, null=True)
    persona = models.CharField(max_length=200, null=True)
    project = models.ForeignKey(Project, on_delete=models.CASCADE, null=True)
    file_name = models.ForeignKey(US_Upload, on_delete=models.CASCADE, null=True)

    def __str__(self):
        if self.persona:
            return self.persona
        return str(self.persona)

    class Meta:
        verbose_name = "Personas"
        verbose_name_plural = "Personas"
