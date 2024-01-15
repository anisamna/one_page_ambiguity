# Generated by Django 4.2.3 on 2024-01-11 04:31

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('inputUS', '0038_userstory_element_is_agree'),
    ]

    operations = [
        migrations.AddField(
            model_name='reportuserstory',
            name='disagree_comment',
            field=models.CharField(max_length=500, null=True),
        ),
        migrations.AddField(
            model_name='reportuserstory',
            name='is_agree',
            field=models.BooleanField(null=True),
        ),
        migrations.AddField(
            model_name='reportuserstory',
            name='is_submited',
            field=models.BooleanField(default=False),
        ),
        migrations.AlterField(
            model_name='reportuserstory',
            name='classification',
            field=models.CharField(max_length=500, null=True),
        ),
        migrations.AlterField(
            model_name='reportuserstory',
            name='predicate',
            field=models.CharField(max_length=500, null=True),
        ),
        migrations.AlterField(
            model_name='reportuserstory',
            name='status',
            field=models.CharField(blank=True, max_length=500, null=True),
        ),
        migrations.AlterField(
            model_name='reportuserstory',
            name='subject',
            field=models.CharField(max_length=500, null=True),
        ),
    ]