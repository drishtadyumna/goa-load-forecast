# Generated by Django 3.0.3 on 2020-05-09 10:00

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('basic', '0003_auto_20200509_0529'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='megawatts',
            name='datetime',
        ),
        migrations.RemoveField(
            model_name='megawatts',
            name='load',
        ),
        migrations.AddField(
            model_name='megawatts',
            name='datafile',
            field=models.FileField(null=True, upload_to='basic/data'),
        ),
    ]