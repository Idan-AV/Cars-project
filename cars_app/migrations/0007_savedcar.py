# Generated by Django 4.2.2 on 2023-08-16 18:04

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('cars_app', '0006_picture'),
    ]

    operations = [
        migrations.CreateModel(
            name='SavedCar',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('car', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='cars_app.car')),
                ('user', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='saved_cars', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'db_table': 'saved cars',
            },
        ),
    ]
