# Generated by Django 2.2.13 on 2021-07-28 15:43

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('treenipaivakirja', '0006_ourauser'),
    ]

    operations = [
        migrations.CreateModel(
            name='OuraSleep',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('date', models.DateField()),
                ('bedtime_start', models.DateTimeField()),
                ('bedtime_end', models.DateTimeField()),
                ('duration', models.DecimalField(decimal_places=2, max_digits=4)),
                ('total', models.DecimalField(decimal_places=2, max_digits=4)),
                ('awake', models.DecimalField(decimal_places=2, max_digits=4)),
                ('rem', models.DecimalField(decimal_places=2, max_digits=4)),
                ('deep', models.DecimalField(decimal_places=2, max_digits=4)),
                ('light', models.DecimalField(decimal_places=2, max_digits=4)),
                ('hr_min', models.IntegerField()),
                ('hr_avg', models.DecimalField(decimal_places=2, max_digits=4)),
                ('hrv_avg', models.IntegerField()),
                ('score', models.IntegerField()),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'unique_together': {('user', 'date')},
            },
        ),
    ]
