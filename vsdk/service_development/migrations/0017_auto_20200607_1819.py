# Generated by Django 3.0.5 on 2020-06-07 16:19

import django.core.validators
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('service_development', '0016_symptom_is_severe'),
    ]

    operations = [
        migrations.CreateModel(
            name='ResultConfig',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('infected_probability_benchmark', models.FloatField(blank=True, help_text='Point of reference against which the infection probability is compared and conclusions may be drawn whether the person is infected or not.', null=True, validators=[django.core.validators.MinValueValidator(0), django.core.validators.MaxValueValidator(100)])),
                ('symptom_no_benchmark', models.PositiveIntegerField(blank=True, help_text='Point of reference against which the number of reported symptoms per session is computed and conclusions may be drawn whether the person is infected or not.', null=True)),
                ('no_testing_voice_label', models.ForeignKey(help_text='A Voice Label for no testing needed', on_delete=django.db.models.deletion.PROTECT, related_name='no_testing_voice_label', to='service_development.VoiceLabel', verbose_name='No testing needed voice label')),
                ('result_negative_voice_label', models.ForeignKey(help_text='A Voice Label for negative diagnosis result', on_delete=django.db.models.deletion.PROTECT, related_name='result_negative_voice_label', to='service_development.VoiceLabel', verbose_name='User is not suspect voice label')),
                ('result_positive_voice_label', models.ForeignKey(help_text='A Voice Label for positive diagnosis result', on_delete=django.db.models.deletion.PROTECT, related_name='result_positive_voice_label', to='service_development.VoiceLabel', verbose_name='User is suspect voice label')),
                ('yes_risks_voice_label', models.ForeignKey(help_text='A Voice Label for notice of risks', on_delete=django.db.models.deletion.PROTECT, related_name='yes_risks_voice_label', to='service_development.VoiceLabel', verbose_name='Notice of risks voice label')),
                ('yes_testing_voice_label', models.ForeignKey(help_text='A Voice Label for testing needed', on_delete=django.db.models.deletion.PROTECT, related_name='yes_testing_voice_label', to='service_development.VoiceLabel', verbose_name='Testing recommended voice label')),
            ],
            options={
                'verbose_name_plural': 'Diagnosis Configurable Parameters',
            },
        ),
        migrations.DeleteModel(
            name='DiagnosisConfigParameters',
        ),
    ]
