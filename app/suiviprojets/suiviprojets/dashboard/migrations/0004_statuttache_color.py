# Generated by Django 3.0 on 2021-12-28 10:17

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('dashboard', '0003_auto_20211215_1023'),
    ]

    operations = [
        migrations.AddField(
            model_name='statuttache',
            name='color',
            field=models.CharField(blank=True, max_length=7, null=True),
        ),
    ]