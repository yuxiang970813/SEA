# Generated by Django 4.1.3 on 2022-12-03 12:28

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('coursework', '0022_assignment_is_submit'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='assignment',
            name='is_submit',
        ),
    ]
