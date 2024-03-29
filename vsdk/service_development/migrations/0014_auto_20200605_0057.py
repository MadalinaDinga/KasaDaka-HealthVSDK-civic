# Generated by Django 3.0.5 on 2020-06-04 22:57

import django.core.validators
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('service_development', '0013_auto_20200604_2101'),
    ]

    operations = [
        migrations.RenameModel(
            old_name='Outcome',
            new_name='DiagnosisConfigParameters',
        ),
        migrations.AlterModelOptions(
            name='diagnosisconfigparameters',
            options={'verbose_name_plural': 'Diagnosis configurable parameters'},
        ),
        migrations.RemoveField(
            model_name='resultitem',
            name='is_infected_confirmed',
        ),
        migrations.RemoveField(
            model_name='resultitem',
            name='is_infected_predicted',
        ),
        migrations.AddField(
            model_name='resultitem',
            name='is_infected_prediction',
            field=models.BooleanField(blank=True, help_text='Whether the person is believed to be infected after the self-check.', null=True, verbose_name='Self-check result'),
        ),
        migrations.AddField(
            model_name='resultitem',
            name='testing_confirmation',
            field=models.BooleanField(blank=True, help_text='Whether the person tested positive for COVID-19.', null=True, verbose_name='Testing result'),
        ),
        migrations.AddField(
            model_name='resultitem',
            name='testing_recommended',
            field=models.BooleanField(blank=True, help_text='Whether testing is recommended.', null=True, verbose_name='Is testing recommended'),
        ),
        migrations.AlterField(
            model_name='messagepresentation',
            name='redirects_to_result',
            field=models.BooleanField(default=False, verbose_name='Compute diagnosis and redirect to self-check result element.'),
        ),
        migrations.AlterField(
            model_name='resultitem',
            name='infected_probability',
            field=models.FloatField(blank=True, help_text='The probability that the person has been infected, based on the configured parameters.', null=True, validators=[django.core.validators.MinValueValidator(0), django.core.validators.MaxValueValidator(100)], verbose_name='Infection estimated probability'),
        ),
        migrations.AlterField(
            model_name='resultitem',
            name='is_exposed',
            field=models.BooleanField(blank=True, help_text='Whether the person has been exposed.', null=True, verbose_name='User was exposed'),
        ),
        migrations.AlterField(
            model_name='resultitem',
            name='risk_no',
            field=models.PositiveIntegerField(blank=True, help_text='The number of reported risks.', null=True, verbose_name='Number of confirmed risk factors'),
        ),
        migrations.AlterField(
            model_name='resultitem',
            name='session',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, related_name='session_result', to='service_development.CallSession', verbose_name='Call session'),
        ),
        migrations.AlterField(
            model_name='resultitem',
            name='symptom_no',
            field=models.PositiveIntegerField(blank=True, help_text='The number of reported symptoms.', null=True, verbose_name='Number of confirmed symptoms'),
        ),
    ]
