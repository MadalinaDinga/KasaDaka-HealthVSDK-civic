# Generated by Django 3.0.5 on 2020-06-01 13:26

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('service_development', '0003_risk_symptom'),
    ]

    operations = [
        migrations.CreateModel(
            name='SelfCheckItem',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('has_symptom', models.BooleanField(null=True)),
                ('choice_element', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='choice_element', to='service_development.Choice', verbose_name='ChoiceElement')),
                ('risk', models.ForeignKey(null=True, on_delete=django.db.models.deletion.PROTECT, related_name='risk', to='service_development.Risk', verbose_name='Risk')),
                ('session', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='check_item_session', to='service_development.CallSession')),
                ('symptom', models.ForeignKey(null=True, on_delete=django.db.models.deletion.PROTECT, related_name='symptom', to='service_development.Symptom', verbose_name='Symptom')),
            ],
            options={
                'verbose_name': 'SelfCheckItem',
            },
        ),
    ]