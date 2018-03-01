# Generated by Django 2.0 on 2018-03-01 19:43

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('User', '0012_auto_20180301_0040'),
        ('Sentence', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='sentence',
            name='owner',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='User.User'),
        ),
        migrations.AlterField(
            model_name='sentence',
            name='sentence',
            field=models.CharField(max_length=255, unique=True),
        ),
        migrations.AlterField(
            model_name='sentence',
            name='tags',
            field=models.ManyToManyField(default=None, to='Sentence.Tag'),
        ),
        migrations.AlterField(
            model_name='tag',
            name='tag',
            field=models.CharField(max_length=10, unique=True),
        ),
    ]
