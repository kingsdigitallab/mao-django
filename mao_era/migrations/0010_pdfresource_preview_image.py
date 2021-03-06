# Generated by Django 2.1 on 2019-05-28 00:53

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('wagtailimages', '0001_squashed_0021'),
        ('mao_era', '0009_auto_20190516_0414'),
    ]

    operations = [
        migrations.AddField(
            model_name='pdfresource',
            name='preview_image',
            field=models.ForeignKey(default=22, on_delete=django.db.models.deletion.PROTECT, related_name='pdfs', to='wagtailimages.Image'),
            preserve_default=False,
        ),
    ]
