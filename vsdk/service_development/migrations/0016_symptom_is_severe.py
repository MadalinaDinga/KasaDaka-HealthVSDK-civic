# Generated by Django 3.0.5 on 2020-06-07 13:05

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('service_development', '0015_auto_20200607_1448'),
    ]

    operations = [
        migrations.AddField(
            model_name='symptom',
            name='is_severe',
            field=models.BooleanField(default=False, help_text='Whether the symptom is considered severe.', verbose_name='Is severe'),
        ),
    ]
