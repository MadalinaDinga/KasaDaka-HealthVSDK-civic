# Generated by Django 3.0.5 on 2020-06-08 11:30

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('service_development', '0020_auto_20200607_2152'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='resultitem',
            options={'verbose_name_plural': 'Self-check results'},
        ),
        migrations.AlterModelOptions(
            name='risk',
            options={'verbose_name_plural': 'Risks'},
        ),
        migrations.AlterModelOptions(
            name='symptom',
            options={'verbose_name_plural': 'Symptoms'},
        ),
    ]