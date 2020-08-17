# Generated by Django 2.2.10 on 2020-08-14 14:11

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('treenipaivakirja', '0003_polaruser'),
    ]

    operations = [
        migrations.CreateModel(
            name='PolarSport',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('polar_sport', models.CharField(max_length=100, verbose_name='Polar laji')),
                ('laji', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='treenipaivakirja.Laji', verbose_name='Laji')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'unique_together': {('polar_sport', 'user')},
            },
        ),
    ]
