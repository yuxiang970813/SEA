# Generated by Django 4.1.3 on 2022-11-28 16:16

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('coursework', '0009_alter_coursework_options'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='course',
            options={'ordering': ['name']},
        ),
        migrations.AlterField(
            model_name='assignment',
            name='created_on',
            field=models.DateField(auto_now_add=True),
        ),
    ]