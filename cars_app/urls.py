from django.contrib import admin
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

from cars_app.views import *


urlpatterns = [
    path('auth/login', TokenObtainPairView.as_view()),
    path('auth/refresh', TokenRefreshView.as_view()),
    path('auth/signup', signup),
    path('auth/get_all_users', get_all_users),
    path('auth/current_user_details', current_user_details),
    path('auth/get_a_user_by_name/<int:user_id>', get_a_user_by_id),
    path('all_companies', get_all_companies),
    path('get_a_company_by_id/<int:company_id>', get_company_by_id),
    path('get_a_car_by_id/<int:car_id>', get_a_car_by_id),
    path('all_cars', get_all_cars),
    path('get_all_cars_by_company/<str:company_name>',get_all_cars_according_company),
    path('get_all_pictures_for_a_car/<int:car_id>',get_all_pictures_for_a_car),
    path('saved_cars', get_saved_cars),
    path('delete_saved_car/<int:car_id>', delete_saved_car),
    path('all_models', get_all_models),
    path('all_cars_for_user', get_all_cars_for_user),
    path('all_companies_name', get_all_companies_name),
    path('profile/img', upload_profile_img),
    path('upload_main_car_pic/<int:car_id>',upload_main_car_pic),
    path('upload_extra_car_pic/<int:car_id>', upload_car_pic),
    path('saved_cars_ids_for_user', get_saved_car_ids_for_user)

]

