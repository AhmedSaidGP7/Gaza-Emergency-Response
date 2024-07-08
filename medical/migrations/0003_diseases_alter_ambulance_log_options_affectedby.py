# Generated by Django 5.0.4 on 2024-07-07 18:50

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('GazaResponse', '0027_uploadeddocument_title'),
        ('medical', '0002_ambulance_log_hospital'),
    ]

    operations = [
        migrations.CreateModel(
            name='diseases',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('diseases_name', models.CharField(max_length=64)),
            ],
        ),
        migrations.AlterModelOptions(
            name='ambulance_log',
            options={'ordering': ['-date']},
        ),
        migrations.CreateModel(
            name='AffectedBy',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('person', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='affected_by', to='GazaResponse.person')),
                ('diseases_name', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='affected_persons', to='medical.diseases')),
            ],
        ),
    ]