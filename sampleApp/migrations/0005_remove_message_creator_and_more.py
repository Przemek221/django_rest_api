# Generated by Django 4.1 on 2023-12-19 22:24

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('sampleApp', '0004_comment_createddate_message_createddate_and_more'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='message',
            name='creator',
        ),
        migrations.RemoveField(
            model_name='messageattachment',
            name='creator',
        ),
        migrations.RemoveField(
            model_name='post',
            name='creator',
        ),
        migrations.RemoveField(
            model_name='postattachment',
            name='creator',
        ),
        migrations.DeleteModel(
            name='Comment',
        ),
        migrations.DeleteModel(
            name='Message',
        ),
        migrations.DeleteModel(
            name='MessageAttachment',
        ),
        migrations.DeleteModel(
            name='Post',
        ),
        migrations.DeleteModel(
            name='PostAttachment',
        ),
    ]
