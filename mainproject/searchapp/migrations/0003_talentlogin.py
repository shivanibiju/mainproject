# Generated by Django 5.1.5 on 2025-03-15 06:19

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('searchapp', '0002_searchhistory'),
    ]

    operations = [
        migrations.CreateModel(
            name='TalentLogin',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('username', models.CharField(max_length=100)),
                ('password', models.CharField(max_length=100)),
                ('talent', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='searchapp.talent')),
            ],
            options={
                'db_table': 'TalentLogin',
            },
        ),
    ]
