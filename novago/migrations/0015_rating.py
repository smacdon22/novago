# Generated by Django 4.1.5 on 2023-03-24 19:07

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('novago', '0014_delete_tempsearch'),
    ]

    operations = [
        migrations.CreateModel(
            name='Rating',
            fields=[
                ('id', models.BigAutoField(auto_created=True,
                 primary_key=True, serialize=False, verbose_name='ID')),
                ('rating', models.DecimalField(
                    decimal_places=2, default=2.5, max_digits=3)),
                ('booking', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE,
                 related_name='booking', to='novago.booking')),
            ],
        ),
    ]
