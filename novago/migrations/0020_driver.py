# Generated by Django 4.1.5 on 2023-03-28 23:44

from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('novago', '0019_alter_trip_price'),
    ]

    operations = [
        migrations.CreateModel(
            name='Driver',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('master_number', models.CharField(default='', max_length=250)),
                ('license_expiration_date', models.DateField(default=django.utils.timezone.now)),
                ('license_plate', models.CharField(default='AAA 123', max_length=25)),
                ('vehicle_information_number', models.CharField(default='', max_length=250)),
                ('vehicle_picture', models.ImageField(default='driver1.jpg', upload_to='profile_pictures/')),
                ('account', models.ForeignKey(default=1, on_delete=django.db.models.deletion.CASCADE, related_name='account_of_driver', to='novago.account')),
            ],
        ),
    ]
