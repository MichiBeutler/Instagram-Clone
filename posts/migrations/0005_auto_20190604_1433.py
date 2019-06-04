# Generated by Django 2.2.1 on 2019-06-04 12:33

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('posts', '0004_auto_20190604_1411'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='post',
            name='location',
        ),
        migrations.AddField(
            model_name='post',
            name='location',
            field=models.ForeignKey(default=1, on_delete=django.db.models.deletion.CASCADE, to='posts.Location'),
            preserve_default=False,
        ),
    ]
