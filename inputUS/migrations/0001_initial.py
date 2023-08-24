# Generated by Django 4.1.7 on 2023-07-19 09:48

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    initial = True

    dependencies = []

    operations = [
        migrations.CreateModel(
            name="Glossary",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("Action_item", models.CharField(max_length=100)),
            ],
            options={
                "verbose_name": "Glossary",
                "verbose_name_plural": "Glossary",
            },
        ),
        migrations.CreateModel(
            name="KeywordGlossary",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("keyword", models.CharField(max_length=100)),
                (
                    "item_name",
                    models.ManyToManyField(blank=True, to="inputUS.glossary"),
                ),
            ],
            options={
                "verbose_name": "Keyword_Glossary",
                "verbose_name_plural": "Keyword_Glossary",
            },
        ),
        migrations.CreateModel(
            name="Parser",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("Solution_Name", models.CharField(max_length=200, null=True)),
                ("Action_Name", models.CharField(max_length=200, null=True)),
                ("Parsing_result", models.JSONField(null=True)),
                ("results", models.TextField(null=True)),
                ("image_result", models.CharField(max_length=255, null=True)),
                ("is_lock", models.BooleanField(default=False)),
            ],
            options={
                "verbose_name": "Atomic_Parsing",
                "verbose_name_plural": "Atomic_Parsing",
            },
        ),
        migrations.CreateModel(
            name="Project",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("Project_Name", models.CharField(max_length=100)),
                ("Project_Desc", models.CharField(max_length=500)),
            ],
        ),
        migrations.CreateModel(
            name="US_Upload",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("US_File_Name", models.CharField(max_length=100)),
                ("US_File_Txt", models.FileField(null=True, upload_to="file/")),
                ("US_File_Content", models.JSONField()),
                (
                    "US_File_DateCreated",
                    models.DateTimeField(auto_now_add=True, null=True),
                ),
                (
                    "US_Project_Domain",
                    models.ForeignKey(
                        null=True,
                        on_delete=django.db.models.deletion.CASCADE,
                        to="inputUS.project",
                    ),
                ),
            ],
            options={
                "verbose_name": "Upload_UserStory",
                "verbose_name_plural": "Upload_UserStory",
            },
        ),
        migrations.CreateModel(
            name="UserStory_element",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("UserStory_Full_Text", models.CharField(max_length=800, null=True)),
                ("is_processed", models.BooleanField(default=False)),
                (
                    "Project_Name",
                    models.ForeignKey(
                        null=True,
                        on_delete=django.db.models.deletion.CASCADE,
                        to="inputUS.project",
                    ),
                ),
                (
                    "UserStory_File_ID",
                    models.ForeignKey(
                        null=True,
                        on_delete=django.db.models.deletion.CASCADE,
                        to="inputUS.us_upload",
                    ),
                ),
            ],
            options={
                "verbose_name": "Segmented_UserStory",
                "verbose_name_plural": "Segmented_UserStory",
            },
        ),
        migrations.CreateModel(
            name="UserStory_What",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("What_identifier", models.CharField(max_length=100)),
                ("What_action", models.CharField(max_length=500)),
                ("What_full", models.CharField(max_length=800)),
                ("Element_type", models.CharField(max_length=100)),
            ],
        ),
        migrations.CreateModel(
            name="UserStory_Who",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("Who_identifier", models.CharField(max_length=100)),
                ("Who_action", models.CharField(max_length=500)),
                ("Who_full", models.CharField(max_length=800)),
                ("Element_type", models.CharField(max_length=100)),
            ],
        ),
        migrations.CreateModel(
            name="UserStory_Why",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("Why_identifier", models.CharField(max_length=100)),
                ("Why_action", models.CharField(max_length=500)),
                ("Why_full", models.CharField(max_length=800)),
                ("Element_type", models.CharField(max_length=100)),
            ],
        ),
        migrations.CreateModel(
            name="Well_Formed",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("Solution_Name", models.CharField(max_length=200, null=True)),
                ("Action_Name", models.CharField(max_length=200, null=True)),
                ("result_desc", models.CharField(max_length=200, null=True)),
                (
                    "UserStory_Segment_ID",
                    models.ForeignKey(
                        null=True,
                        on_delete=django.db.models.deletion.CASCADE,
                        to="inputUS.userstory_element",
                    ),
                ),
            ],
            options={
                "verbose_name": "Well_Formed",
                "verbose_name_plural": "Well_Formed",
            },
        ),
        migrations.CreateModel(
            name="Concise_for_brackets",
            fields=[
                (
                    "parser_ptr",
                    models.OneToOneField(
                        auto_created=True,
                        on_delete=django.db.models.deletion.CASCADE,
                        parent_link=True,
                        primary_key=True,
                        serialize=False,
                        to="inputUS.parser",
                    ),
                ),
                ("Text_Improvement", models.CharField(max_length=10000)),
            ],
            options={
                "abstract": False,
            },
            bases=("inputUS.parser",),
        ),
        migrations.CreateModel(
            name="WordNet_classification",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("Solution_Name", models.CharField(max_length=200, null=True)),
                ("Action_Name", models.CharField(max_length=200, null=True)),
                ("Keyword_Glossary_name", models.CharField(max_length=100, null=True)),
                ("Item_Glossary_name", models.CharField(max_length=100, null=True)),
                (
                    "Keyword_Glossary",
                    models.ManyToManyField(blank=True, to="inputUS.keywordglossary"),
                ),
                (
                    "well_formed",
                    models.ForeignKey(
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        to="inputUS.well_formed",
                    ),
                ),
            ],
            options={
                "verbose_name": "Precise_WordNet_Lexical",
                "verbose_name_plural": "Precise_WordNet_Lexical",
            },
        ),
        migrations.AddField(
            model_name="userstory_element",
            name="What_full",
            field=models.ForeignKey(
                null=True,
                on_delete=django.db.models.deletion.CASCADE,
                to="inputUS.userstory_what",
            ),
        ),
        migrations.AddField(
            model_name="userstory_element",
            name="Who_full",
            field=models.ForeignKey(
                null=True,
                on_delete=django.db.models.deletion.CASCADE,
                to="inputUS.userstory_who",
            ),
        ),
        migrations.AddField(
            model_name="userstory_element",
            name="Why_full",
            field=models.ForeignKey(
                null=True,
                on_delete=django.db.models.deletion.CASCADE,
                to="inputUS.userstory_why",
            ),
        ),
        migrations.CreateModel(
            name="TopicModeling",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                (
                    "TopicModeling_element_name",
                    models.CharField(
                        choices=[
                            ("Role", "Role"),
                            ("Action", "Action"),
                            (
                                "[('Role', 'role', 'Who-'), ('Action', 'action', 'What-')]",
                                "Element",
                            ),
                        ],
                        max_length=100,
                        null=True,
                    ),
                ),
                ("result_model", models.JSONField(null=True)),
                (
                    "UserStory_Segment_ID_fk",
                    models.ForeignKey(
                        null=True,
                        on_delete=django.db.models.deletion.CASCADE,
                        to="inputUS.userstory_element",
                    ),
                ),
            ],
            options={
                "verbose_name": "Conceptual_Topic_Modeling",
                "verbose_name_plural": "Conceptual_Topic_Modeling",
            },
        ),
        migrations.CreateModel(
            name="Similarity_Analysis",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("Solution_Name", models.CharField(max_length=200, null=True)),
                ("Action_Name", models.CharField(max_length=200, null=True)),
                ("Actor_Who_1", models.CharField(max_length=100)),
                ("Actor_Who_2", models.CharField(max_length=100, null=True)),
                ("Action_What_1", models.CharField(max_length=500)),
                ("Action_What_2", models.CharField(max_length=500, null=True)),
                (
                    "sim_Score_Actor_who",
                    models.FloatField(blank=True, default=None, null=True),
                ),
                (
                    "sim_Score_Action_what",
                    models.FloatField(blank=True, default=None, null=True),
                ),
                (
                    "sim_Score_Sum",
                    models.FloatField(blank=True, default=None, null=True),
                ),
                ("min_threshold", models.IntegerField(blank=True, null=True)),
                (
                    "Well_Formed_1",
                    models.ForeignKey(
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        related_name="well_formed_a_set",
                        to="inputUS.well_formed",
                    ),
                ),
                (
                    "Well_Formed_2",
                    models.ForeignKey(
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        related_name="well_formed_b_set",
                        to="inputUS.well_formed",
                    ),
                ),
            ],
            options={
                "verbose_name": "Similarity Analysis",
                "verbose_name_plural": "Similarity Analysis",
            },
        ),
        migrations.CreateModel(
            name="ParsingDetail",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("Text_improvement", models.CharField(max_length=1000)),
                ("is_selected", models.BooleanField(default=False)),
                ("is_manual", models.BooleanField(default=False)),
                (
                    "Parsing_ID_fk",
                    models.ForeignKey(
                        null=True,
                        on_delete=django.db.models.deletion.CASCADE,
                        to="inputUS.parser",
                    ),
                ),
            ],
            options={
                "verbose_name": "Atomic_Parsing_Detail",
                "verbose_name_plural": "Atomic_Parsing_Detail",
            },
        ),
        migrations.AddField(
            model_name="parser",
            name="well_formed",
            field=models.ForeignKey(
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                to="inputUS.well_formed",
            ),
        ),
        migrations.CreateModel(
            name="N_gram",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("N_gram_method_name", models.BooleanField(default=False)),
                ("number_top_gram", models.IntegerField()),
                ("n_gram_result", models.JSONField()),
                ("n_gram_result_type", models.CharField(max_length=100)),
                (
                    "UserStory_element_name",
                    models.ForeignKey(
                        null=True,
                        on_delete=django.db.models.deletion.CASCADE,
                        to="inputUS.userstory_element",
                    ),
                ),
            ],
            options={
                "verbose_name": "N_gram",
                "verbose_name_plural": "N_gram",
            },
        ),
        migrations.CreateModel(
            name="Conceptual",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("Solution_Name", models.CharField(max_length=200, null=True)),
                ("Action_Name", models.CharField(max_length=200, null=True)),
                ("subject", models.CharField(max_length=100, null=True)),
                ("predicate", models.CharField(max_length=500, null=True)),
                ("object", models.CharField(max_length=150, null=True)),
                (
                    "well_formed",
                    models.ForeignKey(
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        to="inputUS.well_formed",
                    ),
                ),
            ],
            options={
                "abstract": False,
            },
        ),
        migrations.CreateModel(
            name="Coherence_lex",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("Solution_Name", models.CharField(max_length=200, null=True)),
                ("Action_Name", models.CharField(max_length=200, null=True)),
                ("result", models.JSONField(null=True)),
                ("coherence_score", models.JSONField(null=True)),
                ("documents", models.CharField(max_length=255, null=True)),
                ("label", models.IntegerField(null=True)),
                (
                    "well_formed",
                    models.ForeignKey(
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        to="inputUS.well_formed",
                    ),
                ),
            ],
            options={
                "abstract": False,
            },
        ),
    ]
