# Generated by Django 5.0.4 on 2024-05-27 02:24

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('GazaResponse', '0017_rename_apartment_location_shelter'),
    ]

    operations = [
        migrations.RenameField(
            model_name='location',
            old_name='Shelter',
            new_name='shelter',
        ),
    ]