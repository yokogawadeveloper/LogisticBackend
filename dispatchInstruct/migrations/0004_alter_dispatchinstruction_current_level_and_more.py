# Generated by Django 4.2.10 on 2024-03-27 06:25

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('dispatchInstruct', '0003_dispatchinstruction_wf_type'),
    ]

    operations = [
        migrations.AlterField(
            model_name='dispatchinstruction',
            name='current_level',
            field=models.IntegerField(blank=True, default=0, null=True),
        ),
        migrations.AlterField(
            model_name='dispatchinstruction',
            name='dil_level',
            field=models.IntegerField(blank=True, default=0, null=True),
        ),
    ]
