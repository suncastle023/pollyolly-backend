# Generated by Django 5.1.6 on 2025-02-28 10:32

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='customuser',
            name='level',
            field=models.IntegerField(default=1),
        ),
    ]
