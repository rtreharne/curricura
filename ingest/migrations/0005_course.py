# Generated by Django 5.2.4 on 2025-07-16 12:35

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('ingest', '0004_canvasassignment_canvasfile_canvaspage'),
    ]

    operations = [
        migrations.CreateModel(
            name='Course',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('code', models.CharField(max_length=20, unique=True)),
                ('title', models.CharField(max_length=255)),
                ('year', models.IntegerField(choices=[(1, 'Year 1'), (2, 'Year 2'), (3, 'Year 3'), (4, 'Year 4'), (5, 'Year 5')])),
                ('created_at', models.DateTimeField(auto_now_add=True)),
            ],
        ),
    ]
