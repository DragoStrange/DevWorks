# Generated by Django 4.2.6 on 2023-12-16 08:53

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Social', '0004_categories_cdesc'),
    ]

    operations = [
        migrations.AddField(
            model_name='student',
            name='simg',
            field=models.ImageField(null=True, upload_to='student'),
        ),
    ]
