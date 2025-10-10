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
from django.views.decorators.cache import cache_page
from django.utils.decorators import method_decorator
from zeep import Client
from zeep.helpers import serialize_object

from rest_framework_simplejwt.views import TokenObtainPairView
from core.middleware import static_token_required
from rest_framework.pagination import PageNumberPagination
from django_filters import rest_framework as filters
from django_filters.rest_framework import DjangoFilterBackend
<<<<<<< HEAD
from .import_data import import_data
from .models import Warehouse
from .serializers import WarehouseSerializer
from .views import gettoken

=======
from maps.models import Warehouse
from maps.serializers import WarehouseSerializer
from .views import gettoken
from .models import OrderCart
from dotenv import load_dotenv
import os

load_dotenv()
>>>>>>> 2d32d04 (full complated uzpost backend)

class CustomUserThrottle(UserRateThrottle):
    rate = '30/minute'


class CreateOrderApiView(APIView):
<<<<<<< HEAD
    # permission_classes = [IsAuthenticated, ]
    throttle_classes = [CustomUserThrottle, ]

    def post(self, request):
=======
    permission_classes = [IsAuthenticated, ]
    throttle_classes = [CustomUserThrottle, ]

    def post(self, request):
        user = request.user
>>>>>>> 2d32d04 (full complated uzpost backend)
        headers = {
            'Content-Type': 'application/json',
            'Accept': 'application/json',
            'Authorization': f'Bearer {gettoken()}'
        }

        weight = request.query_params.get("Weight")
<<<<<<< HEAD
        if weight is None or type(weight) != float:
            return Response(data="invalid Weight",
                            status=status.HTTP_400_BAD_REQUEST)
        try:
            weight = int(weight)
=======
        if weight is None:
            return Response(data="invalid Weight",
                            status=status.HTTP_400_BAD_REQUEST)
        try:
            weight = float(weight)
>>>>>>> 2d32d04 (full complated uzpost backend)
        except ValueError:
            return Response(data="Invalid Weight: Must be an float", status=status.HTTP_400_BAD_REQUEST)

        service_type_id = request.query_params.get("ServiceTypeId")

        if service_type_id is None:
            return Response(data="invalid ServiceTypeId", status=status.HTTP_400_BAD_REQUEST)
        try:
            service_type_id = int(service_type_id)
        except ValueError:
            return Response(data="Invalid ServiceTypeId: Must be an int", status=status.HTTP_400_BAD_REQUEST)

        fromjurisdiction_id = request.query_params.get("FromJurisDictionId")

        if fromjurisdiction_id is None:
            return Response(data="invalid FromJurisDictionId", status=status.HTTP_400_BAD_REQUEST)
        try:
            fromjurisdiction_id = int(fromjurisdiction_id)
        except ValueError:
            return Response(data="Invalid FromJurisDictionId: Must be an int", status=status.HTTP_400_BAD_REQUEST)

        tojurisdiction_id = request.query_params.get("ToJurisDictionId")

        if tojurisdiction_id is None:
            return Response(data="invalid ToJurisDictionId", status=status.HTTP_400_BAD_REQUEST)
        try:
            tojurisdiction_id = int(tojurisdiction_id)
        except ValueError:
            return Response(data="Invalid ToJurisDictionId: Must be an int", status=status.HTTP_400_BAD_REQUEST)

        SenderName = request.query_params.get("SenderName")

        if SenderName is None:
            return Response(data="invalid SenderName", status=status.HTTP_400_BAD_REQUEST)

        SenderPhoneNumber = request.query_params.get("SenderPhoneNumber")

        if SenderPhoneNumber is None:
            return Response(data="invalid SenderPhoneNumber", status=status.HTTP_400_BAD_REQUEST)

<<<<<<< HEAD
        SenderAddress = request.query_params.get("sender_address")
        if SenderAddress is None:
            return Response(data="invalid Address", status=status.HTTP_400_BAD_REQUEST)
=======
        SenderAddress = request.query_params.get("SenderAddress")
        if SenderAddress is None:
            return Response(data="invalid SenderAddress", status=status.HTTP_400_BAD_REQUEST)
>>>>>>> 2d32d04 (full complated uzpost backend)

        ReseipentName = request.query_params.get("ReseipmentName")
        if ReseipentName is None:
            return Response(data="invalid ReseipmentName", status=status.HTTP_400_BAD_REQUEST)

        ReseipentPhoneNumber = request.query_params.get("ReseipmentPhoneNumber")
        if ReseipentPhoneNumber is None:
            return Response(data="invalid ReseipmentPhoneNumber", status=status.HTTP_400_BAD_REQUEST)

        ReseipentAddress = request.query_params.get("ReseipmentAddress")
        if ReseipentAddress is None:
            return Response(data="invalid ReseipmentAddress", status=status.HTTP_400_BAD_REQUEST)
        ######################################################################################################
        request_services = requests.get('https://prodapi.pochta.uz/api/v1/service_types', headers=headers)
        services = request_services.json()
        service_code = "xxx"
        for service in services["data"]["list"]:
            if service["id"] == service_type_id:
                service_code = service["code"]

        request = requests.get('https://prodapi.pochta.uz/api/v2/jurisdiction/choose/list', headers=headers)
        locations = request.json()
        SenderJurisdictionId = 0
        SenderJurisdictionName = ""
        SenderJurisdictionCode = ""
        SenderJurisdictionLattitude = 0
        SenderJurisdictionLongitude = 0

        for location in locations["data"]:
            if location["id"] == fromjurisdiction_id:
                SenderJurisdictionId = location["id"]
                SenderJurisdictionName = location["name"]
                SenderJurisdictionCode = location["code"]
                SenderJurisdictionLattitude = location["lat"]
                SenderJurisdictionLongitude = location["lng"]
        ReseipentJurisdictionId = 0
        ReseipentJurisdictionName = ""
        ReseipentJurisdictionCode = ""
        for reseipent in locations["data"]:
            if reseipent["id"] == tojurisdiction_id:
                ReseipentJurisdictionId = reseipent["id"]
                ReseipentJurisdictionName = reseipent["name"]
                ReseipentJurisdictionCode = reseipent["code"]

        create_order = {
            "payment_type": "cash",
            "transportation_type": "terrestrial",
            "service_type": {
                "code": f"{service_code}"
            },
            "sender_data": {
                "jurisdiction": {
                    "id": SenderJurisdictionId,
                    "name": f"{SenderJurisdictionName}",
                    "code": f"{SenderJurisdictionCode}"
                },
                "customer": {
                    "name": f"{SenderName}"
                },
                "phone": f"{SenderPhoneNumber}",
                "address": f"{SenderAddress}",
                "lat": SenderJurisdictionLattitude,
                "lon": SenderJurisdictionLongitude
            },
            "recipient_data": {
                "jurisdiction": {
                    "id": ReseipentJurisdictionId,
                    "name": f"{ReseipentJurisdictionName}",
                    "code": f"{ReseipentJurisdictionCode}"
                },
                "customer": {
                    "name": f"{ReseipentName}"
                },
                "phone": f"{ReseipentPhoneNumber}",
                "address": f"{ReseipentAddress}"
            },
            "dimensions": {
                "width": 0,
                "length": 0,
                "height": 0,
                "weight": float(weight)
            }
        }
        result = requests.post("https://prodapi.pochta.uz/api/v1/customer/order", json=create_order, headers=headers)
<<<<<<< HEAD
=======
        if result.json()["status"] == "success":
            OrderCart.objects.create(
                user=user,
                weight=result.json()["data"]["dimensions"]["weight"],
                barcode=result.json()["data"]["order_number"],
                fromjurisdiction=f"{result.json()['data']['sender_data']['jurisdiction']['parent']['parent']['name']}, "
                                 f"{result.json()['data']['sender_data']['jurisdiction']['parent']['name']}, "
                                 f"{result.json()['data']['sender_data']['jurisdiction']['name']}, "
                                 f"{result.json()['data']['sender_data']['address']}, "
                                 f"{result.json()['data']['sender_data']['postcode_index']}, "
                                 f"{result.json()['data']['sender_data']['phone']}",
                tojurisdiction=f"{result.json()['data']['recipient_data']['jurisdiction']['parent']['parent']['name']}, "
                               f"{result.json()['data']['recipient_data']['jurisdiction']['parent']['name']}, "
                               f"{result.json()['data']['recipient_data']['jurisdiction']['name']}, "
                               f"{result.json()['data']['recipient_data']['address']}, "
                               f"{result.json()['data']['recipient_data']['postcode_index']}, "
                               f"{result.json()['data']['recipient_data']['phone']}",
                from_phone_number=result.json()["data"]["sender_data"]["phone"],
                to_phone_number=result.json()["data"]["recipient_data"]["phone"],
                full_name=result.json()["data"]["sender_data"]["name"],
                from_country_code=result.json()["data"]["sender_data"]["country"]["code"],
                to_country_code=result.json()["data"]["recipient_data"]["country"]["code"],
                price=result.json()["data"]["total_charge"],
                price_code=result.json()["data"]["currency"]["name"],
                payment_type=result.json()["data"]["payment_type"],
                shipment_type=f"{result.json()['data']['package_type']['name']}, "
                              f"{result.json()['data']['package_type']['courier_type']['name']}",
                shipox_created_at=result.json()["data"]["created_date"],
                shipox_last_status_date=result.json()["data"]["last_status_date"],
                order_status=True,
                response_data=result.json(),
            )
>>>>>>> 2d32d04 (full complated uzpost backend)
        return Response(data=result.json(), status=status.HTTP_200_OK)


class CreateOderIndexAPIView(APIView):
<<<<<<< HEAD
    # permission_classes = [IsAuthenticated, ]
    throttle_classes = [CustomUserThrottle, ]
    def post(self, request):
=======
    permission_classes = [IsAuthenticated, ]
    throttle_classes = [CustomUserThrottle, ]


    def post(self, request):
        user = request.user
>>>>>>> 2d32d04 (full complated uzpost backend)
        headers = {
            'Content-Type': 'application/json',
            'Accept': 'application/json',
            'Authorization': f'Bearer {gettoken()}'
        }

        weight = request.query_params.get("Weight")
<<<<<<< HEAD
        if weight is None or type(weight) != float:
            return Response(data="invalid Weight",
                            status=status.HTTP_400_BAD_REQUEST)
        try:
            weight = int(weight)
=======
        if weight is None:
            return Response(data="invalid Weight", status=status.HTTP_400_BAD_REQUEST)
        try:
            weight = float(weight)
>>>>>>> 2d32d04 (full complated uzpost backend)
        except ValueError:
            return Response(data="Invalid Weight: Must be an float", status=status.HTTP_400_BAD_REQUEST)

        service_type_id = request.query_params.get("ServiceTypeId")

        if service_type_id is None:
            return Response(data="invalid ServiceTypeId", status=status.HTTP_400_BAD_REQUEST)
        try:
            service_type_id = int(service_type_id)
        except ValueError:
            return Response(data="Invalid ServiceTypeId: Must be an int", status=status.HTTP_400_BAD_REQUEST)

        fromjurisdiction_id = request.query_params.get("FromJurisDictionId")

        if fromjurisdiction_id is None:
            return Response(data="invalid FromJurisDictionId", status=status.HTTP_400_BAD_REQUEST)
        try:
            fromjurisdiction_id = int(fromjurisdiction_id)
        except ValueError:
            return Response(data="Invalid FromJurisDictionId: Must be an int", status=status.HTTP_400_BAD_REQUEST)

        Index = request.query_params.get("Index")

        if Index is None:
            return Response(data="invalid Index", status=status.HTTP_400_BAD_REQUEST)
        try:
<<<<<<< HEAD
            Index = int(tojurisdiction_id)
=======
            Index = int(Index)
>>>>>>> 2d32d04 (full complated uzpost backend)
        except ValueError:
            return Response(data="Invalid Index: Must be an int", status=status.HTTP_400_BAD_REQUEST)

        SenderName = request.query_params.get("SenderName")

        if SenderName is None:
            return Response(data="invalid SenderName", status=status.HTTP_400_BAD_REQUEST)

        SenderPhoneNumber = request.query_params.get("SenderPhoneNumber")

        if SenderPhoneNumber is None:
            return Response(data="invalid SenderPhoneNumber", status=status.HTTP_400_BAD_REQUEST)

<<<<<<< HEAD
        SenderAddress = request.query_params.get("sender_address")
        if SenderAddress is None:
            return Response(data="invalid Address", status=status.HTTP_400_BAD_REQUEST)
=======
        SenderAddress = request.query_params.get("SenderAddress")
        if SenderAddress is None:
            return Response(data="invalid SenderAddress", status=status.HTTP_400_BAD_REQUEST)
>>>>>>> 2d32d04 (full complated uzpost backend)

        ReseipentName = request.query_params.get("ReseipmentName")
        if ReseipentName is None:
            return Response(data="invalid ReseipmentName", status=status.HTTP_400_BAD_REQUEST)

        ReseipentPhoneNumber = request.query_params.get("ReseipmentPhoneNumber")
        if ReseipentPhoneNumber is None:
            return Response(data="invalid ReseipmentPhoneNumber", status=status.HTTP_400_BAD_REQUEST)

        ReseipentAddress = request.query_params.get("ReseipmentAddress")
        if ReseipentAddress is None:
            return Response(data="invalid ReseipmentAddress", status=status.HTTP_400_BAD_REQUEST)

        request_services = requests.get('https://prodapi.pochta.uz/api/v1/service_types', headers=headers)
        services = request_services.json()
        service_code = "xxx"
        for service in services["data"]["list"]:
            if service["id"] == service_type_id:
                service_code = service["code"]

        request = requests.get('https://prodapi.pochta.uz/api/v2/jurisdiction/choose/list', headers=headers)
        locations = request.json()
        SenderJurisdictionId = 0
        SenderJurisdictionName = ""
        SenderJurisdictionCode = ""
        SenderJurisdictionLattitude = 0
        SenderJurisdictionLongitude = 0

        for location in locations["data"]:
            if location["id"] == fromjurisdiction_id:
                SenderJurisdictionId = location["id"]
                SenderJurisdictionName = location["name"]
                SenderJurisdictionCode = location["code"]
                SenderJurisdictionLattitude = location["lat"]
                SenderJurisdictionLongitude = location["lng"]
        ReseipentJurisdictionId = 0
        ReseipentJurisdictionName = ""
        ReseipentJurisdictionCode = ""
        warehouse = Warehouse.objects.filter(index=str(Index)).first()

        if warehouse is None:
            return Response(data="inform not found", status=status.HTTP_400_BAD_REQUEST)


        ToJurisdictionId = warehouse.city_id
        for reseipent in locations["data"]:
            if reseipent["id"] == ToJurisdictionId:
                ReseipentJurisdictionId = reseipent["id"]
                ReseipentJurisdictionName = reseipent["name"]
                ReseipentJurisdictionCode = reseipent["code"]

        create_order = {
            "payment_type": "cash",
            "transportation_type": "terrestrial",
            "service_type": {
                "code": f"{service_code}"
            },
            "sender_data": {
                "jurisdiction": {
                    "id": SenderJurisdictionId,
                    "name": f"{SenderJurisdictionName}",
                    "code": f"{SenderJurisdictionCode}"
                },
                "customer": {
                    "name": f"{SenderName}"
                },
                "phone": f"{SenderPhoneNumber}",
                "address": f"{SenderAddress}",
                "lat": SenderJurisdictionLattitude,
                "lon": SenderJurisdictionLongitude
            },
            "recipient_data": {
                "jurisdiction": {
                    "id": ReseipentJurisdictionId,
                    "name": f"{ReseipentJurisdictionName}",
                    "code": f"{ReseipentJurisdictionCode}"
                },
                "customer": {
                    "name": f"{ReseipentName}"
                },
                "phone": f"{ReseipentPhoneNumber}",
                "address": f"{warehouse.warehouse_name}"
            },
            "dimensions": {
                "width": 0,
                "length": 0,
                "height": 0,
                "weight": float(weight)
            }
        }
        result = requests.post("https://prodapi.pochta.uz/api/v1/customer/order", json=create_order, headers=headers)
<<<<<<< HEAD
=======
        if result.json()["status"] == "success":
            OrderCart.objects.create(
                user=user,
                weight=result.json()["data"]["dimensions"]["weight"],
                barcode=result.json()["data"]["order_number"],
                fromjurisdiction=f"{result.json()['data']['sender_data']['jurisdiction']['parent']['parent']['name']}, "
                                 f"{result.json()['data']['sender_data']['jurisdiction']['parent']['name']}, "
                                 f"{result.json()['data']['sender_data']['jurisdiction']['name']}, "
                                 f"{result.json()['data']['sender_data']['address']}, "
                                 f"{result.json()['data']['sender_data']['postcode_index']}, "
                                 f"{result.json()['data']['sender_data']['phone']}",
                tojurisdiction=f"{result.json()['data']['recipient_data']['jurisdiction']['parent']['parent']['name']}, "
                               f"{result.json()['data']['recipient_data']['jurisdiction']['parent']['name']}, "
                               f"{result.json()['data']['recipient_data']['jurisdiction']['name']}, "
                               f"{result.json()['data']['recipient_data']['address']}, "
                               f"{result.json()['data']['recipient_data']['postcode_index']}, "
                               f"{result.json()['data']['recipient_data']['phone']}",
                from_phone_number=result.json()["data"]["sender_data"]["phone"],
                to_phone_number=result.json()["data"]["recipient_data"]["phone"],
                full_name=result.json()["data"]["sender_data"]["name"],
                from_country_code=result.json()["data"]["sender_data"]["country"]["code"],
                to_country_code=result.json()["data"]["recipient_data"]["country"]["code"],
                price=result.json()["data"]["total_charge"],
                price_code=result.json()["data"]["currency"]["name"],
                payment_type=result.json()["data"]["payment_type"],
                shipment_type=f"{result.json()['data']['package_type']['name']}, "
                              f"{result.json()['data']['package_type']['courier_type']['name']}",
                shipox_created_at=result.json()["data"]["created_date"],
                shipox_last_status_date=result.json()["data"]["last_status_date"],
                order_status=True,
                response_data=result.json(),
            )

>>>>>>> 2d32d04 (full complated uzpost backend)
        return Response(data=result.json(), status=status.HTTP_200_OK)


class CancelOrderAPIView(APIView):
<<<<<<< HEAD
    # permission_classes = [IsAuthenticated, ]
    throttle_classes = [CustomUserThrottle, ]
    def put(self, request):
=======
    permission_classes = [IsAuthenticated, ]
    throttle_classes = [CustomUserThrottle, ]
    def put(self, request):
        user= request.user
>>>>>>> 2d32d04 (full complated uzpost backend)
        headers = {
            'Content-Type': 'application/json',
            'Accept': 'application/json',
            'Authorization': f'Bearer {gettoken()}'
        }
        barcode = request.query_params.get("barcode")
        if not barcode:
            return Response(data="invalid barcode", status=status.HTTP_400_BAD_REQUEST)
<<<<<<< HEAD
        result = requests.put(f"https://prodapi.pochta.uz/api/v1/customer/order/cancel?barcode={barcode}", headers=headers)
=======
        user_order = OrderCart.objects.filter(barcode=barcode).first()
        if not user_order:
            return Response("Not found", status=status.HTTP_404_NOT_FOUND)
        if user_order.user != user:
            return Response("you do not have permission to perform this action", status=status.HTTP_403_FORBIDDEN)
        result = requests.put(f"https://prodapi.pochta.uz/api/v1/customer/order/cancel?barcode={barcode}", headers=headers)
        if result.json()["status"] == "success":
            user_order.order_status = False
            user_order.save()
            return Response(data=result.json(), status=status.HTTP_200_OK)
        return Response(data=result.json(), status=status.HTTP_200_OK)


class ShippingLabelOrderAPIView(APIView):
    permission_classes = [IsAuthenticated, ]
    throttle_classes = [CustomUserThrottle, ]

    def get(self, request):
        headers = {
            'Content-Type': 'application/json',
            #'Accept': 'application/json',
            'Authorization': f'Bearer {gettoken()}'
        }
        # barcode = request.query_params.get("barcode")
        # if not barcode:
        #     return Response(data="invalid barcode", status=status.HTTP_400_BAD_REQUEST)
        print(request.user)
        result = requests.get(f"https://prodapi.pochta.uz/api/v2/customer/230707", headers=headers)
>>>>>>> 2d32d04 (full complated uzpost backend)
        return Response(data=result.json(), status=status.HTTP_200_OK)
