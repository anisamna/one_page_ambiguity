# Generated by Django 4.2.3 on 2023-09-06 07:36

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    dependencies = [
        ("inputUS", "0020_alter_userstory_element_what_full_and_more"),
    ]

    operations = [
        migrations.AlterField(
            model_name="userstory_element",
            name="What_full",
            field=models.ForeignKey(
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                to="inputUS.userstory_what",
            ),
        ),
        migrations.AlterField(
            model_name="userstory_element",
            name="Who_full",
            field=models.ForeignKey(
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                to="inputUS.userstory_who",
            ),
        ),
        migrations.AlterField(
            model_name="userstory_element",
            name="Why_full",
            field=models.ForeignKey(
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                to="inputUS.userstory_why",
            ),
        ),
    ]