# Generated by Django 4.1 on 2024-01-03 16:04

from django.db import migrations, models
import sampleApp.models


class Migration(migrations.Migration):

    dependencies = [
        ('sampleApp', '0013_postattachment'),
    ]

    operations = [
        migrations.AlterField(
            model_name='postattachment',
            name='attachment',
            field=models.FileField(blank=True, upload_to=sampleApp.models.get_directory_path),
        ),
    ]
