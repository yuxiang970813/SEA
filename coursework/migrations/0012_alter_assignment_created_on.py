# Generated by Django 4.1.3 on 2022-11-28 16:19

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('coursework', '0011_alter_assignment_created_on'),
    ]

    operations = [
        migrations.AlterField(
            model_name='assignment',
            name='created_on',
            field=models.DateField(auto_now_add=True),
        ),
    ]