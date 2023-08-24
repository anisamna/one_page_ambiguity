# Generated by Django 4.1.7 on 2023-07-23 12:01

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    dependencies = [
        ("inputUS", "0001_initial"),
    ]

    operations = [
        migrations.CreateModel(
            name="Result",
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
                ("Status_Name", models.CharField(max_length=200, null=True)),
                ("Recommendation_Name", models.CharField(max_length=200, null=True)),
                ("Recommendation_Desc", models.CharField(max_length=200, null=True)),
            ],
            options={
                "verbose_name": "Result",
                "verbose_name_plural": "Results",
            },
        ),
        migrations.RemoveField(
            model_name="conceptual",
            name="well_formed",
        ),
        migrations.RemoveField(
            model_name="concise_for_brackets",
            name="parser_ptr",
        ),
        migrations.RemoveField(
            model_name="n_gram",
            name="UserStory_element_name",
        ),
        migrations.RemoveField(
            model_name="parser",
            name="well_formed",
        ),
        migrations.RemoveField(
            model_name="parsingdetail",
            name="Parsing_ID_fk",
        ),
        migrations.RemoveField(
            model_name="topicmodeling",
            name="UserStory_Segment_ID_fk",
        ),
        migrations.RemoveField(
            model_name="well_formed",
            name="UserStory_Segment_ID",
        ),
        migrations.AlterModelOptions(
            name="userstory_element",
            options={"verbose_name": "UserStory", "verbose_name_plural": "UserStories"},
        ),
        migrations.RenameField(
            model_name="similarity_analysis",
            old_name="Action_Name",
            new_name="Recommendation_Name",
        ),
        migrations.RenameField(
            model_name="similarity_analysis",
            old_name="Solution_Name",
            new_name="Status_Name",
        ),
        migrations.RenameField(
            model_name="wordnet_classification",
            old_name="Action_Name",
            new_name="Recommendation_Name",
        ),
        migrations.RenameField(
            model_name="wordnet_classification",
            old_name="Solution_Name",
            new_name="Status_Name",
        ),
        migrations.DeleteModel(
            name="Coherence_lex",
        ),
        migrations.DeleteModel(
            name="Conceptual",
        ),
        migrations.DeleteModel(
            name="Concise_for_brackets",
        ),
        migrations.DeleteModel(
            name="N_gram",
        ),
        migrations.DeleteModel(
            name="Parser",
        ),
        migrations.DeleteModel(
            name="ParsingDetail",
        ),
        migrations.DeleteModel(
            name="TopicModeling",
        ),
        migrations.AddField(
            model_name="result",
            name="UserStory_Segment_ID",
            field=models.ForeignKey(
                null=True,
                on_delete=django.db.models.deletion.CASCADE,
                to="inputUS.userstory_element",
            ),
        ),
        migrations.AlterField(
            model_name="similarity_analysis",
            name="Well_Formed_1",
            field=models.ForeignKey(
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name="well_formed_a_set",
                to="inputUS.result",
            ),
        ),
        migrations.AlterField(
            model_name="similarity_analysis",
            name="Well_Formed_2",
            field=models.ForeignKey(
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name="well_formed_b_set",
                to="inputUS.result",
            ),
        ),
        migrations.AlterField(
            model_name="wordnet_classification",
            name="well_formed",
            field=models.ForeignKey(
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                to="inputUS.result",
            ),
        ),
        migrations.DeleteModel(
            name="Well_Formed",
        ),
    ]
