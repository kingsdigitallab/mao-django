# Generated by Django 2.1 on 2019-06-19 06:26

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('mao_era', '0013_objectbiographiespage_sourcespage'),
    ]

    operations = [
        migrations.AlterField(
            model_name='place',
            name='title',
            field=models.CharField(max_length=150),
        ),
    ]