# Generated by Django 5.0.6 on 2024-12-21 02:44

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Affiliation',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=50)),
            ],
        ),
        migrations.CreateModel(
            name='Workplace',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=50)),
                ('body', models.TextField(max_length=150)),
                ('media', models.FileField(upload_to='')),
                ('coordinates', models.JSONField(default=list)),
                ('affiliation', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='pages.affiliation')),
            ],
        ),
    ]
