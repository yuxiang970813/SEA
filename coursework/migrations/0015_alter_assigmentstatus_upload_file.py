# Generated by Django 4.1.3 on 2022-12-01 04:48

import coursework.models
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('coursework', '0014_alter_assignment_options_alter_assignment_created_on'),
    ]

    operations = [
        migrations.AlterField(
            model_name='assigmentstatus',
            name='upload_file',
            field=models.FileField(null=True, upload_to=coursework.models.path_and_rename),
        ),
    ]
