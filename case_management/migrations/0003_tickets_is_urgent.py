# Generated by Django 5.0.4 on 2024-05-31 21:49

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('case_management', '0002_comments'),
    ]

    operations = [
        migrations.AddField(
            model_name='tickets',
            name='is_urgent',
            field=models.BooleanField(default=False),
        ),
    ]
