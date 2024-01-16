# Generated by Django 4.2.6 on 2023-12-15 06:08

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('Social', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Categories',
            fields=[
                ('categoryname', models.CharField(max_length=50, primary_key=True, serialize=False)),
            ],
        ),
        migrations.CreateModel(
            name='Shoes',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('shoeimg', models.ImageField(upload_to='shoe')),
                ('categoryname', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='Social.categories')),
            ],
        ),
    ]
