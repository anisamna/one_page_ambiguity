# Generated by Django 4.2.3 on 2023-10-16 06:58

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("inputUS", "0032_alter_adjusteduserstory_status_and_more"),
    ]

    operations = [
        migrations.AddField(
            model_name="reportterms",
            name="problem_action",
            field=models.JSONField(null=True),
        ),
    ]