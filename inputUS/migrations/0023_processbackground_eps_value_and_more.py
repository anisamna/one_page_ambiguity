# Generated by Django 4.2.3 on 2023-09-06 08:45

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("inputUS", "0022_processbackground"),
    ]

    operations = [
        migrations.AddField(
            model_name="processbackground",
            name="eps_value",
            field=models.CharField(max_length=10, null=True),
        ),
        migrations.AddField(
            model_name="processbackground",
            name="min_samples_value",
            field=models.CharField(max_length=10, null=True),
        ),
        migrations.AddField(
            model_name="processbackground",
            name="similarity_value",
            field=models.CharField(max_length=10, null=True),
        ),
        migrations.AddField(
            model_name="processbackground",
            name="terms_action_value",
            field=models.CharField(max_length=10, null=True),
        ),
        migrations.AddField(
            model_name="processbackground",
            name="terms_role_value",
            field=models.CharField(max_length=10, null=True),
        ),
        migrations.AddField(
            model_name="processbackground",
            name="topics_value",
            field=models.CharField(max_length=10, null=True),
        ),
    ]
