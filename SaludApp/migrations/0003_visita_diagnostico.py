# Generated by Django 5.1.6 on 2025-05-28 15:31

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('SaludApp', '0002_remove_diagnostico_diagnostico_tratamiento_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='visita',
            name='diagnostico',
            field=models.OneToOneField(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='visita_diagnostico', to='SaludApp.diagnostico', verbose_name='Diagnóstico asociado'),
        ),
    ]
