# Generated by Django 4.2.18 on 2025-01-30 14:24

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('admin_interface', '0003_reportedcase_description'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='reportedcase',
            name='details',
        ),
        migrations.RemoveField(
            model_name='reportedcase',
            name='name',
        ),
        migrations.AddField(
            model_name='matchedcase',
            name='match_percentage',
            field=models.FloatField(default=0),
            preserve_default=False,
        ),
    ]
