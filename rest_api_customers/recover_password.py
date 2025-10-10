from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.viewsets import ModelViewSet
from rest_framework.response import Response
from rest_framework import status, viewsets
from rest_framework.permissions import IsAuthenticated, IsAdminUser, AllowAny, BasePermission
from rest_framework.authentication import TokenAuthentication
from rest_framework.pagination import LimitOffsetPagination
from rest_framework import status, filters
from models.models import CustomUser
from django.db.transaction import atomic
from rest_framework.response import Response
from django.contrib.auth.hashers import make_password
from django.shortcuts import get_object_or_404
from rest_framework.throttling import UserRateThrottle
import requests
import time
from rest_framework.decorators import action
from django.contrib.auth.models import Group, Permission

# new
from models.models import (CustomUser, UsersRequests, IPAddressLog, CheckSMS)
from django.views.decorators.cache import cache_page
from django.utils.decorators import method_decorator
from zeep import Client
from zeep.helpers import serialize_object

from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework_simplejwt.tokens import RefreshToken
from .serializer import CustomTokenObtainPairSerializer
from core.middleware import static_token_required
from rest_framework.pagination import PageNumberPagination
from django_filters import rest_framework as filters
from django_filters.rest_framework import DjangoFilterBackend
from requests.auth import HTTPBasicAuth
from random import randint
import uuid
from django.utils import timezone

from datetime import timedelta
from dotenv import load_dotenv
from .send_sms import send_sms
import os

load_dotenv()


class CustomUserUnauthorizedThrottle(UserRateThrottle):
    rate = '15/minute'


class RecoverPassword3APIView(APIView):
    throttle_classes = [CustomUserUnauthorizedThrottle, ]
    def post(self, request):
        phone_number = request.data.get('phone_number')
        if not phone_number:
            return Response(data="No phone number provided", status=status.HTTP_400_BAD_REQUEST)
        if type(phone_number) != str:
            return Response(data="phone number is type invalid it is type str", status=status.HTTP_400_BAD_REQUEST)
        if len(phone_number) != 9:
            return Response(data="phone number should not exceed 9 characters", status=status.HTTP_400_BAD_REQUEST)
        if not phone_number.isdigit():
            return Response(data="Phone number is invalid", status=status.HTTP_400_BAD_REQUEST)
        database_number = f"+998{phone_number}"
        custom_user = CustomUser.objects.filter(phone_number=database_number).first()
        if not custom_user:
            return Response("this phone number does not exist", status=status.HTTP_400_BAD_REQUEST)

        check_code = CheckSMS.objects.filter(phone_number=database_number).order_by("-created_at").first()
        if not check_code:
            sms = send_sms(phone_number)
            return Response(data=sms, status=status.HTTP_400_BAD_REQUEST)

        if check_code.status != True:
            code = request.data.get("code")
            if code is None:
                return Response(data="code is invalid", status=status.HTTP_400_BAD_REQUEST)
            check_code = CheckSMS.objects.filter(phone_number=database_number).order_by("-created_at").first()
            if not check_code:
                return Response(data="code does not exist", status=status.HTTP_400_BAD_REQUEST)
            if code != check_code.code:
                return Response(data="code is invalid", status=status.HTTP_400_BAD_REQUEST)
            check_code.status = True
            check_code.save()
            return Response(data="success", status=status.HTTP_200_OK)

        password = request.data.get('password')
        if not password:
            return Response(data="Password must be entered", status=status.HTTP_400_BAD_REQUEST)
        if type(password) != str:
            return Response(data="password is type invalid it is type str", status=status.HTTP_400_BAD_REQUEST)
        if len(password) < 6:
            return Response('password must be longer than 6 characters', status=status.HTTP_400_BAD_REQUEST)

        custom_user.set_password(password)
        custom_user.save()
        refresh = RefreshToken.for_user(custom_user)
        id_token = str(refresh.access_token)
        data = {
            "phone_number": database_number,
            'first_name': custom_user.first_name,
            'last_name': custom_user.last_name,
            'region': custom_user.region,
            'district': custom_user.district,
            "index": custom_user.post_index,
            'password': "********",
            "image": None,
            "status": "successful",
            "id_token": id_token
        }

        check_code.delete()
        all_sms = CheckSMS.objects.filter(phone_number=database_number)
        all_sms.delete()
        return Response(data=data, status=status.HTTP_201_CREATED)



