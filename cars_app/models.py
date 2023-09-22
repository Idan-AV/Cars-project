from django.db import models
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.db import models


# Create your models here.

class Company(models.Model):
    company_name = models.CharField(max_length=256, null=False)
    founder = models.CharField(max_length=256, null=False)
    country = models.CharField(max_length=256, null=False)
    year_of_establishment = models.IntegerField(null=False)

    class Meta:
        db_table = 'companies'


class Car(models.Model):
    year_of_manufacture = models.IntegerField(null=False)
    company_id = models.ForeignKey(
        'Company',
        on_delete=models.CASCADE,
    )
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
    )
    model_name = models.CharField(max_length=256, null=False)
    number_of_past_owners = models.IntegerField(null=False)
    description = models.TextField(null=False)
    color = models.CharField(max_length=256, null=False)
    engine_capacity = models.FloatField(null=False)
    number_of_seats = models.IntegerField(null=False)
    car_condition = models.CharField(max_length=256, null=False, choices=[('new', 'new'), ('used', 'used')])
    mileage = models.FloatField(null=False)
    transmission = models.CharField(max_length=256, null=False)
    price = models.FloatField(null=False)
    pic_url = models.URLField(max_length=512, db_column='pic_url', null=True, blank=True)

    class Meta:
        db_table = 'cars'

    @property
    def user_name(self):
        return f"{self.user.first_name} {self.user.last_name}"

    @property
    def company_name(self):
        return self.company_id.company_name

    @property
    def address1(self):
        return f"{self.user.profile.address}"


class Owner(models.Model):
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name='profile'
    )
    address = models.CharField(max_length=500, null=False)
    phone_number = models.CharField(max_length=256, null=False)
    img_url = models.URLField(max_length=512, null=True)

    class Meta:
        db_table = 'owners'

    # @property
    # def address1(self):
    #     return f"{self.address}"


class Picture(models.Model):
    car = models.ForeignKey(
        'Car',
        on_delete=models.CASCADE,
    )
    original = models.URLField(max_length=512, null=True)
    thumbnail = models.URLField(max_length=512, null=True)


class SavedCar(models.Model):
    car = models.ForeignKey(
        'Car',
        on_delete=models.CASCADE,
    )
    # user = models.OneToOneField(
    #     User,
    #     on_delete=models.CASCADE,
    #     related_name='saved_cars'
    # )
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='saved_cars'
    )

    class Meta:
        db_table = 'saved cars'
        # @property
    # def saved_car(self):
    #     return f"{self.user.saved_cars.car}"
