# Generated by Django 4.2.5 on 2023-09-11 07:43

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Librapp', '0003_remove_kniha_majitel'),
    ]

    operations = [
        migrations.AddField(
            model_name='kniha',
            name='majitel',
            field=models.CharField(blank=True, max_length=180),
        ),
    ]
