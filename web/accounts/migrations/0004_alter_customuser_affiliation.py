# Generated by Django 5.0.6 on 2024-12-07 20:08

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0003_alter_customuser_affiliation'),
    ]

    operations = [
        migrations.AlterField(
            model_name='customuser',
            name='affiliation',
            field=models.CharField(max_length=50, null=True),
        ),
    ]
