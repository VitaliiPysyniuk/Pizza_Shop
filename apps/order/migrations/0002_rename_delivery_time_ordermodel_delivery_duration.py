# Generated by Django 3.2.7 on 2021-09-21 12:35

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('order', '0001_initial'),
    ]

    operations = [
        migrations.RenameField(
            model_name='ordermodel',
            old_name='delivery_time',
            new_name='delivery_duration',
        ),
    ]
