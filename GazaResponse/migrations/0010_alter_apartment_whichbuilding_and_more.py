# Generated by Django 5.0.4 on 2024-05-24 13:42

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('GazaResponse', '0009_alter_person_accommodation'),
    ]

    operations = [
        migrations.AlterField(
            model_name='apartment',
            name='whichBuilding',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='apartments', to='GazaResponse.building'),
        ),
        migrations.AlterField(
            model_name='building',
            name='bshelter',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='Buildings', to='GazaResponse.shelter'),
        ),
    ]
