# Generated by Django 4.1.5 on 2023-03-19 23:05

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('novago', '0007_alter_tempsearch_search_date_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='tempsearch',
            name='search_date',
            field=models.DateField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='tempsearch',
            name='search_term',
            field=models.CharField(blank=True, max_length=255, null=True),
        ),
    ]
