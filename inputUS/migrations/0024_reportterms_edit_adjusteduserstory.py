# Generated by Django 4.2.3 on 2023-09-08 06:40

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ("inputUS", "0023_processbackground_eps_value_and_more"),
    ]

    operations = [
        migrations.AddField(
            model_name="reportterms",
            name="edit",
            field=models.IntegerField(
                choices=[
                    (1, "Action"),
                    (2, "Role"),
                    (3, "Action and Role"),
                    (4, "None"),
                ],
                null=True,
            ),
        ),
        migrations.CreateModel(
            name="AdjustedUserStory",
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
                ("created_at", models.DateTimeField(auto_now_add=True, null=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("userstory_text", models.CharField(max_length=800, null=True)),
                ("adjusted", models.CharField(max_length=800, null=True)),
                (
                    "status",
                    models.IntegerField(
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
                (
                    "created_by",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        related_name="%(app_label)s_%(class)s_create_by_user",
                        to=settings.AUTH_USER_MODEL,
                        verbose_name="Dibuat Oleh",
                    ),
                ),
                (
                    "userstory",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        to="inputUS.userstory_element",
                    ),
                ),
            ],
            options={
                "verbose_name": "Adjusted User Story",
                "verbose_name_plural": "Adjusted User Story",
            },
        ),
    ]
