# Generated by Django 4.2.1 on 2023-05-24 07:38

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('trust_eval_prod', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='collectorlog',
            name='size',
            field=models.FloatField(default=100),
            preserve_default=False,
        ),
    ]