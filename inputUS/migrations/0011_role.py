# Generated by Django 4.2.3 on 2023-08-24 12:40

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("inputUS", "0010_project_created_at_project_created_by_and_more"),
    ]

    operations = [
        migrations.CreateModel(
            name="Role",
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
                ("role", models.CharField(max_length=100, null=True)),
            ],
            options={
                "verbose_name": "Role",
                "verbose_name_plural": "Role",
            },
        ),
    ]
