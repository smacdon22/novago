# Generated by Django 4.1.5 on 2023-03-28 19:49

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('novago', '0016_rating_description_alter_rating_rating_driver'),
    ]

    operations = [
        migrations.AddField(
            model_name='trip',
            name='price',
            field=models.IntegerField(default=10),
        ),
    ]
