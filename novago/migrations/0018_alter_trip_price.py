# Generated by Django 4.1.5 on 2023-03-28 19:58

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('novago', '0017_trip_price'),
    ]

    operations = [
        migrations.AlterField(
            model_name='trip',
            name='price',
            field=models.IntegerField(db_column='price', default=10),
        ),
    ]