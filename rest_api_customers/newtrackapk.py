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
from calculator.models import OrderCart


class CustomUserUnauthorizedThrottle(UserRateThrottle):
    rate = '15/minute'


@method_decorator(cache_page(60*1), name='dispatch')
class NewTrackAPK(APIView):
    permission_classes = [AllowAny, ]
    throttle_classes = [CustomUserUnauthorizedThrottle, ]

    def get(self, request, barcode):
        if (barcode[:2] == "RZ" or barcode[:2] == "CZ" or barcode[:1] == "E") and barcode[:3] != "EHM" and barcode[:3] != "EMI":
            wsdl = 'http://10.100.0.69/IPSAPIService/TrackAndTraceService.svc?singleWsdl'

            # SOAP servisi uchun ulanish
            client = Client(wsdl=wsdl)

            # Parametrlar tayyorlash
            ids = barcode
            # lang = 'RU'
            token = '269a208f-7006-4dc6-b52f-6dfba6af113a'

            # GetMailitems metodini chaqirish
            response = client.service.GetMailitems(ids=ids, token=token)

            # SOAP javobini dictionary'ga aylantirish
            response_data = serialize_object(response)
            if response_data == None:
                first = {
                    "code": "order_not_found",
                    "message": "Order Not Found",
                    "request_id": "69f059d0-1748-42cc-982c-7a322c4e81fa",
                    "status": "error"
                }
                return Response(data=first, status=status.HTTP_404_NOT_FOUND)
            response_data_2 = response_data
            if response_data_2[0]["InfoFromEdi"] != None:
                for i in range(len(
                        response_data_2[0]["InfoFromEdi"]["TMailitemInfoFromEDI"][0]["Events"]["TMailitemEventEDI"])):
                    response_data_2[0]["InfoFromEdi"]["TMailitemInfoFromEDI"][0]["Events"]["TMailitemEventEDI"][i][
                        "ReceivedDispatch"] = None
            if response_data_2[0]["OperationalMailitems"] != None:
                for j in range(len(response_data_2[0]["OperationalMailitems"]["TMailitemInfoFromScanning"][0]["Events"][
                                       "TMailitemEventScanning"])):
                    response_data_2[0]["OperationalMailitems"]["TMailitemInfoFromScanning"][0]["Events"][
                        "TMailitemEventScanning"][j]["ReceivedDispatch"] = None
            return Response(data=response_data_2, status=status.HTTP_200_OK)

        # header keladigan data
        max_retries = 1  # Maksimal urinishlar soni
        retry_delay = 1  # Qayta urinishdan oldin kutish (soniyada)
        url_header = f"https://prodapi.pochta.uz/api/v1/public/order/{barcode}"
        url_shipox = f"https://prodapi.pochta.uz/api/v1/public/order/{barcode}/history_items"

        for attempt in range(max_retries):
            try:
                # APIga so'rov yuborish
                data_header = requests.get(url_header, timeout=1)
                data_shipox = requests.get(url_shipox, timeout=1)

                data_header = data_header.json()
                data_shipox = data_shipox.json()
                # API'dan muvaffaqiyatli javob olinsa, ma'lumotni qaytarish
                if data_header.get('status') == "success":
                    total_data_2 = {'header': data_header}
                    if barcode[:2] != 'SX' and data_header["data"]['locations'][0]['country']['code'] == 'UZ' and \
                            data_header["data"]['locations'][1]['country']['code'] == 'UZ':

                        total_data_2['shipox'] = data_shipox
                        total_data_2['gdeposilka'] = None
                        return Response(total_data_2, status=status.HTTP_200_OK)
                    total_data_2 = {"header": data_header, "shipox": data_shipox}

                    # gdeposilka ma'lumotlari shipox bilan bog'liqlari

                    url1 = f"https://gdeposylka.ru/api/v4/tracker/detect/{barcode}"
                    headers = {
                        "X-Authorization-Token": "65bbbac85f796f8032e0874411f4d1f5af7185a99e184709bf0c1f38d95486fa2338733760a48704"
                    }
                    response1 = requests.get(url1, headers=headers)
                    data = response1.json()

                    if len(data["data"]) != 0:
                        url2 = f"https://gdeposylka.ru{data['data'][0]['tracker_url']}"
                        response2 = requests.get(url2, headers=headers)
                        response_x = response2.json()
                        if len(response_x["messages"]) == 0:
                            gdeposylka = {
                                "result": response_x['result'],
                                'data': {
                                    'id': response_x['data']['id'],
                                    'tracking_number': response_x['data']['tracking_number'],
                                    "tracking_number_secondary": response_x['data']['tracking_number_secondary'],
                                    "tracking_number_current": response_x['data']['tracking_number_current'],
                                    "courier": response_x['data']['courier'],
                                    "is_active": response_x['data']['is_active'],
                                    "is_delivered": response_x['data']['is_delivered'],
                                    "last_check": response_x['data']['last_check'],
                                    'checkpoints': [],
                                    "extra": response_x['data']['extra']
                                }
                            }
                            for points in response_x['data']['checkpoints']:
                                if points['courier']['slug'] != 'ozbekiston-pochtasi':
                                    gdeposylka['data']['checkpoints'].append(points)
                            total_data_2['gdeposilka'] = gdeposylka
                        else:
                            time.sleep(15)
                            response2 = requests.get(url2, headers=headers)
                            response_x = response2.json()
                            if len(response_x['messages']) == 0:
                                gdeposylka = {
                                    "result": response_x['result'],
                                    'data': {
                                        'id': response_x['data']['id'],
                                        'tracking_number': response_x['data']['tracking_number'],
                                        "tracking_number_secondary": response_x['data']['tracking_number_secondary'],
                                        "tracking_number_current": response_x['data']['tracking_number_current'],
                                        "courier": response_x['data']['courier'],
                                        "is_active": response_x['data']['is_active'],
                                        "is_delivered": response_x['data']['is_delivered'],
                                        "last_check": response_x['data']['last_check'],
                                        'checkpoints': [],
                                        "extra": response_x['data']['extra']
                                    }
                                }
                                for points in response_x['data']['checkpoints']:
                                    if points['courier']['slug'] != 'ozbekiston-pochtasi':
                                        gdeposylka['data']['checkpoints'].append(points)
                                total_data_2['gdeposilka'] = gdeposylka
                            else:
                                total_data_2['gdeposilka'] = "please try again we are processing the data"
                        return Response(total_data_2, status=status.HTTP_200_OK)
                    total_data_2['gdeposilka'] = None
                    return Response(total_data_2, status=status.HTTP_200_OK)
                else:
                    total_data_2 = {"header": None, "shipox": None}

            except ConnectTimeout:
                # Agar ulanish timeoutga uchrasa, qayta urinib ko'riladi
                if attempt < max_retries - 1:
                    time.sleep(retry_delay)  # Kutish va yana urinib ko'rish
                else:
                    total_data_2 = {"header": "Server bilan ulanishda muammo yuz berdi. Iltimos, keyinroq qayta urinib ko'ring.",
                                    "gdeposilka_header": None,
                                    "shipox": "Server bilan bo'glanishda muammo yuz berdi"}


        # shipoxga bo'g'liq bo'lmagan gdeposilka ma'lumotlari


        url1 = f"https://gdeposylka.ru/api/v4/tracker/detect/{barcode}"
        headers = {
            "X-Authorization-Token": "65bbbac85f796f8032e0874411f4d1f5af7185a99e184709bf0c1f38d95486fa2338733760a48704"
        }
        response1 = requests.get(url1, headers=headers)
        data = response1.json()

        if len(data["data"]) != 0:
            url2 = f"https://gdeposylka.ru{data['data'][0]['tracker_url']}"
            response2 = requests.get(url2, headers=headers)
            response_x = response2.json()
            if len(response_x["messages"]) == 0:
                # gdeposylka = {
                #     "result": response_x['result'],
                #     'data': {
                #         'id': response_x['data']['id'],
                #         'tracking_number': response_x['data']['tracking_number'],
                #         "tracking_number_secondary": response_x['data']['tracking_number_secondary'],
                #         "tracking_number_current": response_x['data']['tracking_number_current'],
                #         "courier": response_x['data']['courier'],
                #         "is_active": response_x['data']['is_active'],
                #         "is_delivered": response_x['data']['is_delivered'],
                #         "last_check": response_x['data']['last_check'],
                #         'checkpoints': [],
                #         "extra": response_x['data']['extra']
                #     }
                # }
                # for points in response_x['data']['checkpoints']:
                #     if points['courier']['slug'] != 'ozbekiston-pochtasi':
                #         gdeposylka['data']['checkpoints'].append(points)
                total_data_2['gdeposilka'] = response_x
            else:
                time.sleep(15)
                response2 = requests.get(url2, headers=headers)
                response_x = response2.json()
                if len(response_x['messages']) == 0:
                    # gdeposylka = {
                    #     "result": response_x['result'],
                    #     'data': {
                    #         'id': response_x['data']['id'],
                    #         'tracking_number': response_x['data']['tracking_number'],
                    #         "tracking_number_secondary": response_x['data']['tracking_number_secondary'],
                    #         "tracking_number_current": response_x['data']['tracking_number_current'],
                    #         "courier": response_x['data']['courier'],
                    #         "is_active": response_x['data']['is_active'],
                    #         "is_delivered": response_x['data']['is_delivered'],
                    #         "last_check": response_x['data']['last_check'],
                    #         'checkpoints': [],
                    #         "extra": response_x['data']['extra']
                    #     }
                    # }
                    # for points in response_x['data']['checkpoints']:
                    #     if points['courier']['slug'] != 'ozbekiston-pochtasi':
                    #         gdeposylka['data']['checkpoints'].append(points)
                    total_data_2['gdeposilka'] = response_x

                else:
                    total_data_2['gdeposilka'] = "please try again we are processing the data"
            return Response(total_data_2, status=status.HTTP_200_OK)
        total_data_2['gdeposilka'] = None
        return Response(total_data_2, status=status.HTTP_200_OK)