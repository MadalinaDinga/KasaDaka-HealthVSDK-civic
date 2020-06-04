# Generated by Django 3.0.5 on 2020-06-04 19:01

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('service_development', '0012_auto_20200604_2022'),
    ]

    operations = [
        migrations.RenameModel(
            old_name='ResultUtils',
            new_name='Outcome',
        ),
        migrations.AlterModelOptions(
            name='outcome',
            options={'verbose_name_plural': 'Outcome Configuration'},
        ),
        migrations.AlterModelOptions(
            name='resultitem',
            options={'verbose_name': 'Result Item'},
        ),
        migrations.AlterModelOptions(
            name='selfcheckitem',
            options={'verbose_name_plural': 'Self-Reported Items (Symptoms and Risks)'},
        ),
        migrations.RenameField(
            model_name='messagepresentation',
            old_name='is_result_message',
            new_name='redirects_to_result',
        ),
        migrations.RemoveField(
            model_name='messagepresentation',
            name='result',
        ),
    ]