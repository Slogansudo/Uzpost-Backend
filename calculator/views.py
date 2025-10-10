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

<<<<<<< HEAD
from rest_framework_simplejwt.views import TokenObtainPairView
=======
>>>>>>> 2d32d04 (full complated uzpost backend)
from core.middleware import static_token_required
from rest_framework.pagination import PageNumberPagination
from django_filters import rest_framework as filters
from django_filters.rest_framework import DjangoFilterBackend
<<<<<<< HEAD
from .import_data import import_data
from .ImportPochtamat import ImportPostalOffice
from .models import Warehouse
from .serializers import WarehouseSerializer
=======
from maps.models import Warehouse
from maps.serializers import WarehouseSerializer
from dotenv import load_dotenv
import os

load_dotenv()
>>>>>>> 2d32d04 (full complated uzpost backend)


class CustomUserThrottle(UserRateThrottle):
    rate = '30/minute'


<<<<<<< HEAD
class ResultExelView(APIView):
    def get(self, request):
        data = ImportPostalOffice()
        return Response(data=data, status=status.HTTP_200_OK)


=======
>>>>>>> 2d32d04 (full complated uzpost backend)
class IsCustomUsersPost(BasePermission):
    def has_permission(self, request, view):
        if request.method in ('GET', 'POST', 'OPTIONS'):
            return True
        return False

    def post(self, request):
        values = {
            "username": "+998505850551",
            "password": "Uzpost@9933",
            "remember_me": True
          }

        headers = {
            'Content-Type': 'application/json',
            'Accept': 'application/json'
        }
        # JSON formatida yuborish
        response = requests.post('https://prodapi.pochta.uz/api/v1/customer/authenticate', json=values, headers=headers)

        # Agar ma'lumotlar noto'g'ri bo'lsa, ma'lumotlar va statusni qaytarish
        # Agar hamma narsa to'g'ri bo'lsa
        data = response.json()
        if response.status_code != 200:
            return Response(data, status=response.status_code)
        return Response(data=data, status=status.HTTP_201_CREATED)


from pprint import pprint as p
import time
# Global token va muddati saqlanadigan o'zgaruvchilar


cached_token = None
token_expiry = 0


def gettoken():
    global cached_token, token_expiry
    # Token amal qilish muddati tugaganini tekshirish
    if cached_token and time.time() < token_expiry:
        return cached_token

    # Token olish uchun so'rov
    values = {
<<<<<<< HEAD
        "username": "+998505850551",
        "password": "Uzpost@9933",
=======
        "username": os.getenv('USERNAME'),
        "password": os.getenv('PASSWORD'),
>>>>>>> 2d32d04 (full complated uzpost backend)
        "remember_me": True
    }
    headers = {
        'Content-Type': 'application/json',
        'Accept': 'application/json'
    }
    response = requests.post('https://prodapi.pochta.uz/api/v1/customer/authenticate', json=values, headers=headers)

    data = response.json()
    if response.status_code != 200:
        return data["status"]

    # Yangi tokenni saqlash
    cached_token = data["data"]["id_token"]

    # Tokenning amal qilish muddati (odatda JWT tokenida "exp" maydoni bo'ladi)
    # Tokenning amal qilish vaqtini (24 soat yoki 86400 soniya) qo'shamiz
    token_expiry = time.time() + 86400

    return cached_token


class OrderServicesView(APIView):
    permission_classes = [IsCustomUsersPost, ]
    throttle_classes = [CustomUserThrottle, ]
    def get(self, request):
        headers = {
            'Content-Type': 'application/json',
            'Accept': 'application/json',
            'Authorization': f'Bearer {gettoken()}'
        }
        data = {}
        request_1 = requests.get('https://prodapi.pochta.uz/api/v1/service_types', headers=headers)
        data_1 = request_1.json()
        if data_1["status"] == "success":
            data["service_types"] = data_1
        return Response(data=data, status=status.HTTP_200_OK)


class VIloyatuzbView(APIView):
    permission_classes = [IsCustomUsersPost, ]
    throttle_classes = [CustomUserThrottle, ]
    def get(self, request):
        data = {
            "Buxoro": "259",
            "Navoiy": "263",
            "Xorazm": "271",
            "Qoraqalpog'iston Respublikasi": "265",
            "Samarqand": "266",
            "Jizzax": "261",
            "Sirdaryo": "267",
            "Toshkent shahar": "270",
            "Toshkent viloyati": "269",
            "Andijon": "258",
            "Farg'ona": "260",
            "Namangan": "262",
            "Qashqadaryo": "264",
            "Surxondaryo": "268",
        }
        return Response(data=data, status=status.HTTP_200_OK)


class VIloyatkrlView(APIView):
    permission_classes = [IsCustomUsersPost]
    throttle_classes = [CustomUserThrottle, ]
    def get(self, request):
        data_k = {
            "Бухоро": "259",
            "Навоий": "263",
            "Хоразм": "271",
            "Қорақалпоғистон Республикаси": "265",
            "Самарқанд": "266",
            "Жиззах": "261",
            "Сирдарё": "267",
            "Тошкент шаҳар": "270",
            "Тошкент вилояти": "269",
            "Андижон": "258",
            "Фарғона": "260",
            "Наманган": "262",
            "Қашқадарё": "264",
            "Сурхондарё": "268",
        }
        return Response(data=data_k, status=status.HTTP_200_OK)


from transliterate import translit

# Lotin alifbosidagi qidiruvni kirillga o'tkazish funksiyasi
def to_cyrillic(text):
    try:
        return translit(text, 'ru')
    except:
        return text


class LocationsKrelUZbView(APIView):
    permission_classes = [IsCustomUsersPost, ]
    throttle_classes = [CustomUserThrottle, ]

    def get(self, request):
        headers = {
            'Content-Type': 'application/json',
            'Accept': 'application/json',
            'Authorization': f'Bearer {gettoken()}'
        }
        parent_id = request.query_params.get('ParentId')
        if parent_id is None:
            return Response(data="Invalid ParentId", status=status.HTTP_400_BAD_REQUEST)

        try:
            parent_id = int(parent_id)
        except ValueError:
            return Response(data="Invalid ParentId: Must be an integer", status=status.HTTP_400_BAD_REQUEST)

        data = {}
        request = requests.get('https://prodapi.pochta.uz/api/v2/jurisdiction/choose/list', headers=headers)
        data_2 = request.json()
        base = []
        if data_2["status"] == "success":
            for location in data_2["data"]:
                if location["parent_id"] == parent_id:
                    location["name"] = to_cyrillic(location["name"])
                    base.append(location)
        data_2["data"] = base
        data["locations"] = data_2
        return Response(data=data_2, status=status.HTTP_200_OK)


class LocationsUZbUZbView(APIView):
    permission_classes = [IsCustomUsersPost, ]
    throttle_classes = [CustomUserThrottle, ]

    def get(self, request):
        headers = {
            'Content-Type': 'application/json',
            'Accept': 'application/json',
            'Authorization': f'Bearer {gettoken()}'
        }
        parent_id = request.query_params.get('ParentId')
        if parent_id is None:
            return Response(data="Invalid ParentId", status=status.HTTP_400_BAD_REQUEST)

        try:
            parent_id = int(parent_id)
        except ValueError:
            return Response(data="Invalid ParentId: Must be an integer", status=status.HTTP_400_BAD_REQUEST)

        data = {}
        request = requests.get('https://prodapi.pochta.uz/api/v2/jurisdiction/choose/list', headers=headers)
        data_2 = request.json()
        base = []
        if data_2["status"] == "success":
            for location in data_2["data"]:
                if location["parent_id"] == int(parent_id):
                    base.append(location)
        data_2["data"] = base
        data["locations"] = data_2
        return Response(data=data_2, status=status.HTTP_200_OK)


class LocationsAllView(APIView):
    permission_classes = [IsCustomUsersPost]
    throttle_classes = [CustomUserThrottle, ]

    def get(self, request):
        headers = {
            'Content-Type': 'application/json',
            'Accept': 'application/json',
            'Authorization': f'Bearer {gettoken()}'
        }
        data = {}
        request = requests.get('https://prodapi.pochta.uz/api/v2/jurisdiction/choose/list', headers=headers)
        data_2 = request.json()
        base = []
        if data_2["status"] == "success":
            for location in data_2["data"]:
                if len(location["hierarchy"]) == 0:
                    base.append(location)
        data_2["data"] = base
        return Response(data=data_2, status=status.HTTP_200_OK)


class LocationsKrelAllView(APIView):
    permission_classes = [IsCustomUsersPost]
    throttle_classes = [CustomUserThrottle, ]
    def get(self, request):
        headers = {
            'Content-Type': 'application/json',
            'Accept': 'application/json',
            'Authorization': f'Bearer {gettoken()}'
        }
        data = {}
        request = requests.get('https://prodapi.pochta.uz/api/v2/jurisdiction/choose/list', headers=headers)
        data_2 = request.json()
        base = []
        if data_2["status"] == "success":
            for location in data_2["data"]:
                if len(location["hierarchy"]) == 0:
                    location["name"] = to_cyrillic(location["name"])
                    base.append(location)
        data_2["data"] = base
        return Response(data=data_2, status=status.HTTP_200_OK)


class CalculatorShipoxView(APIView):
    permission_classes = [IsCustomUsersPost, ]
    throttle_classes = [CustomUserThrottle, ]

    def get(self, request):
        headers = {
            'Content-Type': 'application/json',
            'Accept': 'application/json',
            'Authorization': f'Bearer {gettoken()}'
        }
        data = {}
        weight = request.query_params.get("Weight")
        if weight is None:
            return Response(data="invalid Weight", status=status.HTTP_400_BAD_REQUEST)
        try:
            weight = float(weight)
        except ValueError:
<<<<<<< HEAD
            return Response(data="Invalid weight: Must be an integer", status=status.HTTP_400_BAD_REQUEST)
=======
            return Response(data="Invalid weight: Must be an float", status=status.HTTP_400_BAD_REQUEST)
>>>>>>> 2d32d04 (full complated uzpost backend)
        service_type_id = request.query_params.get("ServiceTypeId")
        if service_type_id is None:
            return Response(data="ServiceTypeId should be int", status=status.HTTP_400_BAD_REQUEST)
        try:
            service_type_id = int(service_type_id)
        except ValueError:
            return Response(data="Invalid ServiceTypeId: Must be an integer", status=status.HTTP_400_BAD_REQUEST)

<<<<<<< HEAD
        fromjurisdiction_id = request.query_params.get("FromJrisdictionId")
        if fromjurisdiction_id is None:
            return Response(data="FromJrisdictionId should be int", status=status.HTTP_400_BAD_REQUEST)
=======
        fromjurisdiction_id = request.query_params.get("FromJurisdictionId")
        if fromjurisdiction_id is None:
            return Response(data="Invalid FromJrisdictionId", status=status.HTTP_400_BAD_REQUEST)
>>>>>>> 2d32d04 (full complated uzpost backend)
        try:
            fromjurisdiction_id = int(fromjurisdiction_id)
        except ValueError:
            return Response(data="Invalid FromJrisdictionId: Must be an integer", status=status.HTTP_400_BAD_REQUEST)

<<<<<<< HEAD
        tojurisdiction_id = request.query_params.get("ToJrisdictionId")

        if tojurisdiction_id is None:
            return Response(data="ToJrisdictionId should be int")
        try:
            tojurisdiction_id = int(tojurisdiction_id)
        except ValueError:
            return Response(data="Invalid ToJrisdictionId: Must be an integer", status=status.HTTP_400_BAD_REQUEST)
=======
        tojurisdiction_id = request.query_params.get("ToJurisdictionId")

        if tojurisdiction_id is None:
            return Response(data="Invalid ToJurisdictionId")
        try:
            tojurisdiction_id = int(tojurisdiction_id)
        except ValueError:
            return Response(data="Invalid ToJurisdictionId: Must be an integer", status=status.HTTP_400_BAD_REQUEST)
>>>>>>> 2d32d04 (full complated uzpost backend)

        request = requests.get('https://prodapi.pochta.uz/api/v2/jurisdiction/choose/list', headers=headers)
        data_2 = request.json()
        from_latitude = ""
        from_longitude = ""
        to_latitude = ""
        to_longitude = ""
        fromJurisdictionId = None
        toJurisdictionId = None

        for i in data_2["data"]:
            if i["id"] == fromjurisdiction_id:
                fromJurisdictionId = fromjurisdiction_id
                from_latitude = i["lat"]
                from_longitude = i["lng"]
            if i["id"] == tojurisdiction_id:
                toJurisdictionId = tojurisdiction_id
                to_latitude = i["lat"]
                to_longitude = i["lng"]
        request = requests.get(f'https://prodapi.pochta.uz/api/v2/customer/packages/prices/starting_from?dimensions.weight={weight}&service_type={service_type_id}&page=0&size=20&fromJurisdictionId='
                               f'{fromJurisdictionId}&toJurisdictionId={toJurisdictionId}&from_latitude={from_latitude}&from_longitude={from_longitude}&to_latitude={to_latitude}&to_longitude={to_longitude}', headers=headers)
<<<<<<< HEAD
        request_x = requests.get(f"https://prodapi.pochta.uz/api/v2/customer/packages/prices/starting_from?dimensions.weight={weight}&service_type={service_type_id}&fromJurisdictionId={fromJurisdictionId}&toJurisdictionId={toJurisdictionId}", headers=headers)
        data = request.json()
        data_x = request_x.json()
=======
        data = request.json()
        if data["status"] != "success":
            return Response([data], status=status.HTTP_400_BAD_REQUEST)
>>>>>>> 2d32d04 (full complated uzpost backend)
        x = [data]
        return Response(data=x, status=status.HTTP_200_OK)


#@method_decorator(cache_page(60*1), name='dispatch')
class CalculatorShipoxIndexView(APIView):
    permission_classes = [IsCustomUsersPost, ]
    throttle_classes = [CustomUserThrottle, ]

    def get(self, request):
        headers = {
            'Content-Type': 'application/json',
            'Accept': 'application/json',
            'Authorization': f'Bearer {gettoken()}'
        }

        data = {}
<<<<<<< HEAD
        weight = request.query_params.get("weight")
        if weight is None:
            return Response(data="Invalid weight: Missing parameter", status=status.HTTP_400_BAD_REQUEST)
        try:
            weight = float(weight)
        except ValueError:
            return Response(data="Invalid weight: Must be a float", status=status.HTTP_400_BAD_REQUEST)

        # service_type_id ni tekshirish
        service_type_id = request.query_params.get("service_type_id")
        if service_type_id is None:
            return Response(data="Invalid service_type_id: Missing parameter", status=status.HTTP_400_BAD_REQUEST)
        try:
            service_type_id = int(service_type_id)
        except ValueError:
            return Response(data="Invalid service_type_id: Must be an integer", status=status.HTTP_400_BAD_REQUEST)

        # fromjurisdiction_id ni tekshirish
        fromjurisdiction_id = request.query_params.get("fromjurisdiction_id")
        if fromjurisdiction_id is None:
            return Response(data="Invalid fromjurisdiction_id: Missing parameter",
=======
        weight = request.query_params.get("Weight")
        if weight is None:
            return Response(data="Invalid Weight: Missing parameter", status=status.HTTP_400_BAD_REQUEST)
        try:
            weight = float(weight)
        except ValueError:
            return Response(data="Invalid Weight: Must be a float", status=status.HTTP_400_BAD_REQUEST)

        # service_type_id ni tekshirish
        service_type_id = request.query_params.get("ServiceTypeId")
        if service_type_id is None:
            return Response(data="Invalid ServiceTypeId: Missing parameter", status=status.HTTP_400_BAD_REQUEST)
        try:
            service_type_id = int(service_type_id)
        except ValueError:
            return Response(data="Invalid ServiceTypeId: Must be an integer", status=status.HTTP_400_BAD_REQUEST)

        # fromjurisdiction_id ni tekshirish
        fromjurisdiction_id = request.query_params.get("FromJurisdictionId")
        if fromjurisdiction_id is None:
            return Response(data="Invalid FromJurisdictionId: Missing parameter",
>>>>>>> 2d32d04 (full complated uzpost backend)
                            status=status.HTTP_400_BAD_REQUEST)
        try:
            fromjurisdiction_id = int(fromjurisdiction_id)
        except ValueError:
<<<<<<< HEAD
            return Response(data="Invalid fromjurisdiction_id: Must be an integer",
                            status=status.HTTP_400_BAD_REQUEST)

        # index ni tekshirish
        index = request.query_params.get("index")
        if index is None:
            return Response(data="Invalid index: Missing parameter", status=status.HTTP_400_BAD_REQUEST)
=======
            return Response(data="Invalid FromJurisdictionId: Must be an integer",
                            status=status.HTTP_400_BAD_REQUEST)

        # index ni tekshirish
        index = request.query_params.get("Index")
        if index is None:
            return Response(data="Invalid Index: Missing parameter", status=status.HTTP_400_BAD_REQUEST)
>>>>>>> 2d32d04 (full complated uzpost backend)

        # Omborxona ma'lumotini olish
        warehouse = Warehouse.objects.filter(index=str(index)).first()
        if warehouse is None:
            return Response(data="Information not found for the provided index", status=status.HTTP_404_NOT_FOUND)

        request = requests.get('https://prodapi.pochta.uz/api/v2/jurisdiction/choose/list', headers=headers)
        data_2 = request.json()
        from_latitude = ""
        from_longitude = ""
        to_latitude = warehouse.warehouse_lat
        to_longitude = warehouse.warehouse_lon
        fromJurisdictionId = None
        toJurisdictionId = warehouse.city_id

        for i in data_2["data"]:
            if i["id"] == fromjurisdiction_id:
                fromJurisdictionId = fromjurisdiction_id
                from_latitude = i["lat"]
                from_longitude = i["lng"]
        request = requests.get(f'https://prodapi.pochta.uz/api/v2/customer/packages/prices/starting_from?dimensions.weight={weight}&service_type={service_type_id}&page=0&size=20&fromJurisdictionId='
                               f'{fromJurisdictionId}&toJurisdictionId={toJurisdictionId}&from_latitude={from_latitude}&from_longitude={from_longitude}&to_latitude={to_latitude}&to_longitude={to_longitude}', headers=headers)
<<<<<<< HEAD
        request_x = requests.get(f"https://prodapi.pochta.uz/api/v2/customer/packages/prices/starting_from?dimensions.weight={weight}&service_type={service_type_id}&fromJurisdictionId={fromJurisdictionId}&toJurisdictionId={toJurisdictionId}", headers=headers)
        data = request.json()
        data_x = request_x.json()
=======
        data = request.json()
        if data["status"] != "success":
            return Response([data], status=status.HTTP_400_BAD_REQUEST)
>>>>>>> 2d32d04 (full complated uzpost backend)
        x = [data]
        return Response(data=x, status=status.HTTP_200_OK)




# class Postindexfilter(filters.FilterSet):
#     warehouse_name = filters.CharFilter(field_name='warehouse_name', lookup_expr='icontains')
#     class Meta:
#         model = Warehouse
#         fields = ["warehouse_name"]


<<<<<<< HEAD
class PostIndexesView(APIView):
    permission_classes = [IsCustomUsersPost]
    throttle_classes = [CustomUserThrottle, ]
    def get(self, request):
        query = request.query_params.get('name')
        if query is None:
            return Response(data="name is not correct", status=status.HTTP_400_BAD_REQUEST)
        try:
            query = int(query)
        except ValueError:
            return Response(data="Invalid name: Must be an int", status=status.HTTP_400_BAD_REQUEST)
        query_x = to_cyrillic(query)
        data = Warehouse.objects.filter(warehouse_name__icontains=query_x)
        serializer = WarehouseSerializer(data, many=True)
        return Response(data=serializer.data, status=status.HTTP_200_OK)
=======
from django.db.models import Q


class PostIndexesView(APIView):
    permission_classes = [IsCustomUsersPost]
    throttle_classes = [CustomUserThrottle]

    def get(self, request):
        allow_params = ["warehouse_name", "city_name", "city_code", "region_name", "index"]
        filters = Q()

        # Dinamik filtrlash
        for param in allow_params:
            value = request.query_params.get(param)
            if value:
                if param != "city_code":
                    value = to_cyrillic(value)
                filters |= Q(**{f"{param}__icontains": value})

        if filters:
            # Filtrlangan natijalar
            data_x = Warehouse.objects.filter(filters)
            serializer = WarehouseSerializer(data_x, many=True)
            return Response(data=serializer.data, status=status.HTTP_200_OK)

        # Agar hech narsa topilmasa bo'sh ro'yxat qaytariladi
        return Response(data=[], status=status.HTTP_200_OK)
>>>>>>> 2d32d04 (full complated uzpost backend)


class PostIndexesAllView(APIView):
    permission_classes = []
    throttle_classes = [CustomUserThrottle, ]
    def get(self, request):
        data = Warehouse.objects.all()

        # NaN qiymatlarni tekshirish va almashtirish
        for obj in data:
            if obj.warehouse_lat != obj.warehouse_lat:  # NaN ni aniqlash
                obj.warehouse_lat = 0.0  # 0.0 bilan almashtirish
            if obj.warehouse_lon != obj.warehouse_lon:
                obj.warehouse_lon = 0.0

        serializer = WarehouseSerializer(data, many=True)
        return Response(data=serializer.data, status=status.HTTP_200_OK)





<<<<<<< HEAD













# from rest_framework.views import APIView
# from rest_framework.response import Response
# from rest_framework import status
# from .models import Warehouse
# import pandas as pd
# from rest_framework.parsers import MultiPartParser, FormParser
#
#
# class WarehouseImportView(APIView):
#     # Faylni olish uchun parser
#     parser_classes = (MultiPartParser, FormParser)
#
#     def post(self, request, *args, **kwargs):
#         # Faylni requestdan olish
#         file = request.FILES.get('file')
#
#         if not file:
#             return Response({"error": "Fayl kiritilmagan!"}, status=status.HTTP_400_BAD_REQUEST)
#
#         # Excel faylini o'qing
#         try:
#             data = pd.read_excel(file)
#         except Exception as e:
#             return Response({"error": f"Faylni o'qishda xato: {str(e)}"}, status=status.HTTP_400_BAD_REQUEST)
#
#         # Har bir qatordagi ma'lumotlarni saqlash
#         for _, row in data.iterrows():
#             Warehouse.objects.create(
#                 warehouse_id=row['warehouse_id'],
#                 warehouse_name=row['warehouse_name'],
#                 warehouse_lat=row['warehouse_lat'],
#                 warehouse_lon=row['warehouse_lon'],
#                 city_id=row['city_id'],
#                 city_name=row['city_name'],
#                 city_code=row['city_code'],
#                 region_name=row['region_name'],
#                 index=row['Index']
#             )
#
#         return Response({"message": "Ma'lumotlar muvaffaqiyatli saqlandi!"}, status=status.HTTP_201_CREATED)
#
#
#






=======
>>>>>>> 2d32d04 (full complated uzpost backend)
