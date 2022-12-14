# Generated by Django 4.1.3 on 2022-11-26 17:09

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('coursework', '0002_studentlist_user_is_email_verified_user_status'),
    ]

    operations = [
        migrations.CreateModel(
            name='Course',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=60)),
            ],
        ),
        migrations.CreateModel(
            name='Coursework',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('course', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='coursework_name', to='coursework.course')),
                ('taken_person', models.ManyToManyField(blank=True, related_name='taken_coursework', to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]
