# Generated by Django 4.2.1 on 2023-05-26 10:32

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('trust_eval_prod', '0008_alter_webservicemetrics_request_id'),
    ]

    operations = [
        migrations.AddField(
            model_name='webservicemetrics',
            name='successability',
            field=models.FloatField(default=0),
            preserve_default=False,
        ),
    ]