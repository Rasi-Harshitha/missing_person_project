# Generated by Django 4.2.18 on 2025-01-29 16:35

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='RegisteredPerson',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100)),
                ('age', models.IntegerField()),
                ('date_missing', models.DateField()),
                ('phone', models.CharField(max_length=15)),
                ('email', models.EmailField(max_length=254)),
                ('photo', models.ImageField(upload_to='registered_photos/')),
                ('address', models.TextField()),
            ],
        ),
        migrations.CreateModel(
            name='ReportedCase',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100)),
                ('location', models.CharField(max_length=255)),
                ('details', models.TextField()),
                ('photo', models.ImageField(upload_to='reported_photos/')),
                ('reported_date', models.DateTimeField(auto_now_add=True)),
            ],
        ),
        migrations.CreateModel(
            name='MatchedCase',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('match_date', models.DateTimeField(auto_now_add=True)),
                ('registered_person', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='admin_interface.registeredperson')),
                ('reported_case', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='admin_interface.reportedcase')),
            ],
        ),
    ]
