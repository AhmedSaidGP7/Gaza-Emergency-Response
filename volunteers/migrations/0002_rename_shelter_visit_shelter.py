# Generated by Django 5.0.4 on 2024-05-27 02:25

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('volunteers', '0001_initial'),
    ]

    operations = [
        migrations.RenameField(
            model_name='visit',
            old_name='shelter',
            new_name='Shelter',
        ),
    ]
