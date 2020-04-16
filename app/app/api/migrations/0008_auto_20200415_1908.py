# Generated by Django 3.0.5 on 2020-04-15 19:08

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0007_auto_20200410_1708'),
    ]

    operations = [
        migrations.AlterField(
            model_name='profiledata',
            name='gender',
            field=models.TextField(choices=[('Male', 'Male'), ('Female', 'Female'), ('Unknown', 'Unknown')], default='Unknown'),
        ),
        migrations.AlterField(
            model_name='reason',
            name='profile_data_type',
            field=models.TextField(choices=[('Age', 'Age'), ('Gender', 'Gender'), ('Location', 'Location'), ('Personality', 'Personality'), ('Depression', 'Depression')]),
        ),
    ]
