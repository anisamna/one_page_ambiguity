# Generated by Django 4.2.3 on 2023-08-24 18:17

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("inputUS", "0015_remove_reportterms_roles_role_project"),
    ]

    operations = [
        migrations.RemoveField(
            model_name="reportterms",
            name="glossarys",
        ),
        migrations.RemoveField(
            model_name="reportterms",
            name="keyword",
        ),
        migrations.AddField(
            model_name="reportterms",
            name="action",
            field=models.CharField(max_length=100, null=True),
        ),
        migrations.AddField(
            model_name="reportterms",
            name="terms_actions",
            field=models.JSONField(null=True),
        ),
        migrations.AddField(
            model_name="reportterms",
            name="type",
            field=models.IntegerField(
                choices=[
                    (1, "Well Formed"),
                    (2, "Atomicity"),
                    (3, "Preciseness"),
                    (4, "Consistency"),
                    (5, "Conceptually Sound"),
                    (6, "Uniqueness"),
                ],
                null=True,
            ),
        ),
        migrations.AlterField(
            model_name="reportterms",
            name="userstory",
            field=models.ForeignKey(
                null=True,
                on_delete=django.db.models.deletion.CASCADE,
                to="inputUS.userstory_element",
            ),
        ),
    ]