import datetime

from django.contrib.auth.models import User
from django.contrib.auth.password_validation import validate_password
from django.core.validators import MinValueValidator
from django.db import transaction
from rest_framework import serializers
from rest_framework.exceptions import ValidationError
from rest_framework.generics import get_object_or_404
from rest_framework.serializers import ModelSerializer
from rest_framework.validators import UniqueTogetherValidator

from cars_app.models import *


# class SignupSerializer(ModelSerializer):
#     password = serializers.CharField(
#         max_length=128, validators=[validate_password], write_only=True)
#     address = serializers.CharField(
#         required=True, max_length=256, write_only=True)
#     phone_number = serializers.CharField(
#         required=True, max_length=256, write_only=True)
#
#     class Meta:
#         model = User
#         fields = ['id', 'username', 'email', 'password', 'first_name', 'last_name', 'address',
#                   'phone_number']
#         extra_kwargs = {
#             'email': {'required': True},
#             'username': {'read_only': True},
#         }
#         validators = [UniqueTogetherValidator(User.objects.all(), ['email'])]
#
#     def create(self, validated_data):
#         with transaction.atomic():
#             user = User.objects.create_user(
#                 username=validated_data['email'],
#                 email=validated_data['email'],
#                 password=validated_data['password'],
#                 first_name=validated_data.get('first_name', ''),
#                 last_name=validated_data.get('last_name', ''))
#             Owner.objects.create(user=user, address=validated_data['address'],
#                                  phone_number=validated_data['phone_number'])
#         return user
#
#
# class UserProfileSerializer(SignupSerializer):
#
#     def to_representation(self, instance):
#         user_repr = super().to_representation(instance)
#         user_repr['address'] = instance.profile.address
#         user_repr['phone_number'] = instance.profile.phone_number
#         return user_repr
#
#     class Meta:
#         model = User
#         fields = ['id', 'username', 'email', 'first_name', 'last_name']
#
#
# class UserSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = User
#         exclude = ['password', 'groups', 'last_login', 'user_permissions']

class UserProfileSerializer(ModelSerializer):

    def to_representation(self, instance):
        user_repr = super().to_representation(instance)
        user_repr['address'] = instance.profile.address
        user_repr['img_url'] = instance.profile.img_url
        user_repr['phone_number'] = instance.profile.phone_number
        return user_repr

    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'first_name', 'last_name']


class UserSerializer(ModelSerializer):
    password = serializers.CharField(
        max_length=128, validators=[validate_password], write_only=True)
    address = serializers.CharField(
        required=True, max_length=256, write_only=True
    )
    phone_number = serializers.CharField(
        required=True, max_length=256, write_only=True
    )
    img_url = serializers.URLField(
        required=False, max_length=256, write_only=True
    )

    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'password', 'first_name', 'last_name', 'address', 'phone_number', 'img_url'
            , 'profile']
        extra_kwargs = {
            'email': {'required': True},
            'username': {'read_only': True},
        }
        validators = [UniqueTogetherValidator(User.objects.all(), ['email'])]
        depth = 1

    def create(self, validated_data):
        with transaction.atomic():
            user = User.objects.create_user(
                username=validated_data['email'],
                email=validated_data['email'],
                password=validated_data['password'],
                first_name=validated_data.get('first_name', ''),
                last_name=validated_data.get('last_name', ''))
            Owner.objects.create(user=user, address=validated_data['address'],
                                 phone_number=validated_data['phone_number'])
        return user


class ProfileUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Owner
        fields = ['phone_number']


class UserUpdateSerializer(serializers.ModelSerializer):
    profile = ProfileUpdateSerializer(many=False)

    class Meta:
        model = User
        fields = ['email', 'profile']

    def update(self, instance, validated_data):
        print(validated_data)
        profile = None
        if 'profile' in validated_data:
            profile = validated_data.pop('profile')
            instance.profile.phone_number = profile['phone_number']
            instance.profile.save()
            print(profile)
        instance.email = validated_data['email']
        instance.save()
        return instance


class DetailedUserSerializer(ModelSerializer):
    user = UserSerializer()

    class Meta:
        fields = '__all__'
        model = Owner


class GetCompany(serializers.ModelSerializer):
    class Meta:
        model = Company
        fields = '__all__'


class GetCompanies(serializers.ModelSerializer):
    class Meta:
        model = Company
        fields = '__all__'


class AddCompany(serializers.ModelSerializer):
    class Meta:
        model = Company
        fields = '__all__'
        extra_kwargs = {
            'id': {'read_only': True}
        }


class GetCar(serializers.ModelSerializer):
    class Meta:
        model = Car
        fields = ['year_of_manufacture', 'model_name', 'number_of_past_owners', 'description', 'color',
                  'engine_capacity', 'number_of_seats', 'car_condition'
            , 'mileage', 'transmission', 'price', 'user_name', 'company_name', 'pic_url', 'address1', 'id', 'user']
        # just the company name and the username


class AddCar(serializers.ModelSerializer):
    class Meta:
        model = Car
        fields = '__all__'

    def validate(self, attrs):
        company = attrs['company_id']
        print(company.year_of_establishment)
        today = datetime.date.today()
        # aks
        if attrs['year_of_manufacture'] < company.year_of_establishment or attrs['year_of_manufacture'] > today.year:
            raise ValidationError("invalid year")
        return attrs


class AllCars(serializers.ModelSerializer):
    class Meta:
        model = Car
        fields = ['id', 'price', 'model_name', 'mileage', 'car_condition', 'year_of_manufacture', 'pic_url',
                  'company_name', 'description', 'user']

    # ask valeria
    # def validate(self, data):
    #     # Handle validation and defaults for missing or null parameters
    #     if data.get('from_price') is None:
    #         data['from_price'] = 0  # Set a default value if minPrice is not provided
    #     if data.get('to_price') is None:
    #         data['to_price'] = 1_000_000  # Set a default value if maxPrice is not provided
    #     if data.get('from_year_of_manufacture') is None:
    #         data['from_year_of_manufacture'] = 1995
    #     if data.get('to_year_of_manufacture') is None:
    #         data['to_year_of_manufacture'] = 2070
    #     return data


class GetAllCarsByCompany(serializers.ModelSerializer):
    class Meta:
        model = Car
        exclude = ['id', 'company_id']


class AllPicturesByCar(serializers.ModelSerializer):
    class Meta:
        model = Picture
        fields = ['original', 'thumbnail']


class PostAPictureByCar(serializers.ModelSerializer):
    class Meta:
        model = Picture
        fields = '__all__'

    # def create(self, validated_data):
    #     original_image_url = validated_data.get('original_image_url')
    #     validated_data['thumbnail'] = original_image_url
    #     instance = Picture.objects.create(
    #         original=original_image_url,
    #         thumbnail=original_image_url
    #     )
    #     return instance


class GetSavedCars(serializers.ModelSerializer):
    class Meta:
        model = SavedCar
        # fields = ['car']
        fields = []
        depth = 1
        # fields = ['car', 'user']

    def to_representation(self, instance):
        car_instance = instance.car
        car_serializer = AllCars(car_instance)
        return car_serializer.data


class AddSavedCarSerializer(serializers.ModelSerializer):
    class Meta:
        model = SavedCar
        fields = ['car', 'user']
