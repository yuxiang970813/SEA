# Generated by Django 4.1.3 on 2022-11-28 08:47

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('coursework', '0007_rename_status_assigmentstatus_upload_status_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='assigmentstatus',
            name='memo',
            field=models.TextField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='assigmentstatus',
            name='upload_file',
            field=models.FileField(null=True, upload_to=''),
        ),
    ]