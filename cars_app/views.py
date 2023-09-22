import os
import uuid

from django.http import JsonResponse
from django.shortcuts import render
import json

from django.shortcuts import render
from google.oauth2 import service_account
from google.cloud import storage

from google.oauth2 import id_token
from google.auth.transport import requests

from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.generics import get_object_or_404
from rest_framework.pagination import PageNumberPagination
from rest_framework.permissions import IsAuthenticated, BasePermission
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet

from cars_app.models import *
from cars_app.serializers import *


# Create your views here.
@api_view(['POST'])
def signup(request):
    s = UserSerializer(data=request.data)
    s.is_valid(raise_exception=True)
    s.save()
    return Response(data=s.data)


# class UsersViewSet(ModelViewSet):
#     serializer_class = UserSerializer
#     queryset = User.objects.all()
#
#     def create(self, request, *args, **kwargs):
#         serializer = self.get_serializer(data=request.data)
#         serializer.is_valid(raise_exception=True)
#         user = serializer.save()
#         data = {
#             'id': user.id,
#             'email': user.email,
#             'first_name': user.first_name,
#             'last_name': user.last_name,
#             'address': user.profile.address
#         }
#         return JsonResponse(data)


@api_view(['GET'])
def current_user_details(request):
    if not request.user.is_authenticated:
        return Response(status=status.HTTP_401_UNAUTHORIZED)
    else:
        serializer = UserSerializer(instance=request.user)
        return Response(serializer.data)


@api_view(['GET'])
def get_all_users(request):
    if not request.user.is_authenticated and not request.user.is_staff:
        return Response(status=status.HTTP_401_UNAUTHORIZED)
    else:
        all_users = User.objects.all()
        serializer = UserSerializer(instance=all_users, many=True)
        return Response(serializer.data)


@api_view(['GET', 'PATCH', 'PUT'])
def get_a_user_by_id(request, user_id):
    # if not request.user.is_authenticated:
    #     return Response(status=status.HTTP_401_UNAUTHORIZED)
    #
    # # Get the user specified in the URL or return a 404 response if not found
    # user = get_object_or_404(User, id=user_id)
    #
    # # Check if the user is trying to update their own profile
    # if request.user.id != user.id:
    #     return Response(status=status.HTTP_403_FORBIDDEN)
    #
    # if request.method == 'GET':
    #     serializer = UserSerializer(instance=user)
    #     return Response(serializer.data)
    # elif request.method in ('PUT', 'PATCH'):
    #     serializer = UserProfileSerializer(
    #         instance=user,
    #         data=request.data,
    #         partial=request.method == 'PATCH'
    #     )
    #     serializer.is_valid(raise_exception=True)
    #     serializer.save()
    #     return Response(data=serializer.data)
    if not request.user.is_authenticated and request.user.is_staff:
        return Response(status=status.HTTP_401_UNAUTHORIZED)
    elif request.method == 'GET':
        user = get_object_or_404(User, id=user_id)
        serializer = UserSerializer(instance=user)
        return Response(serializer.data)
    elif request.method in ('PUT', 'PATCH'):
        user = get_object_or_404(User, id=user_id)
        serializer = UserUpdateSerializer(
            instance=user, data=request.data,
            partial=request.method == 'PATCH'
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(data=serializer.data)


# works
@api_view(['GET', 'POST'])
def get_all_companies(request):
    if request.method == 'GET':
        all_companies = Company.objects.all()
        serializer = GetCompanies(instance=all_companies, many=True)
        return Response(serializer.data)
    else:
        if not request.user.is_authenticated or not request.user.is_staff:
            return Response(status=status.HTTP_401_UNAUTHORIZED)

        else:
            serializer = AddCompany(data=request.data)
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response(data=serializer.data, status=status.HTTP_201_CREATED)


# works
@api_view(['GET', 'PATCH', 'PUT', 'DELETE'])
def get_company_by_id(request, company_id):
    company = get_object_or_404(Company, id=company_id)
    if request.method == 'GET':
        serializer = GetCompany(instance=company)
        return Response(serializer.data)

    elif request.method in ('PUT', 'PATCH'):
        if not request.user.is_authenticated and not request.user.is_staff:
            return Response(status=status.HTTP_401_UNAUTHORIZED)
        else:
            serializer = GetCompany(
                instance=company, data=request.data,
                partial=request.method == 'PATCH'
            )
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response(data=serializer.data)
    else:
        # ask if the user needs to be authenticated
        company.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


@api_view(['GET', 'PATCH', 'PUT', 'DELETE'])
def get_a_car_by_id(request, car_id):
    car = get_object_or_404(Car, id=car_id)
    if request.method == 'GET':
        serializer = GetCar(instance=car)
        return Response(serializer.data)
    elif request.method in ('PUT', 'PATCH'):
        if not request.user.is_authenticated or not request.user.is_staff or request.user != car.user:
            return Response(status=status.HTTP_401_UNAUTHORIZED)
        else:
            serializer = GetCar(
                instance=car, data=request.data,
                partial=request.method == 'PATCH'
            )
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response(data=serializer.data)
    else:
        car.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


# works I only need to check the filters
@api_view(['GET', 'POST'])
def get_all_cars(request):
    if request.method == 'GET':
        all_cars = Car.objects.all()
        if 'model' in request.query_params:
            all_cars = all_cars.filter(model_name__icontains=request.query_params['model'])
        if 'from_year_of_manufacture' in request.query_params:
            all_cars = all_cars.filter(year_of_manufacture__gte=request.query_params['from_year_of_manufacture'])
        if 'to_year_of_manufacture' in request.query_params:
            all_cars = all_cars.filter(year_of_manufacture__lte=request.query_params['to_year_of_manufacture'])
        if 'from_number_of_past_owners' in request.query_params:
            all_cars = all_cars.filter(number_of_past_owners__gte=request.query_params['from_number_of_past_owners'])
        if 'to_number_of_past_owners' in request.query_params:
            all_cars = all_cars.filter(number_of_past_owners__lte=request.query_params['to_number_of_past_owners'])
        if 'color' in request.query_params:
            all_cars = all_cars.filter(color__iexact=request.query_params['color'])
        if 'from_engine_capacity' in request.query_params:
            all_cars = all_cars.filter(engine_capacity__gte=request.query_params['from_engine_capacity'])
        if 'to_engine_capacity' in request.query_params:
            all_cars = all_cars.filter(engine_capacity__lte=request.query_params['to_engine_capacity'])
        if 'from_number_of_seats' in request.query_params:
            all_cars = all_cars.filter(number_of_seats__gte=request.query_params['from_number_of_seats'])
        if 'to_number_of_seats' in request.query_params:
            all_cars = all_cars.filter(number_of_seats__lte=request.query_params['to_number_of_seats'])
        if 'car_condition' in request.query_params:
            all_cars = all_cars.filter(car_condition__iexact=request.query_params['car_condition'])
        if 'from_mileage' in request.query_params:
            all_cars = all_cars.filter(mileage__gte=request.query_params['from_mileage'])
        if 'to_mileage' in request.query_params:
            all_cars = all_cars.filter(mileage__lte=request.query_params['to_mileage'])
        if 'transmission' in request.query_params:
            all_cars = all_cars.filter(transmission__iexact=request.query_params['transmission'])
        if 'from_price' in request.query_params:
            all_cars = all_cars.filter(price__gte=request.query_params['from_price'])
        if 'to_price' in request.query_params:
            all_cars = all_cars.filter(price__lte=request.query_params['to_price'])
        if 'city' in request.query_params:
            all_cars = all_cars.filter(user__profile__address__icontains=request.query_params['city'])

        paginator = PageNumberPagination()
        paginator.page_size = 4
        result_page = paginator.paginate_queryset(all_cars, request)

        serializer = AllCars(instance=result_page, many=True)

        if request.user.is_authenticated:
            user_saved_cars = SavedCar.objects.filter(user=request.user)
            saved_cars_ids = [saved_car.car.id for saved_car in user_saved_cars]
            for item in serializer.data:
                item['is_saved'] = item['id'] in saved_cars_ids

        # saved_user_cars = SavedCar.objects.filter(user=request.user)
        # for elem in saved_user_cars:
        #     elem.car

        # return Response(data=serializer.data)
        return paginator.get_paginated_response(serializer.data)
    else:
        if not request.user.is_authenticated and not request.user.is_staff:
            return Response(status=status.HTTP_401_UNAUTHORIZED)
        else:
            serializer = AddCar(data=request.data)
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response(data=serializer.data, status=status.HTTP_201_CREATED)


# works
@api_view(['GET'])
def get_all_cars_according_company(request, company_name):
    company = get_object_or_404(Company, company_name=company_name)
    all_cars_by_company = company.car_set.all()
    serializer = GetAllCarsByCompany(instance=all_cars_by_company, many=True)
    return Response(data=serializer.data)


@api_view(['GET', 'POST'])
def get_all_pictures_for_a_car(request, car_id):
    car = get_object_or_404(Car, id=car_id)
    if request.method == 'GET':
        pictures = Picture.objects.filter(car_id=car_id)
        serializer = AllPicturesByCar(instance=pictures, many=True)
        return Response(serializer.data)
    else:
        if request.user == car.user:
            serializer = PostAPictureByCar(data=request.data)
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response(data=serializer.data, status=status.HTTP_201_CREATED)


@api_view(['GET', 'POST'])
def get_saved_cars(request):
    if not request.user.is_authenticated:
        return Response(status=status.HTTP_401_UNAUTHORIZED)
    if request.method == 'GET':
        saved_cars = SavedCar.objects.filter(user=request.user)
        paginator = PageNumberPagination()
        paginator.page_size = 4
        result_page = paginator.paginate_queryset(saved_cars, request)
        serializer = GetSavedCars(instance=result_page, many=True)
        # serializer = AllCars(instance=result_page, many=True)

        return paginator.get_paginated_response(serializer.data)
    elif request.method == 'POST':
        serializer = AddSavedCarSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(data=serializer.data, status=status.HTTP_201_CREATED)


@api_view(['DELETE'])
def delete_saved_car(request, car_id):
    saved_car = SavedCar.objects.get(car=car_id, user=request.user)
    if request.method == 'DELETE':
        saved_car.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


@api_view(['GET'])
def get_all_models(request):
    all_models = list(Car.objects.order_by().values_list('model_name').distinct())
    all_models = [num for sublist in all_models for num in sublist]
    print(all_models)
    return JsonResponse(data=list(all_models), safe=False)


@api_view(['GET'])
def get_all_cars_for_user(request):
    if not request.user.is_authenticated:
        return Response(status=status.HTTP_401_UNAUTHORIZED)
    user = request.user
    all_cars_for_user = Car.objects.filter(user=user)
    paginator = PageNumberPagination()
    paginator.page_size = 4
    result_page = paginator.paginate_queryset(all_cars_for_user, request)
    serializer = AllCars(instance=result_page, many=True)
    return paginator.get_paginated_response(serializer.data)


@api_view(['GET'])
def get_all_companies_name(request):
    all_companies = list(Company.objects.order_by().values_list('company_name').distinct())
    all_models = [num for sublist in all_companies for num in sublist]
    print(all_models)
    return JsonResponse(data=list(all_models), safe=False)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def upload_profile_img(request):
    bucket_name = 'car_jb'
    # the content of the files will always be in request.Files and we can upload more than 1 file so request.Files is
    # a dict
    file_stream = request.FILES['file'].file
    # the ext will have the end of the file name for example :(.jpeg) and the _ variable is going to
    # have all the file string except the end
    _, ext = os.path.splitext(request.FILES['file'].name)

    object_name = f"profile_img_{uuid.uuid4()}{ext}"
    # take the information from the file we downloaded recently that contains the credentials for our cloud
    credentials = service_account.Credentials.from_service_account_file(
        "C:\\Users\\avulo\\Downloads\\cars-395918-6f32a95632d9.json")
    # here we give access to our storage , and then we specify what do we want from our storage
    storage_client = storage.Client(credentials=credentials)
    # we give our bucket name , and it goes to that bucket  if the credentials were good after that we will have our
    # bucket
    bucket = storage_client.bucket(bucket_name)
    # here we want to create an obj inside the bucket with our name , and it returns to us an obj(the file itself)
    blob = bucket.blob(object_name)
    # here we save inside the blob our file that we want to upload
    blob.upload_from_file(file_stream)

    # update the db with the new profile img
    request.user.profile.img_url = blob.public_url
    request.user.profile.save()

    userSerializer = UserProfileSerializer(request.user)
    return Response(userSerializer.data)


# this func is for not required pictures
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def upload_car_pic(request, car_id):
    bucket_name = 'car_jb'
    # the content of the files will always be in request.Files and we can upload more than 1 file so request.Files is
    # a dict
    file_stream = request.FILES['file'].file
    # the ext will have the end of the file name for example :(.jpeg) and the _ variable is going to
    # have all the file string except the end
    _, ext = os.path.splitext(request.FILES['file'].name)

    object_name = f"profile_img_{uuid.uuid4()}{ext}"
    # take the information from the file we downloaded recently that contains the credentials for our cloud
    credentials = service_account.Credentials.from_service_account_file(
        "C:\\Users\\avulo\\Downloads\\cars-395918-6f32a95632d9.json")
    # here we give access to our storage , and then we specify what do we want from our storage
    storage_client = storage.Client(credentials=credentials)
    # we give our bucket name , and it goes to that bucket  if the credentials were good after that we will have our
    # bucket
    bucket = storage_client.bucket(bucket_name)
    # here we want to create an obj inside the bucket with our name , and it returns to us an obj(the file itself)
    blob = bucket.blob(object_name)
    # here we save inside the blob our file that we want to upload
    blob.upload_from_file(file_stream)

    # update the db with the new img
    picture = Picture(car_id=car_id, original=blob.public_url, thumbnail=blob.public_url)
    # Save the Picture instance to the database
    picture.save()
    # request.user.profile.save()

    serializer = AllPicturesByCar(instance=picture)
    return Response(serializer.data)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def upload_main_car_pic(request, car_id):
    bucket_name = 'car_jb'
    # the content of the files will always be in request.Files and we can upload more than 1 file so request.Files is
    # a dict
    file_stream = request.FILES['file'].file
    # the ext will have the end of the file name for example :(.jpeg) and the _ variable is going to
    # have all the file string except the end
    _, ext = os.path.splitext(request.FILES['file'].name)

    object_name = f"profile_img_{uuid.uuid4()}{ext}"
    # take the information from the file we downloaded recently that contains the credentials for our cloud
    credentials = service_account.Credentials.from_service_account_file(
        "C:\\Users\\avulo\\Downloads\\cars-395918-6f32a95632d9.json")
    # here we give access to our storage , and then we specify what do we want from our storage
    storage_client = storage.Client(credentials=credentials)
    # we give our bucket name , and it goes to that bucket  if the credentials were good after that we will have our
    # bucket
    bucket = storage_client.bucket(bucket_name)
    # here we want to create an obj inside the bucket with our name , and it returns to us an obj(the file itself)
    blob = bucket.blob(object_name)
    # here we save inside the blob our file that we want to upload
    blob.upload_from_file(file_stream)

    # update the db with the new img
    car = get_object_or_404(Car, id=car_id)

    # Save the Picture instance to the database
    car.pic_url = blob.public_url
    car.save()
    carSerializer = GetCar(instance=car)
    return Response(carSerializer.data)
