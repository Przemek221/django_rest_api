# Generated by Django 4.1 on 2024-01-02 10:38

from django.db import migrations, models
import django.db.models.deletion
import sampleApp.models


class Migration(migrations.Migration):

    dependencies = [
        ('sampleApp', '0012_comment'),
    ]

    operations = [
        migrations.CreateModel(
            name='PostAttachment',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('attachment', models.FileField(upload_to=sampleApp.models.get_directory_path)),
                ('relatedPost', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='attachments', to='sampleApp.post')),
            ],
        ),
    ]
