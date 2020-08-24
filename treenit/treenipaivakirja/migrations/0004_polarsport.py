# Generated by Django 2.2.10 on 2020-08-21 18:05

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('treenipaivakirja', '0003_polaruser'),
    ]

    operations = [
        migrations.CreateModel(
            name='PolarSport',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('polar_sport', models.CharField(max_length=100, verbose_name='Polar laji')),
                ('laji', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='treenipaivakirja.Laji', verbose_name='Laji')),
                ('polar_user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='treenipaivakirja.PolarUser')),
            ],
            options={
                'unique_together': {('polar_sport', 'polar_user')},
            },
        ),
    ]
