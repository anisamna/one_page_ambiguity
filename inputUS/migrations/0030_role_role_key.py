# Generated by Django 4.2.3 on 2023-09-14 05:34

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("inputUS", "0029_reportuserstory_predicate_reportuserstory_subject"),
    ]

    operations = [
        migrations.AddField(
            model_name="role",
            name="role_key",
            field=models.CharField(max_length=100, null=True),
        ),
    ]