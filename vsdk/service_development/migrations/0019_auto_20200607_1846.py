# Generated by Django 3.0.5 on 2020-06-07 16:46

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('service_development', '0018_auto_20200607_1827'),
    ]

    operations = [
        migrations.AddField(
            model_name='resultconfig',
            name='yes_contact_voice_label',
            field=models.ForeignKey(blank=True, help_text='A Voice Label for exposure or contact warning', null=True, on_delete=django.db.models.deletion.PROTECT, related_name='yes_contact_voice_label', to='service_development.VoiceLabel', verbose_name='Exposure warning voice label'),
        ),
        migrations.AlterField(
            model_name='resultconfig',
            name='no_testing_voice_label',
            field=models.ForeignKey(help_text='A Voice Label for no testing necessary', on_delete=django.db.models.deletion.PROTECT, related_name='no_testing_voice_label', to='service_development.VoiceLabel', verbose_name='Testing not necessary voice label'),
        ),
        migrations.AlterField(
            model_name='resultconfig',
            name='yes_risks_voice_label',
            field=models.ForeignKey(help_text='A Voice Label for risks warning', on_delete=django.db.models.deletion.PROTECT, related_name='yes_risks_voice_label', to='service_development.VoiceLabel', verbose_name='Risks warning voice label'),
        ),
    ]