# Generated by Django 5.0.4 on 2024-07-10 08:59

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('GazaResponse', '0027_uploadeddocument_title'),
    ]

    operations = [
        migrations.AlterField(
            model_name='person',
            name='idNumber',
            field=models.CharField(blank=True, max_length=64),
        ),
        migrations.AlterField(
            model_name='person',
            name='status',
            field=models.CharField(blank=True, max_length=64),
        ),
    ]