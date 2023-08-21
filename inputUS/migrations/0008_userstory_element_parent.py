# Generated by Django 4.2.3 on 2023-08-15 14:43

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    dependencies = [
        ("inputUS", "0007_alter_reportuserstory_type"),
    ]

    operations = [
        migrations.AddField(
            model_name="userstory_element",
            name="parent",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.CASCADE,
                to="inputUS.userstory_element",
            ),
        ),
    ]