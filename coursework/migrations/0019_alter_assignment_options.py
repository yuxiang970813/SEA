# Generated by Django 4.1.3 on 2022-12-01 13:05

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('coursework', '0018_alter_uploadfile_file'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='assignment',
            options={'ordering': ['coursework', '-created_on']},
        ),
    ]