# Generated by Django 4.2.7 on 2025-03-28 05:01

import blog.models
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('blog', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='post',
            name='featured_image',
            field=models.ImageField(max_length=500, upload_to=blog.models.post_image_path, verbose_name='featured image'),
        ),
    ]
