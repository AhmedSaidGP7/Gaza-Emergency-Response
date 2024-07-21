# Generated by Django 5.0.4 on 2024-07-21 12:16

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('medical', '0003_diseases_alter_ambulance_log_options_affectedby'),
    ]

    operations = [
        migrations.AddField(
            model_name='ambulance_log',
            name='fees',
            field=models.CharField(blank=True, max_length=64, null=True),
        ),
        migrations.AddField(
            model_name='ambulance_log',
            name='scannedDocs',
            field=models.FileField(blank=True, upload_to='medical-reports'),
        ),
    ]
