# Generated by Django 4.2.3 on 2023-09-11 13:14

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("inputUS", "0026_rename_edit_reportuserstory_recommendation_type"),
    ]

    operations = [
        migrations.AddField(
            model_name="role",
            name="status",
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
    ]