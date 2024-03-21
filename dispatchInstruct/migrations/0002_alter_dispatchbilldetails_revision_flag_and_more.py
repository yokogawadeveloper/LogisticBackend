# Generated by Django 4.2.10 on 2024-03-21 03:51

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('dispatchInstruct', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='dispatchbilldetails',
            name='revision_flag',
            field=models.BooleanField(default=False),
        ),
        migrations.AlterField(
            model_name='dispatchinstruction',
            name='current_level',
            field=models.CharField(default=0, max_length=100),
        ),
        migrations.AlterField(
            model_name='dispatchinstruction',
            name='dil_level',
            field=models.CharField(default=0, max_length=100),
        ),
        migrations.AlterField(
            model_name='dispatchinstruction',
            name='dil_status_no',
            field=models.CharField(default=0, max_length=100),
        ),
        migrations.AlterField(
            model_name='dispatchinstruction',
            name='dispatched_flag',
            field=models.BooleanField(default=False),
        ),
        migrations.AlterField(
            model_name='dispatchinstruction',
            name='loaded_flag',
            field=models.BooleanField(default=False),
        ),
        migrations.AlterField(
            model_name='dispatchinstruction',
            name='packed_flag',
            field=models.BooleanField(default=False),
        ),
        migrations.AlterField(
            model_name='dispatchinstruction',
            name='revision_flag',
            field=models.BooleanField(default=False),
        ),
        migrations.AlterField(
            model_name='masteritemlist',
            name='revision_flag',
            field=models.BooleanField(default=False),
        ),
        migrations.AlterField(
            model_name='masteritemlist',
            name='serial_flag',
            field=models.BooleanField(default=False),
        ),
    ]