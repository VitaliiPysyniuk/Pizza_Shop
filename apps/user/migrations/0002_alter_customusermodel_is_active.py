# Generated by Django 3.2.7 on 2021-09-21 12:35

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('user', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='customusermodel',
            name='is_active',
            field=models.BooleanField(),
        ),
    ]