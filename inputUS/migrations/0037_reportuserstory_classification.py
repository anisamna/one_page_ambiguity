# Generated by Django 4.2.3 on 2023-10-29 16:57

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("inputUS", "0036_personas_key_name"),
    ]

    operations = [
        migrations.AddField(
            model_name="reportuserstory",
            name="classification",
            field=models.CharField(max_length=255, null=True),
        ),
    ]
