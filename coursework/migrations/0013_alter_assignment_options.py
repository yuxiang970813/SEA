# Generated by Django 4.1.3 on 2022-11-29 07:29

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('coursework', '0012_alter_assignment_created_on'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='assignment',
            options={'ordering': ['created_on']},
        ),
    ]
