# Generated by Django 3.0.5 on 2020-06-08 14:37

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('service_development', '0023_auto_20200608_1529'),
    ]

    operations = [
        migrations.AlterField(
            model_name='resultitem',
            name='is_exposed',
            field=models.BooleanField(blank=True, help_text='Whether the person has been exposed to the virus.', null=True, verbose_name='Exposed'),
        ),
    ]
