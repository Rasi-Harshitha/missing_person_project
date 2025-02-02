# Generated by Django 4.2.18 on 2025-01-30 09:14

from django.db import migrations, models
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('user', '0001_initial'),
    ]

    operations = [
        migrations.RenameField(
            model_name='reportedcase',
            old_name='last_seen_location',
            new_name='location',
        ),
        migrations.RenameField(
            model_name='reportedcase',
            old_name='image',
            new_name='photo',
        ),
        migrations.RenameField(
            model_name='reportedcase',
            old_name='timestamp',
            new_name='reported_date',
        ),
        migrations.AddField(
            model_name='reportedcase',
            name='description',
            field=models.CharField(default='No description', max_length=255),
        ),
        migrations.AddField(
            model_name='reportedcase',
            name='details',
            field=models.TextField(default=django.utils.timezone.now),
            preserve_default=False,
        ),
    ]
