# Generated by Django 5.1.1 on 2024-12-11 13:57

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("hottrack", "0003_populate_song_slugs"),
    ]

    operations = [
        migrations.AlterField(
            model_name="song",
            name="slug",
            field=models.SlugField(allow_unicode=True, blank=True, max_length=100),
        ),
    ]
