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
from db_models.models import (Banners, MenuElements, Menu, StatisticItems, Statistics, TegRegions, TegWorkingDays,
                              TegExperience, TegVacancies, TegBranches2, Vacancies, Purchases, Marks, SaveMediaFiles,
                              Events, UzPostNews, PostalServices, Pages, BranchServices, ShablonServices, Branches,
                              VacanciesImages, InternalDocuments, ThemaQuestions, BusinessPlansCompleted, AnnualReports,
                              Dividends, QuarterReports, UserInstructions, ExecutiveApparatus, ShablonUzPostTelNumber,
                              ShablonContactSpecialTitle, Contact, Advertisements, OrganicManagements, Partners,
                              RegionalBranches, Advertising, InformationAboutIssuer, Slides, SocialMedia, EssentialFacts,
                              Rates, Services, CharterSociety, SecurityPapers, FAQ, SiteSettings, CategoryPages, ControlCategoryPages, CategoryServices,
                              CategoryFaq)

from rest_api.serializes import (UsersRequestsSerializer, BannersSerializer, MenuElementsSerializer,
                        MenuSerializer, StatisticItemsSerializer, StatisticsSerializer, TegRegionsSerializer,
                        TegWorkingDaysSerializer, TegExperiencesSerializer, TegVacanciesSerializer, TegBranches2Serializer,
                        VacanciesSerializer, PurchasesSerializer, MarksSerializer, SaveMediaFilesSerializer, EventsSerializer,
                         UzPostNewsSerializer, PostalServicesSerializer, PagesSerializer, BranchServicesSerializer,
                         ShablonServicesSerializer, BranchesSerializer, VacanciesImagesSerializer, InternalDocumentsSerializer,
                         ThemaQuestionsSerializer, BusinessPlansCompletedSerializer, AnnualReportsSerializer, DividendsSerializer,
                         QuarterReportsSerializer, UserInstructionsSerializer, ExecutiveApparatusSerializer, ShablonUzPostTelNumberSerializer, ShablonContactSpecialTitleSerializer,
                         ContactSerializer, AdvertisementsSerializer, OrganicManagementsSerializer, PartnersSerializer, RegionalBranchesSerializer,
                         AdvertisingSerializer, InformationAboutIssuerSerializer, SlidesSerializer, SocialMediaSerializer, EssentialFactsSerializer,
                         RatesSerializer, ServicesSerializer, CharterSocietySerializer, SecurityPapersSerializer, FAQSerializer,
                         SiteSettingsSerializer, CategoryPagesSerializer, ControlCategoryPagesSerializer, CategoryServicesSerializer, CategoryFAQSerializer)
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
<<<<<<< HEAD
=======
from requests.auth import HTTPBasicAuth
from random import randint
import uuid
from django.utils import timezone
from datetime import datetime
from datetime import timedelta
from calculator.models import OrderCart
from dotenv import load_dotenv
import os
from django.db.models import Q
from .send_sms import send_sms

load_dotenv()
>>>>>>> 2d32d04 (full complated uzpost backend)


class CustomPagination(PageNumberPagination):
    page_size = 15  # Har bir sahifada 10 ta obyekt chiqadi
    page_size_query_param = 'page_size'  # Foydalanuvchi URL'da 'page_size' ni o'zgartira oladi
    max_page_size = 20  # Foydalanuvchi sahifa hajmini 100 dan oshira olmaydi

    def get_paginated_response(self, data):
        total_pages = (self.page.paginator.count + self.page_size - 1) // self.page_size
        return Response({
            'total_pages': total_pages,  # Sahifalar soni
            "next": self.get_next_link(),
            "previous": self.get_previous_link(),
            'results': data
        })


class CustomTokenObtainPairView(TokenObtainPairView):
    serializer_class = CustomTokenObtainPairSerializer


class CustomUserThrottle(UserRateThrottle):
    rate = '30/minute'


class CustomUserUnauthorizedThrottle(UserRateThrottle):
    rate = '15/minute'


class RegisterUnauthorizedThrottle(UserRateThrottle):
    rate = '5/minute'


class IsCustomUsersGet(BasePermission):
    def has_permission(self, request, view):
        if request.method in ('GET', 'OPTIONS'):
            return True
        return False


class TwoFACTauthPermissions(BasePermission):
    def has_permission(self, request, view):
        token = request.headers.get("X-API-Token")
        if not token:
            return False
        if token == "abdullo":
            return True
        return False


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
        "username": "uzpost",
        "password": "q%0-E5~3T#i&",
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


class RegisterUserView(APIView):
    permission_classes = [AllowAny, ]
    throttle_classes = [RegisterUnauthorizedThrottle, ]
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
        if custom_user:
            return Response('custom user with this phone number already exists.', status=status.HTTP_400_BAD_REQUEST)
        last_sms = CheckSMS.objects.filter(phone_number=database_number).order_by('-created_at').first()
        if last_sms:
            time_diff = timezone.now() - last_sms.created_at
            if time_diff < timedelta(minutes=1):
                remaining_time = timedelta(minutes=1) - time_diff
                return Response(f'Please try again after {remaining_time} minutes.', status=status.HTTP_400_BAD_REQUEST)

        sms_code = randint(1000, 9999)
        massage_id = str(uuid.uuid4())
        # post_sms = {
        # "messages":
        # [
        # {
        #     "recipient": f"998{phone_number}",
        #     "message-id": f"{massage_id}",
        #
        # "sms":{
        #     "originator": "3700",
        #     "content": {
        #         "text": f"UzPost veb saytiga kirish uchun kod: {sms_code}. Kodni hech kimga bermang! Tel: 1165"
        #             }
        # }
        # }
        # ]
        # }
        post_sms = {
                "messages": [
                    {
                        "recipient": f"998{phone_number}",
                        "message-id": f"{massage_id}",
                        "sms": {
                            "originator": "3700",
                            "content": {
                                "text": f"UzPost veb saytiga kirish uchun kod: {sms_code}. Kodni hech kimga bermang! Tel: 1165"
                            }
                        }
                    }
                ]
            }
        results = requests.post("https://smssend.avval.uz/SMSSend/send_sms_v2.php", json=post_sms, headers={'content-type': 'application/json'}, auth=HTTPBasicAuth(username="postuz_user_sms", password="3Ddwr1324fqeq@sdcswr#4wc"))

        if results.status_code == 200:
            CheckSMS.objects.create(
                massage_id=massage_id,
                code=sms_code,
                phone_number=database_number)
            return Response(data=results.json(), status=status.HTTP_200_OK)
        return Response(data='Something went wrong', status=status.HTTP_400_BAD_REQUEST)


class RegisterUser2View(APIView):
    permission_classes = [AllowAny, ]
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
        if custom_user:
            return Response('custom user with this phone number already exists.', status=status.HTTP_400_BAD_REQUEST)
        code = request.data.get('code')
        if not code:
            return Response(data="No code provided", status=status.HTTP_400_BAD_REQUEST)
        check_code = CheckSMS.objects.filter(phone_number=database_number).order_by("-created_at").first()
        if not check_code:
            return Response(data="Code does not exist", status=status.HTTP_400_BAD_REQUEST)
        if code != check_code.code:
            return Response(data="Code does not match", status=status.HTTP_400_BAD_REQUEST)
        check_code.status = True
        check_code.save()
        return Response(data={"status": "success"}, status=status.HTTP_200_OK)


class RegisterUser3View(APIView):
    permission_classes = [AllowAny, ]
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
        if custom_user:
            return Response('custom user with this phone number already exists.', status=status.HTTP_400_BAD_REQUEST)
        check_code = CheckSMS.objects.filter(phone_number=database_number).order_by("-created_at").first()
        if not check_code:
            return Response(data="Code does not exist", status=status.HTTP_400_BAD_REQUEST)
        if check_code.status != True:
            return Response(data="phone number code not verified", status=status.HTTP_400_BAD_REQUEST)
        first_name = request.data.get('first_name')
        last_name = request.data.get('last_name')
        image = request.data.get('image')
        region = request.data.get('region')
        district = request.data.get('district')
        index = request.data.get('index')
        if not first_name:
            first_name = None
        if not last_name:
            last_name = None
        if not image:
            image = None
        if not region:
            region = None
        if not district:
            district = None
        if not index:
            index = None

        password = request.data.get('password')
        if not password:
            return Response(data="Password must be entered", status=status.HTTP_400_BAD_REQUEST)
        if type(password) != str:
            return Response(data="password is type invalid it is type str", status=status.HTTP_400_BAD_REQUEST)
        if len(password) < 6:
            return Response('password must be longer than 6 characters', status=status.HTTP_400_BAD_REQUEST)

        custom_user = CustomUser.objects.create(
            phone_number=database_number,
            first_name=first_name,
            last_name=last_name,
            image=image,
            region=region,
            district=district,
            post_index=index,
            password=make_password(password)  # Parolni hashlash

        )
        refresh = RefreshToken.for_user(custom_user)
        id_token = str(refresh.access_token)
        data = {
            "phone_number": database_number,
            'first_name': first_name,
            'last_name': last_name,
            'region': region,
            'district': district,
            "index": index,
            'password': "********",
            "image": None,
            "status": "successful",
            "id_token": id_token
        }
        check_code.delete()
        all_sms = CheckSMS.objects.filter(phone_number=database_number)
        all_sms.delete()
        return Response(data=data, status=status.HTTP_201_CREATED)


class MyProfileView(APIView):
    permission_classes = [IsAuthenticated, ]
    throttle_classes = [CustomUserThrottle, ]

    def get(self, request):
        user = CustomUser.objects.filter(phone_number=request.user.phone_number).first()
        user_orders = OrderCart.objects.filter(user=user, archiving_status=True).order_by('-created_at')
        for order in user_orders:
            check_time = timezone.now() - order.created_at
            if check_time > timedelta(days=15):
                order.archiving_status = False
                order.save()
        if not user:
            return Response({"error": "User not found."}, status=status.HTTP_404_NOT_FOUND)

        allow_params_1 = [
            "barcode", "fromjurisdiction", "tojurisdiction", "from_phone_number", "full_name",
            "from_country_code", "to_country_code", "payment_type", "shipment_type"
        ]
        filters = Q(user=user) & Q(archiving_status=True)
        filters_archives = Q(user=user) & Q(archiving_status=False)
        # Dinamik filtrlarni qo'llash
        for param in allow_params_1:
            value = request.query_params.get(param)
            if value:  # Faqat qiymat mavjud bo'lsa filtr qo'llanadi
                filters &= Q(**{f"{param}__icontains": value})
                filters_archives &= Q(**{f"{param}__icontains": value})

        # Vaqt oralig'i validatsiyasi
        from_date = request.query_params.get("from_created_at")
        to_date = request.query_params.get("to_created_at")
        try:
            if from_date:
                from_date = datetime.strptime(from_date, "%Y-%m-%d")
                filters &= Q(created_at__gte=from_date)
                filters_archives &= Q(created_at__gte=from_date)
            if to_date:
                to_date = datetime.strptime(to_date, "%Y-%m-%d")
                filters &= Q(created_at__lte=to_date)
                filters_archives &= Q(created_at__lte=to_date)
        except ValueError:
            return Response({
                "error": "Invalid date format. Use YYYY-MM-DD format for 'from_created_at' and 'to_created_at'."
            }, status=status.HTTP_400_BAD_REQUEST)

        orders = OrderCart.objects.filter(filters)
        archives_orders = OrderCart.objects.filter(filters_archives)

        # Natijalarni shakllantirish
        orders_data = [
            {
                "weight": order.weight,
                "barcode": order.barcode,
                "from_jurisdiction": order.fromjurisdiction,
                "to_jurisdiction": order.tojurisdiction,
                "from_phone_number": order.from_phone_number,
                "to_phone_number": order.to_phone_number,
                "full_name": order.full_name,
                "from_country_code": order.from_country_code,
                "to_country_code": order.to_country_code,
                "price": order.price,
                "price_code": order.price_code,
                "payment_type": order.payment_type,
                "shipment_type": order.shipment_type,
                "shipox_created_at": order.shipox_created_at,
                "shipox_last_status_date": order.shipox_last_status_date,
                "order_status": order.order_status,
                "created_at": order.created_at.strftime('%Y-%m-%d %H:%M:%S'),
            }
            for order in orders
        ]
        archive_orders_data = [
            {
                "weight": archives_order.weight,
                "barcode": archives_order.barcode,
                "from_jurisdiction": archives_order.fromjurisdiction,
                "to_jurisdiction": archives_order.tojurisdiction,
                "from_phone_number": archives_order.from_phone_number,
                "to_phone_number": archives_order.to_phone_number,
                "full_name": archives_order.full_name,
                "from_country_code": archives_order.from_country_code,
                "to_country_code": archives_order.to_country_code,
                "price": archives_order.price,
                "price_code": archives_order.price_code,
                "payment_type": archives_order.payment_type,
                "shipment_type": archives_order.shipment_type,
                "shipox_created_at": archives_order.shipox_created_at,
                "shipox_last_status_date": archives_order.shipox_last_status_date,
                "order_status": archives_order.order_status,
                "created_at": archives_order.created_at.strftime('%Y-%m-%d %H:%M:%S'),
            }
            for archives_order in archives_orders
        ]

        profile_data = {
            "phone_number": user.phone_number,
            "first_name": user.first_name,
            "last_name": user.last_name,
            "image": user.image.url if user.image else None,
            "region": user.region,
            "district": user.district,
            "index": user.post_index,
            "password": "********",
            "orders": orders_data,
            "archive_orders": archive_orders_data
        }

        return Response(profile_data, status=status.HTTP_200_OK)

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
        if custom_user == request.user:
            return Response('this phone number your old number', status=status.HTTP_400_BAD_REQUEST)
        if custom_user:
            return Response("this phone number is already registered", status=status.HTTP_400_BAD_REQUEST)
        check_code = CheckSMS.objects.filter(phone_number=database_number).order_by("-created_at").first()
        if not check_code:
            send_sms_code = send_sms(phone_number)
            return Response(data=send_sms_code, status=status.HTTP_400_BAD_REQUEST)
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
        custom_user = CustomUser.objects.filter(phone_number=request.user.phone_number).first()
        custom_user.phone_number = database_number
        custom_user.save()
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
        }
        check_code.delete()
        return Response(data=data, status=status.HTTP_200_OK)

    def put(self, request):
        user = CustomUser.objects.filter(phone_number=request.user.phone_number).first()
        if not user:
            return Response("User not found", status=status.HTTP_404_NOT_FOUND)

        data = request.data
        first_name = data.get('first_name')
        last_name = data.get('last_name')
        image = request.FILES.get('image')
        remove_image = data.get('remove_image')  # Rasmni o'chirish uchun bayroq
        index = data.get("index")
        region = data.get('region')
        district = data.get('district')
        password = data.get('password')

        if not password:
            return Response("Password must be entered", status=status.HTTP_400_BAD_REQUEST)
        if len(password) < 6:
            return Response('Password must be longer than 6 characters', status=status.HTTP_400_BAD_REQUEST)

        user.first_name = first_name if first_name else user.first_name
        user.last_name = last_name if last_name else user.last_name
        if image:
            if user.image:
                user.image.delete()
            user.image = image  # Agar yangi rasm berilgan bo'lsa, yangilash
        elif remove_image:
            user.image.delete()  # Rasmni o'chirish
            user.image = None
        user.region = region if region else user.region
        user.district = district if district else user.district
        user.index = index if index else user.index
        user.password = make_password(password)
        user.save()

        data = {
            "phone_number": user.phone_number,
            'first_name': user.first_name,
            'last_name': user.last_name,
            'image': user.image.url if user.image else None,  # URL yoki None
            'region': user.region,
            'district': user.district,
            "index": user.post_index,
            'password': "********"
        }
        return Response(data, status=status.HTTP_200_OK)

    def delete(self, request):
        user = CustomUser.objects.filter(phone_number=request.user.phone_number).first()
        user.is_active = False
        user.save()
        return Response(data='successful deleted', status=status.HTTP_204_NO_CONTENT)


@method_decorator(cache_page(60*15), name='dispatch')
class Barcode(APIView):
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


        data = requests.get(f"https://prodapi.pochta.uz/api/v1/public/order/{barcode}")
        data = data.json()
        if data['status'] != "success":
            return Response(data=data, status=status.HTTP_404_NOT_FOUND)
        total_data_2 = {'header': data}
        if barcode[:2] != 'SX' and data["data"]['locations'][0]['country']['code'] == 'UZ' and data["data"]['locations'][1]['country']['code'] == 'UZ':
            total_data = requests.get(f"https://prodapi.pochta.uz/api/v1/public/order/{barcode}/history_items")
            total_data_2['shipox'] = total_data.json()
            total_data_2['gdeposilka'] = None
            return Response(total_data_2, status=status.HTTP_200_OK)

        url1 = f"https://gdeposylka.ru/api/v4/tracker/detect/{barcode}"
        headers = {
            "X-Authorization-Token": "65bbbac85f796f8032e0874411f4d1f5af7185a99e184709bf0c1f38d95486fa2338733760a48704"
        }
        response1 = requests.get(url1, headers=headers)
        data = response1.json()
        shipox = requests.get(f"https://prodapi.pochta.uz/api/v1/public/order/{barcode}/history_items")
        total_data_2['shipox'] = shipox.json()

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


from requests.exceptions import ConnectTimeout, RequestException


class Barcode_new(APIView):
    def get(self, request, barcode):
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

        ###### shipox ips uchun
        url_header = f"https://prodapi.pochta.uz/api/v1/public/order/{barcode}"
        url_shipox = f"https://prodapi.pochta.uz/api/v1/customer/order/{barcode}/history_items"

        data_header = requests.get(url_header, headers={
            'Content-Type': 'application/json',
            'Accept': 'application/json',
            'Authorization': f'Bearer {gettoken()}'
        }, timeout=1)
        data_shipox = requests.get(url_shipox, headers={
            'Content-Type': 'application/json',
            'Accept': 'application/json',
            'Authorization': f'Bearer {gettoken()}'
        }, timeout=1)
        data_header = data_header.json()
        data_shipox = data_shipox.json()
        if data_header['status'] != 'success':
            return Response(data=data_header, status=404)
        if data_shipox['status'] != 'success':
            return Response(data=data_header, status=404)
        full_track_temu = []




        if response_data_2[0]["InfoFromEdi"] != None:
            for i in response_data_2[0]["InfoFromEdi"]["TMailitemInfoFromEDI"][0]["Events"]["TMailitemEventEDI"]:
                if i["IPSEventType"]["Name"] == "Items on way":
                    local_datetime = datetime.strptime(i['GmtDateTime'], "%Y-%m-%dT%H:%M:%S")
                    compare_date = datetime(2025, 3, 6)
                    if local_datetime <= compare_date:
                        form = {
                            "EventOffice": {
                                "Code": "UZTASA",
                                "Name": "UzPost"
                            },
                            "IPSEventType": {
                                "Code": None,
                                "Name": None,
                                "LocalName": None
                            },
                            "date": None
                        }
                        for i in response_data_2[0]["InfoFromEdi"]["TMailitemInfoFromEDI"][0]["Events"][
                            "TMailitemEventEDI"]:
                            form["IPSEventType"]["Code"] = i["IPSEventType"]["Name"]
                            form["IPSEventType"]["Code"] = i["IPSEventType"]["Code"]
                            form["IPSEventType"]["LocalName"] = i["IPSEventType"]["Localname"]
                            form["date"] = i['GmtDateTime']
                            full_track_temu.append(form)
                        if response_data_2[0]["OperationalMailitems"] != None:
                            for j in response_data_2[0]["OperationalMailitems"]["TMailitemInfoFromScanning"][0]["Events"][
                            "TMailitemEventScanning"]:
                                form_op = {
                                    "EventOffice": {
                                        "Code": "UZTASA",
                                        "Name": "UzPost"
                                    },
                                    "IPSEventType": {
                                        "Code": None,
                                        "Name": None,
                                        "LocalName": None
                                    },
                                    "date": None
                                }
                                form_op["IPSEventType"]["Code"] = j["IPSEventType"]["Name"]
                                form_op["IPSEventType"]["Code"] = j["IPSEventType"]["Code"]
                                form_op["IPSEventType"]["LocalName"] = j["IPSEventType"]["Localname"]
                                form_op["date"] = j['GmtDateTime']
                                full_track_temu.append(form_op)
                        if not any(item_x["IPSEventType"]["Name"] == "Deliver item (Inb)" for item_x in
                                   full_track_temu) or not any(item_x["IPSEventType"]["Name"] == "Deliver item (Otb)" for item_x in
                                   full_track_temu):
                            for data in data_shipox['data']["list"]:
                                if data["status"] == 'issued_to_recipient':
                                    form_f = {
                                        "EventOffice": {
                                            "Code": "UZTASA",
                                            "Name": "UzPost"
                                        },
                                        "IPSEventType": {
                                            "Code": None,
                                            "Name": None,
                                            "LocalName": None
                                        },
                                        "date": None
                                    }
                                    form_f['IPSEventType']["Name"] = "Deliver item"
                                    form_f['IPSEventType']["LocalName"] = "Deliver item"
                                    form_f['IPSEventType']["Code"] = "1257"
                                    form_f["date"] = item['date']
                                    full_track_temu.append(form_f)
                                    break
                                if data["status"] == 'completed':
                                    form_j = {
                                        "EventOffice": {
                                            "Code": "UZTASA",
                                            "Name": "UzPost"
                                        },
                                        "IPSEventType": {
                                            "Code": None,
                                            "Name": None,
                                            "LocalName": None
                                        },
                                        "date": None
                                    }
                                    form_j['IPSEventType']["Name"] = "Deliver item"
                                    form_j['IPSEventType']["LocalName"] = "Deliver item"
                                    form_j['IPSEventType']["Code"] = "1257"
                                    form_j["date"] = data['date']
                                    full_track_temu.append(form_j)
                                    break

                        full_data = {}
                        full_data['header'] = data_header
                        full_data['data'] = full_track_temu

                        return Response(data=full_data, status=200)

                    form = {
                                    "EventOffice": {
                                        "Code": "UZTASA",
                                        "Name": "UzPost"
                                    },
                                    "IPSEventType": {
                                        "Code": None,
                                        "Name": None,
                                        "LocalName": None
                                    },
                                    "date": None
                                }
                    form["IPSEventType"]["Code"] = i["IPSEventType"]["Name"]
                    form["IPSEventType"]["Code"] = i["IPSEventType"]["Code"]
                    form["IPSEventType"]["LocalName"] = i["IPSEventType"]["Localname"]
                    form["date"] = i['GmtDateTime']
                    full_track_temu.append(form)
                    break


        if response_data_2[0]["OperationalMailitems"] != None:
            for j in response_data_2[0]["OperationalMailitems"]["TMailitemInfoFromScanning"][0]["Events"]["TMailitemEventScanning"]:
                if j["IPSEventType"]["Name"] == "Items on way":
                    local_datetime = datetime.strptime(j['GmtDateTime'], "%Y-%m-%dT%H:%M:%S")
                    compare_date = datetime(2025, 3, 6)
                    if local_datetime <= compare_date:
                        form = {
                            "EventOffice": {
                                "Code": "UZTASA",
                                "Name": "UzPost"
                            },
                            "IPSEventType": {
                                "Code": None,
                                "Name": None,
                                "LocalName": None
                            },
                            "date": None
                        }
                        for j in response_data_2[0]["OperationalMailitems"]["TMailitemInfoFromScanning"][0]["Events"]["TMailitemEventScanning"]:
                            form["IPSEventType"]["Code"] = j["IPSEventType"]["Name"]
                            form["IPSEventType"]["Code"] = j["IPSEventType"]["Code"]
                            form["IPSEventType"]["LocalName"] = j["IPSEventType"]["Localname"]
                            form["date"] = j['GmtDateTime']
                            full_track_temu.append(form)

                        if response_data_2[0]["InfoFromEdi"] != None:
                            for i in response_data_2[0]["InfoFromEdi"]["TMailitemInfoFromEDI"][0]["Events"][
                                "TMailitemEventEDI"]:
                                form_op = {
                                    "EventOffice": {
                                        "Code": "UZTASA",
                                        "Name": "UzPost"
                                    },
                                    "IPSEventType": {
                                        "Code": None,
                                        "Name": None,
                                        "LocalName": None
                                    },
                                    "date": None
                                }
                                form_op["IPSEventType"]["Code"] = i["IPSEventType"]["Name"]
                                form_op["IPSEventType"]["Code"] = i["IPSEventType"]["Code"]
                                form_op["IPSEventType"]["LocalName"] = i["IPSEventType"]["Localname"]
                                form_op["date"] = j['GmtDateTime']
                                full_track_temu.append(form_op)
                        if not any(item_x["IPSEventType"]["Name"] == "Deliver item (Inb)" for item_x in
                                   full_track_temu) or not any(
                            item_x["IPSEventType"]["Name"] == "Deliver item (Otb)" for item_x in
                            full_track_temu):
                            for data in data_shipox['data']["list"]:
                                if data["status"] == 'issued_to_recipient':
                                    form_f = {
                                        "EventOffice": {
                                            "Code": "UZTASA",
                                            "Name": "UzPost"
                                        },
                                        "IPSEventType": {
                                            "Code": None,
                                            "Name": None,
                                            "LocalName": None
                                        },
                                        "date": None
                                    }
                                    form_f['IPSEventType']["Name"] = "Deliver item"
                                    form_f['IPSEventType']["LocalName"] = "Deliver item"
                                    form_f['IPSEventType']["Code"] = "1257"
                                    form_f["date"] = item['date']
                                    full_track_temu.append(form_f)
                                    break
                                if data["status"] == 'completed':
                                    form_j = {
                                        "EventOffice": {
                                            "Code": "UZTASA",
                                            "Name": "UzPost"
                                        },
                                        "IPSEventType": {
                                            "Code": None,
                                            "Name": None,
                                            "LocalName": None
                                        },
                                        "date": None
                                    }
                                    form_j['IPSEventType']["Name"] = "Deliver item"
                                    form_j['IPSEventType']["LocalName"] = "Deliver item"
                                    form_j['IPSEventType']["Code"] = "1257"
                                    form_j["date"] = data['date']
                                    full_track_temu.append(form_j)
                                    break

                        full_data = {}
                        full_data['header'] = data_header
                        full_data['data'] = full_track_temu

                        return Response(data=full_data, status=200)

                    form = {
                        "EventOffice": {
                            "Code": "UZTASA",
                            "Name": "UzPost"
                            },
                        "IPSEventType": {
                            "Code": None,
                            "Name": None,
                            "LocalName": None
                            },
                        "date": None
                    }
                    form["IPSEventType"]["Name"] = j["IPSEventType"]["Name"]
                    form["IPSEventType"]["Code"] = j["IPSEventType"]["Code"]
                    form["IPSEventType"]["LocalName"] = j["IPSEventType"]["LocalName"]
                    form["date"] = j['GmtDateTime']
                    full_track_temu.append(form)
                    break

        ##############
        #############
        ### buyog'i shipox ma'lumotlari
        #############################

        max_retries = 1  # Maksimal urinishlar soni
        retry_delay = 1  # Qayta urinishdan oldin kutish (soniyada)
        url_header = f"https://prodapi.pochta.uz/api/v1/public/order/{barcode}"
        url_shipox = f"https://prodapi.pochta.uz/api/v1/customer/order/{barcode}/history_items"
        for attempt in range(max_retries):
            try:
                # APIga so'rov yuborish
                data_header = requests.get(url_header, headers={
                    'Content-Type': 'application/json',
                    'Accept': 'application/json',
                    'Authorization': f'Bearer {gettoken()}'
                }, timeout=1)
                data_shipox = requests.get(url_shipox, headers={
                    'Content-Type': 'application/json',
                    'Accept': 'application/json',
                    'Authorization': f'Bearer {gettoken()}'
                }, timeout=1)
                data_header = data_header.json()
                data_shipox = data_shipox.json()
                if data_header['status'] != 'success':
                    return Response(data=data_header, status=404)
                if data_shipox['status'] != 'success':
                    return Response(data=data_header, status=404)
                #######################################

                ##### 1-status uchun tekshirish

                for item in data_shipox['data']['list']:
                    if item["status"] == 'in_sorting_facility':
                        form = {
                            "EventOffice": {
                                "Code": "UZTASA",
                                "Name": "UzPost"
                            },
                            "IPSEventType": {
                                "Code": None,
                                "Name": None,
                                "LocalName": None
                            },
                            "date": None
                        }
                        form['IPSEventType']["Name"] = "Arrived item at office of exchange"
                        form['IPSEventType']["LocalName"] = "Arrived item at office of exchange"
                        form['IPSEventType']["Code"] = "1251"
                        form["date"] = item["date"]
                        last_form = form
                if last_form:
                    full_track_temu.append(last_form)


                ######### 2- status uchun tekshirish

                for item in data_shipox['data']['list']:
                    if item["status"] == 'sent_to_customs':
                        form = {
                            "EventOffice": {
                                "Code": "UZTASA",
                                "Name": "UzPost"
                            },
                            "IPSEventType": {
                                "Code": None,
                                "Name": None,
                                "LocalName": None
                            },
                            "date": None
                        }
                        form['IPSEventType']["Name"] = "Send item to customs"
                        form['IPSEventType']["LocalName"] = "Send item to customs"
                        form['IPSEventType']["Code"] = "1252"
                        form["date"] = item["date"]
                        full_track_temu.append(form)
                        break

                ############# 3-status uchun tekshirish

                for item in data_shipox['data']['list']:
                    if item["status"] == 'hold_on_at_customs':
                        form = {
                            "EventOffice": {
                                "Code": "UZTASA",
                                "Name": "UzPost"
                            },
                            "IPSEventType": {
                                "Code": None,
                                "Name": None,
                                "LocalName": None
                            },
                            "date": None
                        }
                        form['IPSEventType']["Name"] = "Custom Clearance Exception - Inspection"
                        form['IPSEventType']["LocalName"] = "Custom Clearance Exception - Inspection"
                        form['IPSEventType']["Code"] = "1262"
                        form['IPSEventType']["Comment"] = "High-value goods - Official customs declaration required"
                        form["date"] = item["date"]
                        full_track_temu.append(form)
                        break
                #### 4- status uchun tekshirish
                for item in data_shipox['data']['list']:
                    if item["status"] == 'returned_from_customs':
                        form = {
                            "EventOffice": {
                                "Code": "UZTASA",
                                "Name": "UzPost"
                            },
                            "IPSEventType": {
                                "Code": None,
                                "Name": None,
                                "LocalName": None
                            },
                            "date": None
                        }
                        form['IPSEventType']["Name"] = "Return item from customs"
                        form['IPSEventType']["LocalName"] = "Return item from customs"
                        form['IPSEventType']["Code"] = "1253"
                        form["date"] = item["date"]
                        full_track_temu.append(form)
                        ########### 10 min qo'shib qo'shiladi
                        form_1 = {
                                    "EventOffice": {
                                        "Code": "UZTASA",
                                        "Name": "UzPost"
                                    },
                                    "IPSEventType": {
                                        "Code": None,
                                        "Name": None,
                                        "LocalName": None
                                    },
                                    "date": None
                                }
                        form_1['IPSEventType']["Name"] = "Send item to domestic location"
                        form_1['IPSEventType']["LocalName"] = "Send item to domestic location"
                        form_1['IPSEventType']["Code"] = "1254"
                        date_obj = datetime.fromisoformat(item["date"][:19]) + timedelta(minutes=10)
                        form_1["date"] = date_obj.isoformat()
                        full_track_temu.append(form_1)

                        ###### yana 20 minut qo'shib qo'shiladi
                        form_2 = {
                                    "EventOffice": {
                                        "Code": "UZTASA",
                                        "Name": "UzPost"
                                    },
                                    "IPSEventType": {
                                        "Code": None,
                                        "Name": None,
                                        "LocalName": None
                                    },
                                    "date": None
                                }
                        form_2['IPSEventType']["Name"] = "Receive item at delivery office"
                        form_2['IPSEventType']["LocalName"] = "Receive item at delivery office"
                        form_2['IPSEventType']["Code"] = "1255"
                        date_obj = datetime.fromisoformat(item["date"][:19]) + timedelta(minutes=20)
                        form_2["date"] = date_obj.isoformat()
                        full_track_temu.append(form_2)

                        # ######## yana 50 min qo'shib qo'yiladi
                        form_3 = {
                                    "EventOffice": {
                                        "Code": "UZTASA",
                                        "Name": "UzPost"
                                    },
                                    "IPSEventType": {
                                        "Code": None,
                                        "Name": None,
                                        "LocalName": None
                                    },
                                    "date": None
                                }
                        # form_3['IPSEventType']["Name"] = "Ready for Delivery"
                        # form_3['IPSEventType']["LocalName"] = "Ready for Delivery"
                        # form_3['IPSEventType']["Code"] = "1263"
                        # date_obj = datetime.fromisoformat(item["date"][:19]) + timedelta(minutes=50)
                        # form_3["date"] = date_obj.isoformat()
                        # full_track_temu.append(form_3)
                        break

                ############## ready for delivery ga tekshirish

                for item in data_shipox['data']['list']:
                    if item["status"] == 'ready_for_delivery':
                        for item_x in full_track_temu:
                            if "ready_for_delivery" == item_x["IPSEventType"]["Name"]:
                                item_x["IPSEventType"]["date"] = item["date"]

                        if not any(item_x["IPSEventType"]["Name"] == "Return item from customs" for item_x in full_track_temu):

                                form = {
                                    "EventOffice": {
                                        "Code": "UZTASA",
                                        "Name": "UzPost"
                                    },
                                    "IPSEventType": {
                                        "Code": None,
                                        "Name": None,
                                        "LocalName": None
                                    },
                                    "date": None
                                }
                                form['IPSEventType']["Name"] = "Return item from customs"
                                form['IPSEventType']["LocalName"] = "Return item from customs"
                                form['IPSEventType']["Code"] = "1253"
                                date_obj = datetime.fromisoformat(item["date"][:19]) - timedelta(minutes=50)
                                form["date"] = date_obj.isoformat()
                                full_track_temu.append(form)

                                ########### 10 min qo'shib qo'shiladi
                                form_1 = {
                                    "EventOffice": {
                                        "Code": "UZTASA",
                                        "Name": "UzPost"
                                    },
                                    "IPSEventType": {
                                        "Code": None,
                                        "Name": None,
                                        "LocalName": None
                                    },
                                    "date": None
                                }
                                form_1['IPSEventType']["Name"] = "Send item to domestic location"
                                form_1['IPSEventType']["LocalName"] = "Send item to domestic location"
                                form_1['IPSEventType']["Code"] = "1254"
                                date_obj = datetime.fromisoformat(item["date"][:19]) - timedelta(minutes=40)
                                form_1["date"] = date_obj.isoformat()
                                full_track_temu.append(form_1)

                                ###### yana 20 minut qo'shib qo'shiladi
                                form_2 = {
                                    "EventOffice": {
                                        "Code": "UZTASA",
                                        "Name": "UzPost"
                                    },
                                    "IPSEventType": {
                                        "Code": None,
                                        "Name": None,
                                        "LocalName": None
                                    },
                                    "date": None
                                }
                                form_2['IPSEventType']["Name"] = "Receive item at delivery office"
                                form_2['IPSEventType']["LocalName"] = "Receive item at delivery office"
                                form_2['IPSEventType']["Code"] = "1255"
                                date_obj = datetime.fromisoformat(item["date"][:19]) - timedelta(minutes=30)
                                form_1["date"] = date_obj.isoformat()
                                full_track_temu.append(form_2)

                        form_3 = {
                                    "EventOffice": {
                                        "Code": "UZTASA",
                                        "Name": "UzPost"
                                    },
                                    "IPSEventType": {
                                        "Code": None,
                                        "Name": None,
                                        "LocalName": None
                                    },
                                    "date": None
                                }
                        form_3['IPSEventType']["Name"] = "Ready for Delivery"
                        form_3['IPSEventType']["LocalName"] = "Ready for Delivery"
                        form_3['IPSEventType']["Code"] = "1263"
                        form_3["date"] = item['date']
                        full_track_temu.append(form_3)
                        break

                    ############### out for deliveryga tekshirish
                    if item["status"] == 'out_for_delivery':
                        if not any(item_x["IPSEventType"]["Name"] == "Return item from customs" for item_x in full_track_temu):
                            form = {
                                "EventOffice": {
                                    "Code": "UZTASA",
                                    "Name": "UzPost"
                                },
                                "IPSEventType": {
                                    "Code": None,
                                    "Name": None,
                                    "LocalName": None
                                },
                                "date": None
                            }
                            form['IPSEventType']["Name"] = "Return item from customs"
                            form['IPSEventType']["LocalName"] = "Return item from customs"
                            form['IPSEventType']["Code"] = "1253"
                            date_obj = datetime.fromisoformat(item["date"][:19]) - timedelta(minutes=50)
                            form["date"] = date_obj.isoformat()
                            full_track_temu.append(form)

                            ########### 10 min qo'shib qo'shiladi
                            form_1 = {
                                    "EventOffice": {
                                        "Code": "UZTASA",
                                        "Name": "UzPost"
                                    },
                                    "IPSEventType": {
                                        "Code": None,
                                        "Name": None,
                                        "LocalName": None
                                    },
                                    "date": None
                                }
                            form_1['IPSEventType']["Name"] = "Send item to domestic location"
                            form_1['IPSEventType']["LocalName"] = "Send item to domestic location"
                            form_1['IPSEventType']["Code"] = "1254"
                            date_obj = datetime.fromisoformat(item["date"][:19]) - timedelta(minutes=40)
                            form_1["date"] = date_obj.isoformat()
                            full_track_temu.append(form_1)

                            ###### yana 20 minut qo'shib qo'shiladi
                            form_2 = {
                                    "EventOffice": {
                                        "Code": "UZTASA",
                                        "Name": "UzPost"
                                    },
                                    "IPSEventType": {
                                        "Code": None,
                                        "Name": None,
                                        "LocalName": None
                                    },
                                    "date": None
                                }
                            form_2['IPSEventType']["Name"] = "Receive item at delivery office"
                            form_2['IPSEventType']["LocalName"] = "Receive item at delivery office"
                            form_2['IPSEventType']["Code"] = "1255"
                            date_obj = datetime.fromisoformat(item["date"][:19]) - timedelta(minutes=30)
                            form_1["date"] = date_obj.isoformat()
                            full_track_temu.append(form_2)

                        form_3 = {
                                    "EventOffice": {
                                        "Code": "UZTASA",
                                        "Name": "UzPost"
                                    },
                                    "IPSEventType": {
                                        "Code": None,
                                        "Name": None,
                                        "LocalName": None
                                    },
                                    "date": None
                                }
                        form_3['IPSEventType']["Name"] = "Out for delivery"
                        form_3['IPSEventType']["LocalName"] = "Out for delivery"
                        form_3['IPSEventType']["Code"] = "1264"
                        form_3["date"] = item['date']
                        full_track_temu.append(form_3)
                        break

                for item in data_shipox['data']['list']:
                    if item["status"] == 'not_at_home':
                        form_2 = {
                            "EventOffice": {
                                "Code": "UZTASA",
                                "Name": "UzPost"
                            },
                            "IPSEventType": {
                                "Code": None,
                                "Name": None,
                                "LocalName": None
                            },
                            "date": None
                        }
                        form_2['IPSEventType']["Name"] = "Unsuccessful item delivery attempt - Addressee not available"
                        form_2['IPSEventType']["LocalName"] = "Unsuccessful item delivery attempt - Addressee not available"
                        form_2['IPSEventType']["Code"] = "1256"
                        form_2["date"] = item["date"]
                        full_track_temu.append(form_2)

                        form_3 = {
                            "EventOffice": {
                                "Code": "UZTASA",
                                "Name": "UzPost"
                            },
                            "IPSEventType": {
                                "Code": None,
                                "Name": None,
                                "LocalName": None
                            },
                            "date": None
                        }
                        form_3['IPSEventType']["Name"] = "Unsuccessful item delivery attempt -Customer requested own Pick up"
                        form_3['IPSEventType'][
                            "LocalName"] = "Unsuccessful item delivery attempt -Customer requested own Pick up"
                        form_3['IPSEventType']["Code"] = "1268"
                        date_obj = datetime.fromisoformat(item["date"][:19]) + timedelta(minutes=2)
                        form_3["date"] = date_obj.isoformat()
                        full_track_temu.append(form_3)
                        break


                ######## delivered uchun tekshirish
                for item in data_shipox['data']['list']:
                    if item["status"] == 'completed':
                        if not any(item_x["IPSEventType"]["Name"] == "Out for delivery" for item_x in full_track_temu):
                            form_2 = {
                                    "EventOffice": {
                                        "Code": "UZTASA",
                                        "Name": "UzPost"
                                    },
                                    "IPSEventType": {
                                        "Code": None,
                                        "Name": None,
                                        "LocalName": None
                                    },
                                    "date": None
                                }
                            form_2['IPSEventType']["Name"] = "Out for delivery"
                            form_2['IPSEventType']["LocalName"] = "Out for delivery"
                            form_2['IPSEventType']["Code"] = "1264"
                            date_obj = datetime.fromisoformat(item["date"][:19]) - timedelta(minutes=20)
                            form_2["date"] = date_obj.isoformat()
                            full_track_temu.append(form_2)

                        form_j = {
                                    "EventOffice": {
                                        "Code": "UZTASA",
                                        "Name": "UzPost"
                                    },
                                    "IPSEventType": {
                                        "Code": None,
                                        "Name": None,
                                        "LocalName": None
                                    },
                                    "date": None
                                }
                        form_j['IPSEventType']["Name"] = "Deliver item"
                        form_j['IPSEventType']["LocalName"] = "Deliver item"
                        form_j['IPSEventType']["Code"] = "1257"
                        form_j["date"] = item['date']
                        full_track_temu.append(form_j)
                        break


                    if item["status"] == 'issued_to_recipient':
                        if not any(item_x["IPSEventType"]["Name"] == "Ready for Delivery" for item_x in full_track_temu) and not any(item_x["IPSEventType"]["Name"] == "Out for delivery" for item_x in full_track_temu):
                            print("salom")
                            form_2 = {
                                "EventOffice": {
                                    "Code": "UZTASA",
                                    "Name": "UzPost"
                                },
                                "IPSEventType": {
                                    "Code": None,
                                    "Name": None,
                                    "LocalName": None
                                },
                                "date": None
                            }
                            form_2['IPSEventType']["Name"] = "Ready for Delivery"
                            form_2['IPSEventType']["LocalName"] = "Ready for Delivery"
                            date_obj = datetime.fromisoformat(item["date"][:19]) - timedelta(minutes=20)
                            form_2["date"] = date_obj.isoformat()
                            full_track_temu.append(form_2)

                        form_f = {
                                    "EventOffice": {
                                        "Code": "UZTASA",
                                        "Name": "UzPost"
                                    },
                                    "IPSEventType": {
                                        "Code": None,
                                        "Name": None,
                                        "LocalName": None
                                    },
                                    "date": None
                                }
                        form_f['IPSEventType']["Name"] = "Deliver item"
                        form_f['IPSEventType']["LocalName"] = "Deliver item"
                        form_f['IPSEventType']["Code"] = "1257"
                        form_f["date"] = item['date']
                        full_track_temu.append(form_f)
                        break

                    if item["status"] == 'returning_to_origin':
                        form_f = {
                                    "EventOffice": {
                                        "Code": "UZTASA",
                                        "Name": "UzPost"
                                    },
                                    "IPSEventType": {
                                        "Code": None,
                                        "Name": None,
                                        "LocalName": None
                                    },
                                    "date": None
                                }
                        form_f['IPSEventType']["Name"] = "On the way to sender"
                        form_f['IPSEventType']["LocalName"] = "On the way to sender"
                        form_f['IPSEventType']["Code"] = "1266"
                        form_f["date"] = item['date']
                        full_track_temu.append(form_f)
                        break

                ### oxirgi status

                for item in data_shipox['data']['list']:
                    if item["status"] == 'returned_to_origin':
                        form_f = {
                                    "EventOffice": {
                                        "Code": "UZTASA",
                                        "Name": "UzPost"
                                    },
                                    "IPSEventType": {
                                        "Code": None,
                                        "Name": None,
                                        "LocalName": None
                                    },
                                    "date": None
                                }
                        form_f['IPSEventType']["Name"] = "Delivered to sender"
                        form_f['IPSEventType']["LocalName"] = "Delivered to sender"
                        form_f['IPSEventType']["Code"] = "1266"
                        form_f["date"] = item['date']
                        full_track_temu.append(form_f)
                        break
                full_data = {}
                full_data['header'] = data_header
                full_data['data'] = full_track_temu

                return Response(data=full_data, status=200)
            except ConnectTimeout:
                # Agar ulanish timeoutga uchrasa, qayta urinib ko'riladi
                if attempt < max_retries - 1:
                    time.sleep(retry_delay)  # Kutish va yana urinib ko'rish
                else:
                    total_data_2 = {"header": "Server bilan ulanishda muammo yuz berdi. Iltimos, keyinroq qayta urinib ko'ring.",
                                    "gdeposilka_header": None,
                                    "shipox": "Server bilan bo'glanishda muammo yuz berdi"}



@method_decorator(cache_page(60*15), name='dispatch')
class TrackIsAuth(APIView):
    permission_classes = [IsAuthenticated, IsCustomUsersGet]
    throttle_classes = [CustomUserThrottle, ]

    def get(self, request, barcode):
        if barcode[:2] == "RZ" or barcode[:2] == "CZ" or barcode[:1] == "E":
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
                for i in range(len(response_data_2[0]["InfoFromEdi"]["TMailitemInfoFromEDI"][0]["Events"]["TMailitemEventEDI"])):
                    response_data_2[0]["InfoFromEdi"]["TMailitemInfoFromEDI"][0]["Events"]["TMailitemEventEDI"][i]["ReceivedDispatch"] = None
            if response_data_2[0]["OperationalMailitems"] != None:
                for j in range(len(response_data_2[0]["OperationalMailitems"]["TMailitemInfoFromScanning"][0]["Events"]["TMailitemEventScanning"])):
                    response_data_2[0]["OperationalMailitems"]["TMailitemInfoFromScanning"][0]["Events"]["TMailitemEventScanning"][j]["ReceivedDispatch"] = None
            return Response(data=response_data_2, status=status.HTTP_200_OK)


        data = requests.get(f"https://prodapi.pochta.uz/api/v1/public/order/{barcode}")
        data = data.json()
        if data['status'] != "success":
            return Response(data=data, status=status.HTTP_404_NOT_FOUND)
        total_data_2 = {'header': data}
        if barcode[:2] != 'SX' and data["data"]['locations'][0]['country']['code'] == 'UZ' and data["data"]['locations'][1]['country']['code'] == 'UZ':
            total_data = requests.get(f"https://prodapi.pochta.uz/api/v1/public/order/{barcode}/history_items")
            total_data_2['shipox'] = total_data.json()
            total_data_2['gdeposilka'] = None
            return Response(total_data_2, status=status.HTTP_200_OK)
        url1 = f"https://gdeposylka.ru/api/v4/tracker/detect/{barcode}"
        headers = {
            "X-Authorization-Token": "65bbbac85f796f8032e0874411f4d1f5af7185a99e184709bf0c1f38d95486fa2338733760a48704"
        }
        response1 = requests.get(url1, headers=headers)
        data = response1.json()
        shipox = requests.get(f"https://prodapi.pochta.uz/api/v1/public/order/{barcode}/history_items")
        total_data_2['shipox'] = shipox.json()

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
        return Response(data=total_data_2, status=status.HTTP_200_OK)


@method_decorator(cache_page(60*15), name='dispatch')
class TmuTrackAPIView(APIView):
    permission_classes = [IsAuthenticated, IsCustomUsersGet]
    throttle_classes = [CustomUserThrottle, ]

    def get(self, request, barcode):
        if barcode[:2] == "RZ" or barcode[:2] == "CZ" or barcode[:1] == "E":
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
        first = {
            "code": "order_not_found",
            "message": "Order Not Found",
            "request_id": "69f059d0-1748-42cc-982c-7a322c4e81fa",
            "status": "error"
        }
        return Response(data=first, status=status.HTTP_404_NOT_FOUND)


class UsersRequestsDetailView(APIView):
    permission_classes = [AllowAny, IsCustomUsersPost]
    throttle_classes = [CustomUserThrottle, ]

    def post(self, request):
        serializer = UsersRequestsSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class BannerAPIViewSet(viewsets.ModelViewSet):
    permission_classes = [AllowAny, IsCustomUsersGet]
    throttle_classes = [CustomUserThrottle, ]

    queryset = Banners.objects.all()
    serializer_class = BannersSerializer

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        if instance.image:
            if os.path.isfile(instance.image.path):
                os.remove(instance.image.path)
        self.perform_destroy(instance)
        return Response(status=status.HTTP_204_NO_CONTENT)

    def perform_destroy(self, instance):
        instance.delete()

    def update(self, request, *args, **kwargs):
        instance = self.get_object()
        # Oldingi rasm faylini o'chirish
        if 'image' in request.data and not request.data['image']:
            if instance.image:
                if os.path.isfile(instance.image.path):
                    os.remove(instance.image.path)
                instance.image = None

        serializer = self.get_serializer(instance, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)

        return Response(serializer.data)

    def perform_update(self, serializer):
        serializer.save()


class MenuElementsAPIViewSet(viewsets.ModelViewSet):
    queryset = MenuElements.objects.all()
    serializer_class = MenuElementsSerializer
    permission_classes = [AllowAny, IsCustomUsersGet]
    throttle_classes = [CustomUserThrottle, ]


class MenuAPIViewSet(viewsets.ModelViewSet):
    queryset = Menu.objects.all()
    serializer_class = MenuSerializer
    permission_classes = [AllowAny, IsCustomUsersGet]
    throttle_classes = [CustomUserThrottle, ]

    @action(detail=True, methods=['get'])
    def menu_elements(self, request, *args, **kwargs):
        menu = self.get_object()
        menu_elements = menu.menu_elements.all()
        serializer = MenuElementsSerializer(menu_elements, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @menu_elements.mapping.post
    def add_menu_element(self, request, *args, **kwargs):
        menu = self.get_object()
        serializer = MenuElementsSerializer(data=request.data)
        if serializer.is_valid():
            menu_element = serializer.save()
            menu.menu_elements.add(menu_element)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=['get'])
    def menu_element_detail(self, request, *args, **kwargs):
        id = request.data.get('id')
        if type(id) != int or id is None:
            return Response(data="Try to enter the correct id", status=status.HTTP_400_BAD_REQUEST)
        menu = self.get_object()
        menu_elements = menu.menu_elements.filter(id=id).first()
        if menu_elements is None:
            return Response(data="Statistic Item not found", status=status.HTTP_404_NOT_FOUND)
        serializer = MenuElementsSerializer(menu_elements)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @menu_element_detail.mapping.put
    def update_menu_element_detail(self, request, *args, **kwargs):
        id = request.data.get('id')
        if type(id) != int or id is None:
            return Response(data="Try to enter the correct id", status=status.HTTP_400_BAD_REQUEST)
        menu = self.get_object()
        menu_elements = menu.menu_elements.filter(id=id).first()
        if menu_elements is None:
            return Response(data="Menu Element not found", status=status.HTTP_404_NOT_FOUND)
        serializer = MenuElementsSerializer(menu_elements, data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            user.save()
            return Response(data=serializer.data, status=status.HTTP_200_OK)
        return Response(status=status.HTTP_400_BAD_REQUEST, data=serializer.errors)

    @menu_element_detail.mapping.delete
    def delete_menu_element(self, request, *args, **kwargs):
        menu = self.get_object()
        id = request.data.get('id')
        if type(id) != int:
            return Response(data="You must enter the id as an int type", status=status.HTTP_400_BAD_REQUEST)
        data = menu.menu_elements.filter(id=id)
        if not data:
            return Response(data="No such menu element", status=status.HTTP_404_NOT_FOUND)
        menu.menu_elements.remove(data.first())
        menu_elements = MenuElements.objects.get(id=id)
        menu_elements.delete()
        return Response(data="successful deleted", status=status.HTTP_204_NO_CONTENT)


class StatisticItemsAPIViewSet(viewsets.ModelViewSet):
    queryset = StatisticItems.objects.all()
    serializer_class = StatisticItemsSerializer
    permission_classes = [AllowAny, IsCustomUsersPost]
    throttle_classes = [CustomUserThrottle, ]

    @action(detail=False, methods=['POST'])
    def item_score(self, request, *args, **kwargs):
        id = request.data.get('id')
        if not id:
            return Response(data="No such id", status=status.HTTP_400_BAD_REQUEST)
        try:
            id = int(id)
        except ValueError:
            return Response(data="You must enter the id as int type", status=status.HTTP_400_BAD_REQUEST)

        data = get_object_or_404(StatisticItems, id=id)
        data.number_responses += 1
        data.save()
        return Response(data="successful", status=status.HTTP_200_OK)


class StatisticsAPIViewSet(viewsets.ModelViewSet):
    queryset = Statistics.objects.all()
    serializer_class = StatisticsSerializer
    permission_classes = [AllowAny, IsCustomUsersGet]
    throttle_classes = [CustomUserThrottle, ]

    @action(detail=True, methods=['get'])
    def statistic_items(self, request, *args, **kwargs):
        statistic = self.get_object()
        statistic_items = statistic.statistic_items.all()
        serializer = StatisticItemsSerializer(statistic_items, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @statistic_items.mapping.post
    def add_statistic_item(self, request, *args, **kwargs):
        statistics = self.get_object()
        serializer = StatisticItemsSerializer(data=request.data)
        if serializer.is_valid():
            statistic_item = serializer.save()
            statistics.statistic_items.add(statistic_item)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=['get'])
    def statistic_item_detail(self, request, *args, **kwargs):
        id = request.data.get('id')
        if type(id) != int or id is None:
            return Response(data="Try to enter the correct id", status=status.HTTP_400_BAD_REQUEST)
        statistic = self.get_object()
        statistic_items = statistic.statistic_items.filter(id=id).first()
        if statistic_items is None:
            return Response(data="Statistic Item not found", status=status.HTTP_404_NOT_FOUND)
        serializer = StatisticItemsSerializer(statistic_items)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @statistic_item_detail.mapping.put
    def update_statistic_item(self, request, *args, **kwargs):
        id = request.data.get('id')
        if type(id) != int or id is None:
            return Response(data="Try to enter the correct id", status=status.HTTP_400_BAD_REQUEST)
        statistic = self.get_object()
        statistic_item = statistic.statistic_items.filter(id=id).first()
        if statistic_item is None:
            return Response(data="Statistic Item not found", status=status.HTTP_404_NOT_FOUND)
        serializer = StatisticItemsSerializer(statistic_item, data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            user.save()
            return Response(data=serializer.data, status=status.HTTP_200_OK)
        return Response(status=status.HTTP_400_BAD_REQUEST, data=serializer.errors)

    @statistic_item_detail.mapping.delete
    def delete_statistic_item(self, request, *args, **kwargs):
        statistics = self.get_object()
        id = request.data.get('id')
        if type(id) != int:
            return Response(data="You must enter the id as an int type", status=status.HTTP_400_BAD_REQUEST)
        data = statistics.statistic_items.filter(id=id)
        if not data:
            return Response(data="No such menu element", status=status.HTTP_404_NOT_FOUND)
        statistics.statistic_items.remove(data.first())
        statistic_items = StatisticItems.objects.get(id=id)
        statistic_items.delete()
        return Response(data="successful deleted", status=status.HTTP_204_NO_CONTENT)


class TegRegionsAPIViewSet(viewsets.ModelViewSet):
    queryset = TegRegions.objects.all()
    serializer_class = TegRegionsSerializer
    permission_classes = [AllowAny, IsCustomUsersGet]
    throttle_classes = [CustomUserThrottle, ]


class TegWorkingDaysAPIViewSet(viewsets.ModelViewSet):
    queryset = TegWorkingDays.objects.all()
    serializer_class = TegWorkingDaysSerializer
    permission_classes = [AllowAny, IsCustomUsersGet]
    throttle_classes = [CustomUserThrottle, ]


class TegExperiencesAPIViewSet(viewsets.ModelViewSet):
    queryset = TegExperience.objects.all()
    serializer_class = TegExperiencesSerializer
    permission_classes = [AllowAny, IsCustomUsersGet]
    throttle_classes = [CustomUserThrottle, ]


class TegVacanciesAPIViewSet(viewsets.ModelViewSet):
    queryset = TegVacancies.objects.all()
    serializer_class = TegVacanciesSerializer
    permission_classes = [AllowAny, IsCustomUsersGet]
    throttle_classes = [CustomUserThrottle, ]


class TegBranches2APIViewSet(viewsets.ModelViewSet):
    queryset = TegBranches2.objects.all()
    serializer_class = TegBranches2Serializer
    permission_classes = [AllowAny, IsCustomUsersGet]
    throttle_classes = [CustomUserThrottle, ]


class VacanciesAPIViewSet(viewsets.ModelViewSet):
    queryset = Vacancies.objects.all()
    serializer_class = VacanciesSerializer
    permission_classes = [AllowAny, IsCustomUsersGet]
    throttle_classes = [CustomUserThrottle, ]

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        if instance.save_image:
            if os.path.isfile(instance.save_image.path):
                os.remove(instance.save_image.path)
        self.perform_destroy(instance)
        return Response(status=status.HTTP_204_NO_CONTENT)

    def perform_destroy(self, instance):
        instance.delete()

    def update(self, request, *args, **kwargs):
        instance = self.get_object()
        # Oldingi rasm faylini o'chirish
        if 'save_image' in request.data and not request.data['save_image']:
            if instance.save_image:
                if os.path.isfile(instance.save_image.path):
                    os.remove(instance.save_image.path)
                instance.save_image = None

        serializer = self.get_serializer(instance, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)

        return Response(serializer.data)

    def perform_update(self, serializer):
        serializer.save()


class PurchasesAPIViewSet(ModelViewSet):
    queryset = Purchases.objects.all()
    serializer_class = PurchasesSerializer
    permission_classes = [AllowAny, IsCustomUsersGet]
    throttle_classes = [CustomUserThrottle, ]

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        if instance.save_image:
            if os.path.isfile(instance.save_image.path):
                os.remove(instance.save_image.path)
        self.perform_destroy(instance)
        return Response(status=status.HTTP_204_NO_CONTENT)

    def perform_destroy(self, instance):
        instance.delete()

    def update(self, request, *args, **kwargs):
        instance = self.get_object()
        # Oldingi rasm faylini o'chirish
        if 'save_image' in request.data and not request.data['save_image']:
            if instance.save_image:
                if os.path.isfile(instance.save_image.path):
                    os.remove(instance.save_image.path)
                instance.save_image = None

        serializer = self.get_serializer(instance, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)

        return Response(serializer.data)

    def perform_update(self, serializer):
        serializer.save()


class MarksAPIViewSet(ModelViewSet):
    queryset = Marks.objects.all()
    serializer_class = MarksSerializer
    permission_classes = [AllowAny, IsCustomUsersGet]
    throttle_classes = [CustomUserThrottle, ]

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        if instance.save_image_uz:
            if os.path.isfile(instance.save_image.path):
                os.remove(instance.save_image_uz.path)
        if instance.save_image_ru and os.path.isfile(instance.save_image_ru.path):
            os.remove(instance.save_image_ru.path)

        self.perform_destroy(instance)
        return Response(status=status.HTTP_204_NO_CONTENT)

    def perform_destroy(self, instance):
        instance.delete()

    def update(self, request, *args, **kwargs):
        instance = self.get_object()
        # Oldingi rasm faylini o'chirish
        if 'save_image_uz' in request.data and not request.data['save_image_uz']:
            if instance.save_image_uz:
                if os.path.isfile(instance.save_image_uz.path):
                    os.remove(instance.save_image_uz.path)
                instance.save_image_uz = None
        if 'save_image_ru' in request.data and not request.data['save_image_ru']:
            if instance.save_image_ru and os.path.isfile(instance.save_image_ru.path):
                os.remove(instance.save_image_ru.path)

        serializer = self.get_serializer(instance, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)

        return Response(serializer.data)

    def perform_update(self, serializer):
        serializer.save()


class MarksFilter(filters.FilterSet):
    years = filters.RangeFilter(field_name='years')
    class Meta:
        model = Marks
        fields = ["years"]


class MarksAsosiyAPIViewSet(ModelViewSet):
    queryset = Marks.objects.all()
    serializer_class = MarksSerializer
    permission_classes = [AllowAny, IsCustomUsersGet]
    throttle_classes = [CustomUserThrottle, ]
    pagination_class = CustomPagination
    filter_backends = [DjangoFilterBackend]
    filterset_class = MarksFilter


    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        if instance.save_image_uz:
            if os.path.isfile(instance.save_image.path):
                os.remove(instance.save_image_uz.path)
        if instance.save_image_ru and os.path.isfile(instance.save_image_ru.path):
            os.remove(instance.save_image_ru.path)

        self.perform_destroy(instance)
        return Response(status=status.HTTP_204_NO_CONTENT)

    def perform_destroy(self, instance):
        instance.delete()

    def update(self, request, *args, **kwargs):
        instance = self.get_object()
        # Oldingi rasm faylini o'chirish
        if 'save_image_uz' in request.data and not request.data['save_image_uz']:
            if instance.save_image_uz:
                if os.path.isfile(instance.save_image_uz.path):
                    os.remove(instance.save_image_uz.path)
                instance.save_image_uz = None
        if 'save_image_ru' in request.data and not request.data['save_image_ru']:
            if instance.save_image_ru and os.path.isfile(instance.save_image_ru.path):
                os.remove(instance.save_image_ru.path)

        serializer = self.get_serializer(instance, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)

        return Response(serializer.data)

    def perform_update(self, serializer):
        serializer.save()


class SaveMediaFilesAPIViewSet(ModelViewSet):
    queryset = SaveMediaFiles.objects.all()
    serializer_class = SaveMediaFilesSerializer
    permission_classes = [AllowAny, IsCustomUsersGet]
    throttle_classes = [CustomUserThrottle, ]

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        if instance.file:
            if os.path.isfile(instance.file.path):
                os.remove(instance.file.path)
        self.perform_destroy(instance)
        return Response(status=status.HTTP_204_NO_CONTENT)

    def perform_destroy(self, instance):
        instance.delete()

    def update(self, request, *args, **kwargs):
        instance = self.get_object()
        # Oldingi rasm faylini o'chirish
        if 'file' in request.data and not request.data['file']:
            if instance.file:
                if os.path.isfile(instance.file.path):
                    os.remove(instance.file.path)
                instance.file = None

        serializer = self.get_serializer(instance, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)

        return Response(serializer.data)

    def perform_update(self, serializer):
        serializer.save()


class EventsAPIViewSet(ModelViewSet):
    queryset = Events.objects.all()
    serializer_class = EventsSerializer
    permission_classes = [AllowAny, IsCustomUsersGet]
    throttle_classes = [CustomUserThrottle, ]

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        if instance.save_image:
            if os.path.isfile(instance.save_image.path):
                os.remove(instance.save_image.path)
        self.perform_destroy(instance)
        return Response(status=status.HTTP_204_NO_CONTENT)

    def perform_destroy(self, instance):
        instance.delete()

    def update(self, request, *args, **kwargs):
        instance = self.get_object()
        # Oldingi rasm faylini o'chirish
        if 'save_image' in request.data and not request.data['save_image']:
            if instance.save_image:
                if os.path.isfile(instance.save_image.path):
                    os.remove(instance.save_image.path)
                instance.save_image = None

        serializer = self.get_serializer(instance, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)

        return Response(serializer.data)

    def perform_update(self, serializer):
        serializer.save()


class UzPostNewsAPIViewSet(ModelViewSet):
    queryset = UzPostNews.objects.all()
    serializer_class = UzPostNewsSerializer
    permission_classes = [AllowAny, IsCustomUsersGet]
    throttle_classes = [CustomUserThrottle, ]

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        if instance.save_image:
            if os.path.isfile(instance.save_image.path):
                os.remove(instance.save_image.path)
        self.perform_destroy(instance)
        return Response(status=status.HTTP_204_NO_CONTENT)

    def perform_destroy(self, instance):
        instance.delete()

    def update(self, request, *args, **kwargs):
        instance = self.get_object()
        # Oldingi rasm faylini o'chirish
        if 'save_image' in request.data and not request.data['save_image']:
            if instance.save_image:
                if os.path.isfile(instance.save_image.path):
                    os.remove(instance.save_image.path)
                instance.save_image = None

        serializer = self.get_serializer(instance, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)

        return Response(serializer.data)

    def perform_update(self, serializer):
        serializer.save()


class PostalServicesAPIViewSet(ModelViewSet):
    queryset = PostalServices.objects.all()
    serializer_class = PostalServicesSerializer
    permission_classes = [AllowAny, IsCustomUsersGet]
    throttle_classes = [CustomUserThrottle, ]

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        if instance.save_image:
            if os.path.isfile(instance.save_image.path):
                os.remove(instance.save_image.path)
        self.perform_destroy(instance)
        return Response(status=status.HTTP_204_NO_CONTENT)

    def perform_destroy(self, instance):
        instance.delete()

    def update(self, request, *args, **kwargs):
        instance = self.get_object()
        # Oldingi rasm faylini o'chirish
        if 'save_image' in request.data and not request.data['save_image']:
            if instance.save_image:
                if os.path.isfile(instance.save_image.path):
                    os.remove(instance.save_image.path)
                instance.save_image = None

        serializer = self.get_serializer(instance, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)

        return Response(serializer.data)

    def perform_update(self, serializer):
        serializer.save()


class PagesAPIViewSet(ModelViewSet):
    queryset = Pages.objects.all()
    serializer_class = PagesSerializer
    permission_classes = [AllowAny, IsCustomUsersGet]
    throttle_classes = [CustomUserThrottle, ]

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        if instance.save_image:
            if os.path.isfile(instance.save_image.path):
                os.remove(instance.save_image.path)
        self.perform_destroy(instance)
        return Response(status=status.HTTP_204_NO_CONTENT)

    def perform_destroy(self, instance):
        instance.delete()

    def update(self, request, *args, **kwargs):
        instance = self.get_object()
        # Oldingi rasm faylini o'chirish
        if 'save_image' in request.data and not request.data['save_image']:
            if instance.save_image:
                if os.path.isfile(instance.save_image.path):
                    os.remove(instance.save_image.path)
                instance.save_image = None

        serializer = self.get_serializer(instance, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)

        return Response(serializer.data)

    def perform_update(self, serializer):
        serializer.save()


class CategoryPagesViewSet(ModelViewSet):
    queryset = CategoryPages.objects.all()
    serializer_class = CategoryPagesSerializer
    permission_classes = [AllowAny, IsCustomUsersGet]
    throttle_classes = [CustomUserThrottle, ]

    @action(detail=True, methods=['post'])
    def pages(self, request, *args, **kwargs):
        category = self.get_object()
        serializer = PagesSerializer(data=request.data)
        if serializer.is_valid():
            pages = serializer.save()
            category.pages.add(pages)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @pages.mapping.put
    def update_pages(self, request, *args, **kwargs):
        id = request.data.get('id')
        if type(id) != int or id is None:
            return Response(data="Try to enter the correct id", status=status.HTTP_400_BAD_REQUEST)
        category = self.get_object()
        page = category.pages.filter(id=id).first()
        if page is None:
            return Response(data="postal service not found", status=status.HTTP_404_NOT_FOUND)
        serializer = PagesSerializer(page, data=request.data)
        if serializer.is_valid():
            page_1 = serializer.save()
            page_1.save()
            return Response(data=serializer.data, status=status.HTTP_200_OK)
        return Response(status=status.HTTP_400_BAD_REQUEST, data=serializer.errors)

    @pages.mapping.delete
    def delete_pages(self, request, *args, **kwargs):
        category = self.get_object()
        id = request.data.get('id')
        if type(id) != int:
            return Response(data="You must enter the id as an int type", status=status.HTTP_400_BAD_REQUEST)
        data = category.pages.filter(id=id)
        if not data:
            return Response(data="No such postal service", status=status.HTTP_404_NOT_FOUND)
        category.pages.remove(data.first())
        page = Pages.objects.get(id=id)
        page.delete()
        return Response(data="successful deleted", status=status.HTTP_204_NO_CONTENT)


class ControlCategoryPageViewSet(ModelViewSet):
    queryset = ControlCategoryPages.objects.all()
    serializer_class = ControlCategoryPagesSerializer
    permission_classes = [IsAuthenticated, IsCustomUsersGet]
    throttle_classes = [CustomUserThrottle, ]

    @action(detail=True, methods=['post'])
    def category_pages(self, request, *args, **kwargs):
        control_category = self.get_object()
        serializer = CategoryPagesSerializer(data=request.data)
        if serializer.is_valid():
            category = serializer.save()
            control_category.page_categories.add(category)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @category_pages.mapping.put
    def update_category_page(self, request, *args, **kwargs):
        id = request.data.get('id')
        if type(id) != int or id is None:
            return Response(data="Try to enter the correct id", status=status.HTTP_400_BAD_REQUEST)
        control_category_page = self.get_object()
        page = control_category_page.page_categories.filter(id=id).first()
        if page is None:
            return Response(data="category page not found", status=status.HTTP_404_NOT_FOUND)
        serializer = CategoryPagesSerializer(page, data=request.data)
        if serializer.is_valid():
            page_1 = serializer.save()
            page_1.save()
            return Response(data=serializer.data, status=status.HTTP_200_OK)
        return Response(status=status.HTTP_400_BAD_REQUEST, data=serializer.errors)

    @category_pages.mapping.delete
    def delete_category_page(self, request, *args, **kwargs):
        controlcategory = self.get_object()
        id = request.data.get('id')
        if type(id) != int:
            return Response(data="You must enter the id as an int type", status=status.HTTP_400_BAD_REQUEST)
        data = controlcategory.page_categories.filter(id=id)
        if not data:
            return Response(data="No such category pages", status=status.HTTP_404_NOT_FOUND)
        controlcategory.page_categories.remove(data.first())
        category_page = CategoryPages.objects.get(id=id)
        category_page.delete()
        return Response(data="successful deleted", status=status.HTTP_204_NO_CONTENT)


class BranchServicesAPIViewSet(ModelViewSet):
    queryset = BranchServices.objects.all()
    serializer_class = BranchServicesSerializer
    permission_classes = [AllowAny, IsCustomUsersGet]
    throttle_classes = [CustomUserThrottle, ]

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        if instance.save_image:
            if os.path.isfile(instance.save_image.path):
                os.remove(instance.save_image.path)
        self.perform_destroy(instance)
        return Response(status=status.HTTP_204_NO_CONTENT)

    def perform_destroy(self, instance):
        instance.delete()

    def update(self, request, *args, **kwargs):
        instance = self.get_object()
        # Oldingi rasm faylini o'chirish
        if 'save_image' in request.data and not request.data['save_image']:
            if instance.save_image:
                if os.path.isfile(instance.save_image.path):
                    os.remove(instance.save_image.path)
                instance.save_image = None

        serializer = self.get_serializer(instance, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)

        return Response(serializer.data)

    def perform_update(self, serializer):
        serializer.save()


class ShablonServicesAPIViewSet(ModelViewSet):
    queryset = ShablonServices.objects.all()
    serializer_class = ShablonServicesSerializer
    permission_classes = [AllowAny, IsCustomUsersGet]
    throttle_classes = [CustomUserThrottle, ]



class BranchesAPIViewSet(ModelViewSet):
    queryset = Branches.objects.all()
    serializer_class = BranchesSerializer
    permission_classes = [AllowAny, IsCustomUsersGet]
    throttle_classes = [CustomUserThrottle, ]

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        if instance.save_image:
            if os.path.isfile(instance.save_image.path):
                os.remove(instance.save_image.path)
        self.perform_destroy(instance)
        return Response(status=status.HTTP_204_NO_CONTENT)

    def perform_destroy(self, instance):
        instance.delete()

    def update(self, request, *args, **kwargs):
        instance = self.get_object()
        # Oldingi rasm faylini o'chirish
        if 'save_image' in request.data and not request.data['save_image']:
            if instance.save_image:
                if os.path.isfile(instance.save_image.path):
                    os.remove(instance.save_image.path)
                instance.save_image = None

        serializer = self.get_serializer(instance, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)

        return Response(serializer.data)

    def perform_update(self, serializer):
        serializer.save()
    """
    servise yani usluga qo'shib o'chirish uchun kerak bo'lgan actionlar
    """
    @action(detail=True, methods=['post'])
    def postal_service(self, request, *args, **kwargs):
        branch = self.get_object()
        serializer = ShablonServicesSerializer(data=request.data)
        if serializer.is_valid():
            postal_service = serializer.save()
            branch.postal_service.add(postal_service)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @postal_service.mapping.put
    def update_postal_service(self, request, *args, **kwargs):
        id = request.data.get('id')
        if type(id) != int or id is None:
            return Response(data="Try to enter the correct id", status=status.HTTP_400_BAD_REQUEST)
        branch = self.get_object()
        postal_service = branch.postal_service.filter(id=id).first()
        if postal_service is None:
            return Response(data="postal service not found", status=status.HTTP_404_NOT_FOUND)
        serializer = ShablonServicesSerializer(postal_service, data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            user.save()
            return Response(data=serializer.data, status=status.HTTP_200_OK)
        return Response(status=status.HTTP_400_BAD_REQUEST, data=serializer.errors)

    @postal_service.mapping.delete
    def delete_postal_service(self, request, *args, **kwargs):
        branch = self.get_object()
        id = request.data.get('id')
        if type(id) != int:
            return Response(data="You must enter the id as an int type", status=status.HTTP_400_BAD_REQUEST)
        data = branch.postal_service.filter(id=id)
        if not data:
            return Response(data="No such postal service", status=status.HTTP_404_NOT_FOUND)
        branch.postal_service.remove(data.first())
        shablon_service = ShablonServices.objects.get(id=id)
        shablon_service.delete()
        return Response(data="successful deleted", status=status.HTTP_204_NO_CONTENT)
    #
    #
    #

    @action(detail=True, methods=['post'])
    def kurier_services(self, request, *args, **kwargs):
        branch = self.get_object()
        serializer = ShablonServicesSerializer(data=request.data)
        if serializer.is_valid():
            postal_service = serializer.save()
            branch.kurier_services.add(postal_service)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @kurier_services.mapping.put
    def update_kurier_service(self, request, *args, **kwargs):
        id = request.data.get('id')
        if type(id) != int or id is None:
            return Response(data="Try to enter the correct id", status=status.HTTP_400_BAD_REQUEST)
        branch = self.get_object()
        kurier_service = branch.kurier_services.filter(id=id).first()
        if kurier_service is None:
            return Response(data="kurier usluga not found", status=status.HTTP_404_NOT_FOUND)
        serializer = ShablonServicesSerializer(kurier_service, data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            user.save()
            return Response(data=serializer.data, status=status.HTTP_200_OK)
        return Response(status=status.HTTP_400_BAD_REQUEST, data=serializer.errors)

    @kurier_services.mapping.delete
    def delete_kurier_service(self, request, *args, **kwargs):
        branch = self.get_object()
        id = request.data.get('id')
        if type(id) != int:
            return Response(data="You must enter the id as an int type", status=status.HTTP_400_BAD_REQUEST)
        data = branch.kurier_services.filter(id=id)
        if not data:
            return Response(data="No such menu element", status=status.HTTP_404_NOT_FOUND)
        branch.kurier_services.remove(data.first())
        shablon_service = ShablonServices.objects.get(id=id)
        shablon_service.delete()
        return Response(data="successful deleted", status=status.HTTP_204_NO_CONTENT)
    #
    #
    #

    @action(detail=True, methods=['post'])
    def additional_services(self, request, *args, **kwargs):
        branch = self.get_object()
        serializer = ShablonServicesSerializer(data=request.data)
        if serializer.is_valid():
            postal_service = serializer.save()
            branch.additional_services.add(postal_service)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @additional_services.mapping.put
    def update_additional_service(self, request, *args, **kwargs):
        id = request.data.get('id')
        if type(id) != int or id is None:
            return Response(data="Try to enter the correct id", status=status.HTTP_400_BAD_REQUEST)
        branch = self.get_object()
        additional_service = branch.additional_services.filter(id=id).first()
        if additional_service is None:
            return Response(data="additional service not found", status=status.HTTP_404_NOT_FOUND)
        serializer = ShablonServicesSerializer(additional_service, data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            user.save()
            return Response(data=serializer.data, status=status.HTTP_200_OK)
        return Response(status=status.HTTP_400_BAD_REQUEST, data=serializer.errors)

    @additional_services.mapping.delete
    def delete_additional_service(self, request, *args, **kwargs):
        branch = self.get_object()
        id = request.data.get('id')
        if type(id) != int:
            return Response(data="You must enter the id as an int type", status=status.HTTP_400_BAD_REQUEST)
        data = branch.additional_services.filter(id=id)
        if not data:
            return Response(data="No such additional services", status=status.HTTP_404_NOT_FOUND)
        branch.additional_services.remove(data.first())
        shablon_service = ShablonServices.objects.get(id=id)
        shablon_service.delete()
        return Response(data="successful deleted", status=status.HTTP_204_NO_CONTENT)

    #
    #
    #
    @action(detail=True, methods=['post'])
    def contractual_services(self, request, *args, **kwargs):
        branch = self.get_object()
        serializer = ShablonServicesSerializer(data=request.data)
        if serializer.is_valid():
            contractual_services = serializer.save()
            branch.contractual_services.add(contractual_services)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @contractual_services.mapping.put
    def update_contractual_service(self, request, *args, **kwargs):
        id = request.data.get('id')
        if type(id) != int or id is None:
            return Response(data="Try to enter the correct id", status=status.HTTP_400_BAD_REQUEST)
        branch = self.get_object()
        contractual_services = branch.contractual_services.filter(id=id).first()
        if contractual_services is None:
            return Response(data="contractual usluga not found", status=status.HTTP_404_NOT_FOUND)
        serializer = ShablonServicesSerializer(contractual_services, data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            user.save()
            return Response(data=serializer.data, status=status.HTTP_200_OK)
        return Response(status=status.HTTP_400_BAD_REQUEST, data=serializer.errors)

    @contractual_services.mapping.delete
    def delete_contractual_service(self, request, *args, **kwargs):
        branch = self.get_object()
        id = request.data.get('id')
        if type(id) != int:
            return Response(data="You must enter the id as an int type", status=status.HTTP_400_BAD_REQUEST)
        data = branch.contractual_services.filter(id=id)
        if not data:
            return Response(data="No such contractual services", status=status.HTTP_404_NOT_FOUND)
        branch.contractual_services.remove(data.first())
        shablon_service = ShablonServices.objects.get(id=id)
        shablon_service.delete()
        return Response(data="successful deleted", status=status.HTTP_204_NO_CONTENT)
    #
    #
    #

    @action(detail=True, methods=['post'])
    def modern_ict_services(self, request, *args, **kwargs):
        branch = self.get_object()
        serializer = ShablonServicesSerializer(data=request.data)
        if serializer.is_valid():
            modern_ict_service = serializer.save()
            branch.modern_ict_services.add(modern_ict_service)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @modern_ict_services.mapping.put
    def update_modern_ict_services(self, request, *args, **kwargs):
        id = request.data.get('id')
        if type(id) != int or id is None:
            return Response(data="Try to enter the correct id", status=status.HTTP_400_BAD_REQUEST)
        branch = self.get_object()
        kurier_service = branch.modern_ict_services.filter(id=id).first()
        if kurier_service is None:
            return Response(data="modern_ict_services not found", status=status.HTTP_404_NOT_FOUND)
        serializer = ShablonServicesSerializer(kurier_service, data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            user.save()
            return Response(data=serializer.data, status=status.HTTP_200_OK)
        return Response(status=status.HTTP_400_BAD_REQUEST, data=serializer.errors)

    @modern_ict_services.mapping.delete
    def delete_modern_ict_services(self, request, *args, **kwargs):
        branch = self.get_object()
        id = request.data.get('id')
        if type(id) != int:
            return Response(data="You must enter the id as an int type", status=status.HTTP_400_BAD_REQUEST)
        data = branch.modern_ict_services.filter(id=id)
        if not data:
            return Response(data="No such modern_ict_services", status=status.HTTP_404_NOT_FOUND)
        branch.modern_ict_services.remove(data.first())
        shablon_service = ShablonServices.objects.get(id=id)
        shablon_service.delete()
        return Response(data="successful deleted", status=status.HTTP_204_NO_CONTENT)


class VacanciesImagesAPIViewSet(ModelViewSet):
    queryset = VacanciesImages.objects.all()
    serializer_class = VacanciesImagesSerializer
    permission_classes = [AllowAny, IsCustomUsersGet]
    throttle_classes = [CustomUserThrottle, ]

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        if instance.save_image:
            if os.path.isfile(instance.save_image.path):
                os.remove(instance.save_image.path)
        self.perform_destroy(instance)
        return Response(status=status.HTTP_204_NO_CONTENT)

    def perform_destroy(self, instance):
        instance.delete()

    def update(self, request, *args, **kwargs):
        instance = self.get_object()
        # Oldingi rasm faylini o'chirish
        if 'save_image' in request.data and not request.data['save_image']:
            if instance.save_image:
                if os.path.isfile(instance.save_image.path):
                    os.remove(instance.save_image.path)
                instance.save_image = None

        serializer = self.get_serializer(instance, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)

        return Response(serializer.data)

    def perform_update(self, serializer):
        serializer.save()


class InternalDocumentsAPIViewSet(ModelViewSet):
    queryset = InternalDocuments.objects.all()
    serializer_class = InternalDocumentsSerializer
    permission_classes = [AllowAny, IsCustomUsersGet]
    throttle_classes = [CustomUserThrottle, ]

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        if instance.save_image:
            if os.path.isfile(instance.save_image.path):
                os.remove(instance.save_image.path)
        self.perform_destroy(instance)
        return Response(status=status.HTTP_204_NO_CONTENT)

    def perform_destroy(self, instance):
        instance.delete()

    def update(self, request, *args, **kwargs):
        instance = self.get_object()
        # Oldingi rasm faylini o'chirish
        if 'save_image' in request.data and not request.data['save_image']:
            if instance.save_image:
                if os.path.isfile(instance.save_image.path):
                    os.remove(instance.save_image.path)
                instance.save_image = None

        serializer = self.get_serializer(instance, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)

        return Response(serializer.data)

    def perform_update(self, serializer):
        serializer.save()


class ThemaQuestionsAPIViewSet(ModelViewSet):
    queryset = ThemaQuestions.objects.all()
    serializer_class = ThemaQuestionsSerializer
    permission_classes = [AllowAny, IsCustomUsersGet]
    throttle_classes = [CustomUserThrottle, ]

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        if instance.save_image:
            if os.path.isfile(instance.save_image.path):
                os.remove(instance.save_image.path)
        self.perform_destroy(instance)
        return Response(status=status.HTTP_204_NO_CONTENT)

    def perform_destroy(self, instance):
        instance.delete()

    def update(self, request, *args, **kwargs):
        instance = self.get_object()
        # Oldingi rasm faylini o'chirish
        if 'save_image' in request.data and not request.data['save_image']:
            if instance.save_image:
                if os.path.isfile(instance.save_image.path):
                    os.remove(instance.save_image.path)
                instance.save_image = None

        serializer = self.get_serializer(instance, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)

        return Response(serializer.data)

    def perform_update(self, serializer):
        serializer.save()


class BusinessPlansCompletedAPIViewSet(ModelViewSet):
    queryset = BusinessPlansCompleted.objects.all()
    serializer_class = BusinessPlansCompletedSerializer
    permission_classes = [AllowAny, IsCustomUsersGet]
    throttle_classes = [CustomUserThrottle, ]

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        if instance.save_image:
            if os.path.isfile(instance.save_image.path):
                os.remove(instance.save_image.path)
        self.perform_destroy(instance)
        return Response(status=status.HTTP_204_NO_CONTENT)

    def perform_destroy(self, instance):
        instance.delete()

    def update(self, request, *args, **kwargs):
        instance = self.get_object()
        # Oldingi rasm faylini o'chirish
        if 'save_image' in request.data and not request.data['save_image']:
            if instance.save_image:
                if os.path.isfile(instance.save_image.path):
                    os.remove(instance.save_image.path)
                instance.save_image = None

        serializer = self.get_serializer(instance, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)

        return Response(serializer.data)

    def perform_update(self, serializer):
        serializer.save()


class AnnualReportsAPIViewSet(ModelViewSet):
    queryset = AnnualReports.objects.all()
    serializer_class = AnnualReportsSerializer
    permission_classes = [AllowAny, IsCustomUsersGet]
    throttle_classes = [CustomUserThrottle, ]

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        if instance.save_image:
            if os.path.isfile(instance.save_image.path):
                os.remove(instance.save_image.path)
        self.perform_destroy(instance)
        return Response(status=status.HTTP_204_NO_CONTENT)

    def perform_destroy(self, instance):
        instance.delete()

    def update(self, request, *args, **kwargs):
        instance = self.get_object()
        # Oldingi rasm faylini o'chirish
        if 'save_image' in request.data and not request.data['save_image']:
            if instance.save_image:
                if os.path.isfile(instance.save_image.path):
                    os.remove(instance.save_image.path)
                instance.save_image = None

        serializer = self.get_serializer(instance, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)

        return Response(serializer.data)

    def perform_update(self, serializer):
        serializer.save()


class DividendsAPIViewSet(ModelViewSet):
    queryset = Dividends.objects.all()
    serializer_class = DividendsSerializer
    permission_classes = [AllowAny, IsCustomUsersGet]
    throttle_classes = [CustomUserThrottle, ]

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        if instance.save_image:
            if os.path.isfile(instance.save_image.path):
                os.remove(instance.save_image.path)
        self.perform_destroy(instance)
        return Response(status=status.HTTP_204_NO_CONTENT)

    def perform_destroy(self, instance):
        instance.delete()

    def update(self, request, *args, **kwargs):
        instance = self.get_object()
        # Oldingi rasm faylini o'chirish
        if 'save_image' in request.data and not request.data['save_image']:
            if instance.save_image:
                if os.path.isfile(instance.save_image.path):
                    os.remove(instance.save_image.path)
                instance.save_image = None

        serializer = self.get_serializer(instance, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)

        return Response(serializer.data)

    def perform_update(self, serializer):
        serializer.save()


class QuarterReportsAPIViewSet(ModelViewSet):
    queryset = QuarterReports.objects.all()
    serializer_class = QuarterReportsSerializer
    permission_classes = [AllowAny, IsCustomUsersGet]
    throttle_classes = [CustomUserThrottle, ]

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        if instance.save_image:
            if os.path.isfile(instance.save_image.path):
                os.remove(instance.save_image.path)
        self.perform_destroy(instance)
        return Response(status=status.HTTP_204_NO_CONTENT)

    def perform_destroy(self, instance):
        instance.delete()

    def update(self, request, *args, **kwargs):
        instance = self.get_object()
        # Oldingi rasm faylini o'chirish
        if 'save_image' in request.data and not request.data['save_image']:
            if instance.save_image:
                if os.path.isfile(instance.save_image.path):
                    os.remove(instance.save_image.path)
                instance.save_image = None

        serializer = self.get_serializer(instance, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)

        return Response(serializer.data)

    def perform_update(self, serializer):
        serializer.save()


class UserInstructionsAPIViewSet(ModelViewSet):
    queryset = UserInstructions.objects.all()
    serializer_class = UserInstructionsSerializer
    permission_classes = [AllowAny, IsCustomUsersGet]
    throttle_classes = [CustomUserThrottle, ]

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        if instance.save_image:
            if os.path.isfile(instance.save_image.path):
                os.remove(instance.save_image.path)
        self.perform_destroy(instance)
        return Response(status=status.HTTP_204_NO_CONTENT)

    def perform_destroy(self, instance):
        instance.delete()

    def update(self, request, *args, **kwargs):
        instance = self.get_object()
        # Oldingi rasm faylini o'chirish
        if 'save_image' in request.data and not request.data['save_image']:
            if instance.save_image:
                if os.path.isfile(instance.save_image.path):
                    os.remove(instance.save_image.path)
                instance.save_image = None

        serializer = self.get_serializer(instance, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)

        return Response(serializer.data)

    def perform_update(self, serializer):
        serializer.save()


class ExecutiveApparatusAPIViewSet(ModelViewSet):
    queryset = ExecutiveApparatus.objects.all()
    serializer_class = ExecutiveApparatusSerializer
    permission_classes = [AllowAny, IsCustomUsersGet]
    throttle_classes = [CustomUserThrottle, ]

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        if instance.save_image:
            if os.path.isfile(instance.save_image.path):
                os.remove(instance.save_image.path)
        self.perform_destroy(instance)
        return Response(status=status.HTTP_204_NO_CONTENT)

    def perform_destroy(self, instance):
        instance.delete()

    def update(self, request, *args, **kwargs):
        instance = self.get_object()
        # Oldingi rasm faylini o'chirish
        if 'save_image' in request.data and not request.data['save_image']:
            if instance.save_image:
                if os.path.isfile(instance.save_image.path):
                    os.remove(instance.save_image.path)
                instance.save_image = None

        serializer = self.get_serializer(instance, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)

        return Response(serializer.data)

    def perform_update(self, serializer):
        serializer.save()


class ShablonUzPostTelNumberAPIViewSet(ModelViewSet):
    queryset = ShablonUzPostTelNumber.objects.all()
    serializer_class = ShablonUzPostTelNumberSerializer
    permission_classes = [AllowAny, IsCustomUsersGet]
    throttle_classes = [CustomUserThrottle, ]


class ShablonContactSpecialTitleAPIViewSet(ModelViewSet):
    queryset = ShablonContactSpecialTitle.objects.all()
    serializer_class = ShablonContactSpecialTitleSerializer
    permission_classes = [AllowAny, IsCustomUsersGet]
    throttle_classes = [CustomUserThrottle, ]


class ContactAPIViewSet(ModelViewSet):
    queryset = Contact.objects.all()
    serializer_class = ContactSerializer
    permission_classes = [AllowAny, IsCustomUsersGet]
    throttle_classes = [CustomUserThrottle, ]

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        if instance.save_image:
            if os.path.isfile(instance.save_image.path):
                os.remove(instance.save_image.path)
        self.perform_destroy(instance)
        return Response(status=status.HTTP_204_NO_CONTENT)

    def perform_destroy(self, instance):
        instance.delete()

    def update(self, request, *args, **kwargs):
        instance = self.get_object()
        # Oldingi rasm faylini o'chirish
        if 'save_image' in request.data and not request.data['save_image']:
            if instance.save_image:
                if os.path.isfile(instance.save_image.path):
                    os.remove(instance.save_image.path)
                instance.save_image = None

        serializer = self.get_serializer(instance, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)

        return Response(serializer.data)

    def perform_update(self, serializer):
        serializer.save()
    """
    contact uchun shablonlar many to many actions
    """
    @action(detail=True, methods=['post'])
    def tel_number(self, request, *args, **kwargs):
        contact = self.get_object()
        serializer = ShablonUzPostTelNumberSerializer(data=request.data)
        if serializer.is_valid():
            tel_number = serializer.save()
            contact.tel_number.add(tel_number)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @tel_number.mapping.put
    def update_tel_number(self, request, *args, **kwargs):
        id = request.data.get('id')
        if type(id) != int or id is None:
            return Response(data="Try to enter the correct id", status=status.HTTP_400_BAD_REQUEST)
        contact = self.get_object()
        tel_number = contact.tel_number.filter(id=id).first()
        if tel_number is None:
            return Response(data="tel number not found", status=status.HTTP_404_NOT_FOUND)
        serializer = ShablonUzPostTelNumberSerializer(tel_number, data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            user.save()
            return Response(data=serializer.data, status=status.HTTP_200_OK)
        return Response(status=status.HTTP_400_BAD_REQUEST, data=serializer.errors)

    @tel_number.mapping.delete
    def delete_tel_number(self, request, *args, **kwargs):
        contact = self.get_object()
        id = request.data.get('id')
        if type(id) != int:
            return Response(data="You must enter the id as an int type", status=status.HTTP_400_BAD_REQUEST)
        data = contact.tel_number.filter(id=id)
        if not data:
            return Response(data="No such tel number", status=status.HTTP_404_NOT_FOUND)
        contact.tel_number.remove(data.first())
        shablon_tel_number = ShablonUzPostTelNumber.objects.get(id=id)
        shablon_tel_number.delete()
        return Response(data="successful deleted", status=status.HTTP_204_NO_CONTENT)
    #
    #
    #

    @action(detail=True, methods=['post'])
    def title_2(self, request, *args, **kwargs):
        contact = self.get_object()
        serializer = ShablonContactSpecialTitleSerializer(data=request.data)
        if serializer.is_valid():
            title_2 = serializer.save()
            contact.title_2.add(title_2)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @title_2.mapping.put
    def update_title_2(self, request, *args, **kwargs):
        id = request.data.get('id')
        if type(id) != int or id is None:
            return Response(data="Try to enter the correct id", status=status.HTTP_400_BAD_REQUEST)
        contact = self.get_object()
        title_2 = contact.title_2.filter(id=id).first()
        if title_2 is None:
            return Response(data="title_2 not found", status=status.HTTP_404_NOT_FOUND)
        serializer = ShablonContactSpecialTitleSerializer(title_2, data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            user.save()
            return Response(data=serializer.data, status=status.HTTP_200_OK)
        return Response(status=status.HTTP_400_BAD_REQUEST, data=serializer.errors)

    @title_2.mapping.delete
    def delete_title_2(self, request, *args, **kwargs):
        contact = self.get_object()
        id = request.data.get('id')
        if type(id) != int:
            return Response(data="You must enter the id as an int type", status=status.HTTP_400_BAD_REQUEST)
        data = contact.title_2.filter(id=id)
        if not data:
            return Response(data="No such title_2", status=status.HTTP_404_NOT_FOUND)
        contact.title_2.remove(data.first())
        shablon_title_2 = ShablonContactSpecialTitle.objects.get(id=id)
        shablon_title_2.delete()
        return Response(data="successful deleted", status=status.HTTP_204_NO_CONTENT)

    #
    #
    #

    @action(detail=True, methods=['post'])
    def description_2(self, request, *args, **kwargs):
        contact = self.get_object()
        serializer = ShablonContactSpecialTitleSerializer(data=request.data)
        if serializer.is_valid():
            description_2 = serializer.save()
            contact.description_2.add(description_2)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @description_2.mapping.put
    def update_description_2(self, request, *args, **kwargs):
        id = request.data.get('id')
        if type(id) != int or id is None:
            return Response(data="Try to enter the correct id", status=status.HTTP_400_BAD_REQUEST)
        contact = self.get_object()
        description_2 = contact.description_2.filter(id=id).first()
        if description_2 is None:
            return Response(data="description_2 not found", status=status.HTTP_404_NOT_FOUND)
        serializer = ShablonContactSpecialTitleSerializer(description_2, data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            user.save()
            return Response(data=serializer.data, status=status.HTTP_200_OK)
        return Response(status=status.HTTP_400_BAD_REQUEST, data=serializer.errors)

    @description_2.mapping.delete
    def delete_description_2(self, request, *args, **kwargs):
        contact = self.get_object()
        id = request.data.get('id')
        if type(id) != int:
            return Response(data="You must enter the id as an int type", status=status.HTTP_400_BAD_REQUEST)
        data = contact.description_2.filter(id=id)
        if not data:
            return Response(data="No such description_2", status=status.HTTP_404_NOT_FOUND)
        contact.description_2.remove(data.first())
        shablon_description_2 = ShablonContactSpecialTitle.objects.get(id=id)
        shablon_description_2.delete()
        return Response(data="successful deleted", status=status.HTTP_204_NO_CONTENT)


class AdvertisementsAPIViewSet(ModelViewSet):
    queryset = Advertisements.objects.all()
    serializer_class = AdvertisementsSerializer
    permission_classes = [AllowAny, IsCustomUsersGet]
    throttle_classes = [CustomUserThrottle, ]

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        if instance.save_image:
            if os.path.isfile(instance.save_image.path):
                os.remove(instance.save_image.path)
        self.perform_destroy(instance)
        return Response(status=status.HTTP_204_NO_CONTENT)

    def perform_destroy(self, instance):
        instance.delete()

    def update(self, request, *args, **kwargs):
        instance = self.get_object()
        # Oldingi rasm faylini o'chirish
        if 'save_image' in request.data and not request.data['save_image']:
            if instance.save_image:
                if os.path.isfile(instance.save_image.path):
                    os.remove(instance.save_image.path)
                instance.save_image = None

        serializer = self.get_serializer(instance, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)

        return Response(serializer.data)

    def perform_update(self, serializer):
        serializer.save()


class OrganicManagementsAPIViewSet(ModelViewSet):
    queryset = OrganicManagements.objects.all()
    serializer_class = OrganicManagementsSerializer
    permission_classes = [AllowAny, IsCustomUsersGet]
    throttle_classes = [CustomUserThrottle, ]

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        if instance.save_image:
            if os.path.isfile(instance.save_image.path):
                os.remove(instance.save_image.path)
        self.perform_destroy(instance)
        return Response(status=status.HTTP_204_NO_CONTENT)

    def perform_destroy(self, instance):
        instance.delete()

    def update(self, request, *args, **kwargs):
        instance = self.get_object()
        # Oldingi rasm faylini o'chirish
        if 'save_image' in request.data and not request.data['save_image']:
            if instance.save_image:
                if os.path.isfile(instance.save_image.path):
                    os.remove(instance.save_image.path)
                instance.save_image = None

        serializer = self.get_serializer(instance, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)

        return Response(serializer.data)

    def perform_update(self, serializer):
        serializer.save()


class PartnersAPIViewSet(ModelViewSet):
    queryset = Partners.objects.all()
    serializer_class = PartnersSerializer
    permission_classes = [AllowAny, IsCustomUsersGet]
    throttle_classes = [CustomUserThrottle, ]

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        if instance.save_image:
            if os.path.isfile(instance.save_image.path):
                os.remove(instance.save_image.path)
        self.perform_destroy(instance)
        return Response(status=status.HTTP_204_NO_CONTENT)

    def perform_destroy(self, instance):
        instance.delete()

    def update(self, request, *args, **kwargs):
        instance = self.get_object()
        # Oldingi rasm faylini o'chirish
        if 'save_image' in request.data and not request.data['save_image']:
            if instance.save_image:
                if os.path.isfile(instance.save_image.path):
                    os.remove(instance.save_image.path)
                instance.save_image = None

        serializer = self.get_serializer(instance, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)

        return Response(serializer.data)

    def perform_update(self, serializer):
        serializer.save()


class RegionalBranchesAPIViewSet(ModelViewSet):
    queryset = RegionalBranches.objects.all()
    serializer_class = RegionalBranchesSerializer
    permission_classes = [AllowAny, IsCustomUsersGet]
    throttle_classes = [CustomUserThrottle, ]

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        if instance.save_image:
            if os.path.isfile(instance.save_image.path):
                os.remove(instance.save_image.path)
        self.perform_destroy(instance)
        return Response(status=status.HTTP_204_NO_CONTENT)

    def perform_destroy(self, instance):
        instance.delete()

    def update(self, request, *args, **kwargs):
        instance = self.get_object()
        # Oldingi rasm faylini o'chirish
        if 'save_image' in request.data and not request.data['save_image']:
            if instance.save_image:
                if os.path.isfile(instance.save_image.path):
                    os.remove(instance.save_image.path)
                instance.save_image = None

        serializer = self.get_serializer(instance, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)

        return Response(serializer.data)

    def perform_update(self, serializer):
        serializer.save()


class AdvertisingAPIViewSet(ModelViewSet):
    queryset = Advertising.objects.all()
    serializer_class = AdvertisingSerializer
    permission_classes = [AllowAny, IsCustomUsersGet]
    throttle_classes = [CustomUserThrottle, ]

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        if instance.save_image:
            if os.path.isfile(instance.save_image.path):
                os.remove(instance.save_image.path)
        self.perform_destroy(instance)
        return Response(status=status.HTTP_204_NO_CONTENT)

    def perform_destroy(self, instance):
        instance.delete()

    def update(self, request, *args, **kwargs):
        instance = self.get_object()
        # Oldingi rasm faylini o'chirish
        if 'save_image' in request.data and not request.data['save_image']:
            if instance.save_image:
                if os.path.isfile(instance.save_image.path):
                    os.remove(instance.save_image.path)
                instance.save_image = None

        serializer = self.get_serializer(instance, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)

        return Response(serializer.data)

    def perform_update(self, serializer):
        serializer.save()


class InformationAboutIssuerAPIViewSet(ModelViewSet):
    queryset = InformationAboutIssuer.objects.all()
    serializer_class = InformationAboutIssuerSerializer
    permission_classes = [AllowAny, IsCustomUsersGet]
    throttle_classes = [CustomUserThrottle, ]

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        if instance.save_image:
            if os.path.isfile(instance.save_image.path):
                os.remove(instance.save_image.path)
        self.perform_destroy(instance)
        return Response(status=status.HTTP_204_NO_CONTENT)

    def perform_destroy(self, instance):
        instance.delete()

    def update(self, request, *args, **kwargs):
        instance = self.get_object()
        # Oldingi rasm faylini o'chirish
        if 'save_image' in request.data and not request.data['save_image']:
            if instance.save_image:
                if os.path.isfile(instance.save_image.path):
                    os.remove(instance.save_image.path)
                instance.save_image = None

        serializer = self.get_serializer(instance, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)

        return Response(serializer.data)

    def perform_update(self, serializer):
        serializer.save()


class SlidesAPIViewSet(ModelViewSet):
    queryset = Slides.objects.all()
    serializer_class = SlidesSerializer
    permission_classes = [AllowAny, IsCustomUsersGet]
    throttle_classes = [CustomUserThrottle, ]

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        if instance.save_image:
            if os.path.isfile(instance.save_image.path):
                os.remove(instance.save_image.path)
        self.perform_destroy(instance)
        return Response(status=status.HTTP_204_NO_CONTENT)

    def perform_destroy(self, instance):
        instance.delete()

    def update(self, request, *args, **kwargs):
        instance = self.get_object()
        # Oldingi rasm faylini o'chirish
        if 'save_image' in request.data and not request.data['save_image']:
            if instance.save_image:
                if os.path.isfile(instance.save_image.path):
                    os.remove(instance.save_image.path)
                instance.save_image = None

        serializer = self.get_serializer(instance, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)

        return Response(serializer.data)

    def perform_update(self, serializer):
        serializer.save()


class SocialMediaAPIViewSet(ModelViewSet):
    queryset = SocialMedia.objects.all()
    serializer_class = SocialMediaSerializer
    permission_classes = [AllowAny, IsCustomUsersGet]
    throttle_classes = [CustomUserThrottle, ]

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        if instance.save_image:
            if os.path.isfile(instance.save_image.path):
                os.remove(instance.save_image.path)
        self.perform_destroy(instance)
        return Response(status=status.HTTP_204_NO_CONTENT)

    def perform_destroy(self, instance):
        instance.delete()

    def update(self, request, *args, **kwargs):
        instance = self.get_object()
        # Oldingi rasm faylini o'chirish
        if 'save_image' in request.data and not request.data['save_image']:
            if instance.save_image:
                if os.path.isfile(instance.save_image.path):
                    os.remove(instance.save_image.path)
                instance.save_image = None

        serializer = self.get_serializer(instance, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)

        return Response(serializer.data)

    def perform_update(self, serializer):
        serializer.save()


class EssentialFactsAPIViewSet(ModelViewSet):
    queryset = EssentialFacts.objects.all()
    serializer_class = EssentialFactsSerializer
    permission_classes = [AllowAny, IsCustomUsersGet]
    throttle_classes = [CustomUserThrottle, ]

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        if instance.save_image:
            if os.path.isfile(instance.save_image.path):
                os.remove(instance.save_image.path)
        self.perform_destroy(instance)
        return Response(status=status.HTTP_204_NO_CONTENT)

    def perform_destroy(self, instance):
        instance.delete()

    def update(self, request, *args, **kwargs):
        instance = self.get_object()
        # Oldingi rasm faylini o'chirish
        if 'save_image' in request.data and not request.data['save_image']:
            if instance.save_image:
                if os.path.isfile(instance.save_image.path):
                    os.remove(instance.save_image.path)
                instance.save_image = None

        serializer = self.get_serializer(instance, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)

        return Response(serializer.data)

    def perform_update(self, serializer):
        serializer.save()


class RatesAPIViewSet(ModelViewSet):
    queryset = Rates.objects.all()
    serializer_class = RatesSerializer
    permission_classes = [AllowAny, IsCustomUsersGet]
    throttle_classes = [CustomUserThrottle, ]

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        if instance.save_image:
            if os.path.isfile(instance.save_image.path):
                os.remove(instance.save_image.path)
        self.perform_destroy(instance)
        return Response(status=status.HTTP_204_NO_CONTENT)

    def perform_destroy(self, instance):
        instance.delete()

    def update(self, request, *args, **kwargs):
        instance = self.get_object()
        # Oldingi rasm faylini o'chirish
        if 'save_image' in request.data and not request.data['save_image']:
            if instance.save_image:
                if os.path.isfile(instance.save_image.path):
                    os.remove(instance.save_image.path)
                instance.save_image = None

        serializer = self.get_serializer(instance, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)

        return Response(serializer.data)

    def perform_update(self, serializer):
        serializer.save()


class ServicesAPIViewSet(ModelViewSet):
    queryset = Services.objects.all()
    serializer_class = ServicesSerializer
    permission_classes = [AllowAny, IsCustomUsersGet]
    throttle_classes = [CustomUserThrottle, ]

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        if instance.save_image:
            if os.path.isfile(instance.save_image.path):
                os.remove(instance.save_image.path)
        self.perform_destroy(instance)
        return Response(status=status.HTTP_204_NO_CONTENT)

    def perform_destroy(self, instance):
        instance.delete()

    def update(self, request, *args, **kwargs):
        instance = self.get_object()
        # Oldingi rasm faylini o'chirish
        if 'save_image' in request.data and not request.data['save_image']:
            if instance.save_image:
                if os.path.isfile(instance.save_image.path):
                    os.remove(instance.save_image.path)
                instance.save_image = None

        serializer = self.get_serializer(instance, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)

        return Response(serializer.data)

    def perform_update(self, serializer):
        serializer.save()


class CategoryServicesAPIViewSet(ModelViewSet):
    queryset = CategoryServices.objects.all()
    serializer_class = CategoryServicesSerializer
    permission_classes = [AllowAny, IsCustomUsersGet]
    throttle_classes = [CustomUserThrottle, ]

    @action(detail=True, methods=['post'])
    def services_id(self, request, *args, **kwargs):
        category = self.get_object()
        serializer = CategoryServicesSerializer(data=request.data)
        if serializer.is_valid():
            services = serializer.save()
            category.services_id.add(services)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @services_id.mapping.put
    def update_services(self, request, *args, **kwargs):
        id = request.data.get('id')
        if type(id) != int or id is None:
            return Response(data="Try to enter the correct id", status=status.HTTP_400_BAD_REQUEST)
        category = self.get_object()
        services = category.services_id.filter(id=id).first()
        if services is None:
            return Response(data="tel number not found", status=status.HTTP_404_NOT_FOUND)
        serializer = CategoryServicesSerializer(services, data=request.data)
        if serializer.is_valid():
            aka = serializer.save()
            aka.save()
            return Response(data=serializer.data, status=status.HTTP_200_OK)
        return Response(status=status.HTTP_400_BAD_REQUEST, data=serializer.errors)


    @services_id.mapping.delete
    def delete_services(self, request, *args, **kwargs):
        category = self.get_object()
        id = request.data.get('id')
        if type(id) != int or id is None:
            return Response(data="You must enter the id as an int type", status=status.HTTP_400_BAD_REQUEST)
        data = category.services_id.filter(id=id)
        if not data:
            return Response(data="No such description_2", status=status.HTTP_404_NOT_FOUND)
        category.services_id.remove(data.first())
        services = Services.objects.get(id=id)
        services.delete()
        return Response(data="successful deleted", status=status.HTTP_204_NO_CONTENT)


class CharterSocietyAPIViewSet(ModelViewSet):
    queryset = CharterSociety.objects.all()
    serializer_class = CharterSocietySerializer
    permission_classes = [AllowAny, IsCustomUsersGet]
    throttle_classes = [CustomUserThrottle, ]

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        if instance.save_image:
            if os.path.isfile(instance.save_image.path):
                os.remove(instance.save_image.path)
        self.perform_destroy(instance)
        return Response(status=status.HTTP_204_NO_CONTENT)

    def perform_destroy(self, instance):
        instance.delete()

    def update(self, request, *args, **kwargs):
        instance = self.get_object()
        # Oldingi rasm faylini o'chirish
        if 'save_image' in request.data and not request.data['save_image']:
            if instance.save_image:
                if os.path.isfile(instance.save_image.path):
                    os.remove(instance.save_image.path)
                instance.save_image = None

        serializer = self.get_serializer(instance, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)

        return Response(serializer.data)

    def perform_update(self, serializer):
        serializer.save()


class SecurityPapersAPIViewSet(ModelViewSet):
    queryset = SecurityPapers.objects.all()
    serializer_class = SecurityPapersSerializer
    permission_classes = [AllowAny, IsCustomUsersGet]
    throttle_classes = [CustomUserThrottle, ]

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        if instance.save_image:
            if os.path.isfile(instance.save_image.path):
                os.remove(instance.save_image.path)
        self.perform_destroy(instance)
        return Response(status=status.HTTP_204_NO_CONTENT)

    def perform_destroy(self, instance):
        instance.delete()

    def update(self, request, *args, **kwargs):
        instance = self.get_object()
        # Oldingi rasm faylini o'chirish
        if 'save_image' in request.data and not request.data['save_image']:
            if instance.save_image:
                if os.path.isfile(instance.save_image.path):
                    os.remove(instance.save_image.path)
                instance.save_image = None

        serializer = self.get_serializer(instance, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)

        return Response(serializer.data)

    def perform_update(self, serializer):
        serializer.save()


class FAQAPIViewSet(ModelViewSet):
    queryset = FAQ.objects.all()
    serializer_class = FAQSerializer
    permission_classes = [AllowAny, IsCustomUsersGet]
    throttle_classes = [CustomUserThrottle, ]

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        if instance.save_image:
            if os.path.isfile(instance.save_image.path):
                os.remove(instance.save_image.path)
        self.perform_destroy(instance)
        return Response(status=status.HTTP_204_NO_CONTENT)

    def perform_destroy(self, instance):
        instance.delete()

    def update(self, request, *args, **kwargs):
        instance = self.get_object()
        # Oldingi rasm faylini o'chirish
        if 'save_image' in request.data and not request.data['save_image']:
            if instance.save_image:
                if os.path.isfile(instance.save_image.path):
                    os.remove(instance.save_image.path)
                instance.save_image = None

        serializer = self.get_serializer(instance, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)

        return Response(serializer.data)

    def perform_update(self, serializer):
        serializer.save()


class CategoryFAQAPIViewSet(ModelViewSet):
    queryset = CategoryFaq.objects.all()
    serializer_class = CategoryFAQSerializer
    permission_classes = [AllowAny, IsCustomUsersGet]
    throttle_classes = [CustomUserThrottle, ]


class SiteSettingsAPIViewSet(ModelViewSet):
    queryset = SiteSettings.objects.all()
    serializer_class = SiteSettingsSerializer
    permission_classes = [AllowAny, IsCustomUsersGet]
    throttle_classes = [CustomUserThrottle, ]

