# Generated by Django 3.0.3 on 2020-05-09 10:59

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('basic', '0004_auto_20200509_1000'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='festival',
            name='date',
        ),
        migrations.RemoveField(
            model_name='festival',
            name='occasion',
        ),
        migrations.AddField(
            model_name='festival',
            name='datafile',
            field=models.FileField(null=True, upload_to='basic/data'),
        ),
    ]
