import os
from django.conf import settings
from django.http import HttpResponse, Http404
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404
from django.views.decorators.cache import cache_page
from django.utils.decorators import method_decorator
from zeep import Client
from zeep.helpers import serialize_object
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated, IsAdminUser, AllowAny, BasePermission
from rest_framework import status, filters
from django.db.transaction import atomic
from rest_framework.response import Response
from rest_framework.throttling import UserRateThrottle
import requests
from requests.exceptions import JSONDecodeError, RequestException
from requests.exceptions import ConnectTimeout, RequestException
import copy
import json
from datetime import datetime, timedelta
from concurrent.futures import ThreadPoolExecutor
from requests.adapters import HTTPAdapter
from requests.packages.urllib3.util.retry import Retry



class IsCustomUsersGet(BasePermission):
    def has_permission(self, request, view):
        if request.method in ('GET', 'OPTIONS'):
            return True
        return False


class SafeJSONEncoder(json.JSONEncoder):
    def default(self, obj):
        try:
            return super().default(obj)
        except TypeError:
            return str(obj)


@method_decorator(cache_page(60 * 10), name='dispatch')
class Barcode(APIView):
    permission_classes = [AllowAny]
    throttle_classes = [UserRateThrottle]

    def get(self, request, barcode):
        try:
            if (barcode[:2] == "RZ" or barcode[:2] == "CZ" or barcode[:1] == "E") and barcode[:3] != "EHM" and barcode[
                                                                                                               :3] != "EMI":
                wsdl = 'http://10.100.0.69/IPSAPIService/TrackAndTraceService.svc?singleWsdl'
                client = Client(wsdl=wsdl)
                ids = barcode
                token = '269a208f-7006-4dc6-b52f-6dfba6af113a'
                response = client.service.GetMailitems(ids=ids, token=token)
                response_data = serialize_object(response)

                if response_data is None:
                    return Response({"code": "order_not_found", "message": "Order Not Found", "status": "error"},
                                    status=status.HTTP_404_NOT_FOUND)

                if response_data[0].get("InfoFromEdi"):
                    for event in response_data[0]["InfoFromEdi"]["TMailitemInfoFromEDI"][0]["Events"][
                        "TMailitemEventEDI"]:
                        event["ReceivedDispatch"] = None

                if response_data[0].get("OperationalMailitems"):
                    for event in response_data[0]["OperationalMailitems"]["TMailitemInfoFromScanning"][0]["Events"][
                        "TMailitemEventScanning"]:
                        event["ReceivedDispatch"] = None

                return Response(json.loads(json.dumps(response_data, cls=SafeJSONEncoder)), status=status.HTTP_200_OK)

            data = requests.get(f"https://prodapi.pochta.uz/api/v1/public/order/{barcode}").json()
            if data.get('status') != "success":
                return Response(data=data, status=status.HTTP_404_NOT_FOUND)

            total_data_2 = {'header': data}
            if barcode[:2] != 'SX' and data["data"]['locations'][0]['country']['code'] == 'UZ' and \
                    data["data"]['locations'][1]['country']['code'] == 'UZ':
                total_data = requests.get(
                    f"https://prodapi.pochta.uz/api/v1/public/order/{barcode}/history_items").json()
                total_data_2['shipox'] = total_data
                total_data_2['gdeposilka'] = None
                return Response(json.loads(json.dumps(total_data_2, cls=SafeJSONEncoder)), status=status.HTTP_200_OK)


            # url1 = f"https://gdeposylka.ru/api/v4/tracker/detect/{barcode}"
            # headers = {
            #     "X-Authorization-Token": "65bbbac85f796f8032e0874411f4d1f5af7185a99e184709bf0c1f38d95486fa2338733760a48704"}
            # response1 = requests.get(url1, headers=headers).json()
            # shipox = requests.get(f"https://prodapi.pochta.uz/api/v1/public/order/{barcode}/history_items").json()
            # total_data_2['shipox'] = shipox
            #
            # url2 = f"https://gdeposylka.ru{response1['data'][0]['tracker_url']}"
            # response_x = requests.get(url2, headers=headers)
            # response2 = requests.get(url2, headers=headers).json()
            #
            # if not response2.get("messages") and response_x.status_code == 200:
            #     gdeposylka = {
            #         "result": response2['result'],
            #         'data': {k: response2['data'][k] for k in [
            #             'id', 'tracking_number', 'tracking_number_secondary',
            #             'tracking_number_current', 'courier', 'is_active', 'is_delivered',
            #             'last_check', 'extra']},
            #         'checkpoints': [cp for cp in response2['data']['checkpoints'] if
            #                         cp['courier']['slug'] != 'ozbekiston-pochtasi']
            #     }
            #     total_data_2['gdeposilka'] = gdeposylka
            #     return Response(json.loads(json.dumps(total_data_2, cls=SafeJSONEncoder)), status=status.HTTP_200_OK)
            # else:
            #     time.sleep(15)
            #     response2 = requests.get(url2, headers=headers).json()
            #     if not response2.get("messages"):
            #         gdeposylka = {
            #             "result": response2['result'],
            #             'data': {k: response2['data'][k] for k in [
            #                 'id', 'tracking_number', 'tracking_number_secondary',
            #                 'tracking_number_current', 'courier', 'is_active', 'is_delivered',
            #                 'last_check', 'extra']},
            #             'checkpoints': [cp for cp in response2['data']['checkpoints'] if
            #                             cp['courier']['slug'] != 'ozbekiston-pochtasi']
            #         }
            #         total_data_2['gdeposilka'] = gdeposylka
            #     else:
            #         total_data_2['gdeposilka'] = "please try again we are processing the data"
            total_data_2['gdeposilka'] = "Not Found data"
            return Response(json.loads(json.dumps(total_data_2, cls=SafeJSONEncoder)), status=status.HTTP_200_OK)

        except Exception as e:
            return Response({"error": "Internal Server Error", "details": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


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
        "username": "31409911170011",
        "password": "Admin1234",
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


track_translate = {
    "shipox": {
        "unassigned": {
            "uz": "Jo'natma yaratildi",
            "ru": "Создано отправление",
            "eng": "New order"
        },
        "in_transit": {
            "uz": "Yo'lda",
            "ru": "В пути",
            "eng": "In Transit"
        },
        "in_sorting_facility": {
            "uz": "Saralash jarayonida",
            "ru": "В процессе сортировки",
            "eng": "In sorting warehouse"
        },
        "dispatched": {
            "uz": "Yuborilgan",
            "ru": "Отправлен",
            "eng": "Dispatched"
        },
        "out_for_delivery": {
            "uz": "Yuborilgan",
            "ru": "Отправлен",
            "eng": "Out for delivery"
        },
        "completed": {
            "uz": "Yetkazib berilgan",
            "ru": "Завершено",
            "eng": "Completed"
        },
        "issued_to_recipient": {
            "uz": "Qabul qiluvchiga berilgan",
            "ru": "Выдан получателю",
            "eng": "Issued to recipient"
        },
        "ready_for_delivery": {
            "uz": "Jo'natish uchun tayyor",
            "ru": "Готов к доставке",
            "eng": "Ready for delivery"
        },
        "try_perform": {
            "uz": "Yetkazib berishga urinib ko'rildi",
            "ru": "Попытка вручения",
            "eng": "Try perform"
        }
    },
    "shipox_comment": {
        "receiver_dead": {
            "uz": "Qabul qiluvchi vafot etgan",
            "ru": "Адресат скончался",
            "eng": "Reciever is dead"
        },
        "receiver_not_lives_there": {
            "uz": "Qabul qiluvchi bu manzilda yashamaydi",
            "ru": "Адресат не проживает по указанному адресу"
        },
        "incomplete_address": {
            "uz": "Manzil to'liq emas",
            "ru": "Адрес не полный",
            "eng": "Incomplete address"
        },
        "receiver_refuse": {
            "uz": "Qabul qilish rad etildi",
            "ru": "Адресат от получения отказался",
            "eng": "Reciever  refused"
        },
        "not_at_home": {
            "uz": "Uyda hech kim yo'q",
            "ru": "Нет дома",
            "eng": "Not at home"
        },
        "didnt_appear_on_notice": {
            "uz": "Bildirishnoma bo'yicha xabar olinmadi",
            "ru": "Адресат не явился по уведомлению",
            "eng": "Didnt appear on notice"
        },
        "defect": {
            "uz": "Qabul qiluvchi manzili to'liq kiritilmagan",
            "ru": "Адрес не определен",
            "eng": "Defect"
        },
        "organization_with_given_address_not_found": {
            "uz": "Berilgan ma'lumot bo'yicha bunaqa tashkilot topilmadi",
            "ru": "По указанному адресу организация не найдена",
            "eng": "Organization with given address not found"
        },
        "retention_period_has_expired": {
            "uz": "Saqlash muddati tugagan",
            "ru": "Срок хранения истек",
            "eng": "Retention period has expired"
        }
    },
    "gdeposilka": {
        "Посылка принята": {
            "uz": "Yangi jo'natma",
            "ru": "Новая отправления",
            "eng": "New order"
        },
        "В пути - Покинула промежуточный пункт": {
            "uz": "Tranzitda",
            "ru": "Транзит",
            "eng": "In Transit"
        },
        "Покинула таможню": {
            "uz": "Bojxonadan qaytdi",
            "ru": "Выпущено из таможни",
            "eng": "Returned from customs"
        },
        "Прибыла на таможню": {
            "uz": "Bojxonaga yuborildi",
            "ru": "Отправлено на таможню",
            "eng": "Sent to customs"
        }
    },
    "ips": {
        "Arrived item at office of exchange": {
            "uz": "Ayirboshlash punktida qabul qilindi",
            "ru":  "Принято в пункте обмена"
        },
        "Send item to customs": {
            "uz": " Bojxonaga jo'natildi",
            "ru": "Отправлено на таможню"
        },
        "Return item from customs": {
            "uz": "Bojxonadan chiqarildi",
            "ru": " Выпущено из таможни"
        },
        "Send item to domestic location": {
            "uz": "Mahalliy punktga yuborildi",
            "ru": "Отправлено в местный пункт"
        },
        "Record item customs information": {
            "uz": "Bojxona ma'lumotlari ro'yxatga olinmoqda",
            "ru": "Осуществляется запись таможенной информации"
        },
        "Ready for Delivery": {
            "uz": "Yetkazib berishga tayyor",
            "ru": " Готово к доставке"
        },
        "Receive item at delivery office": {
            "uz": "Yetkazib berish bo'limiga yuborildi",
            "ru": "Отправлено в отделение доставки"
        },
        "Receive item at regional distribution hub": {
            "uz": "Hududiy taqsimlash markaziga qabul qilindi",
            "ru": "Принято в региональном распределительном центре"
        },
        "Out for delivery": {
            "uz": "Yetkazib berish jarayonida",
            "ru": "В процессе доставки"
        },
        "Sent item from distribution hub": {
            "uz": "Taqsimlash markazidan jo'natildi",
            "ru": "Отправлено с распределительного центра"
        },
        "Unsuccessful item delivery attempt": {
            "uz": "Muvaffaqiyatsiz yetkazib berish",
            "ru": "Неудачная попытка доставки"
        },
        "Deliver item": {
            "uz": "Jo'natmani yetkazib berildi",
            "ru": "Доставка отправления"
        },
        "On the way to sender": {
            "uz": "Jo'natuvchi shaxs tomon yo'lda",
            "ru": "В пути к отправителю"
        },
        "Delivered to sender": {
            "uz": "Jo'natuvchi shaxsga yetkazildi",
            "ru": "Доставлено отправителю"
        },
        "Stop item import": {
            "uz": "Jo'natma importi to'xtatildi",
            "ru": "Остановка импорта отправления"
        },
        "Unsuccessful item delivery attempt - Customer request pickup": {
            "uz": "Mahsulotni yetkazib berishga muvaffaqiyatsiz urinish - Mijoz mahsulotni olib ketishni so‘radi",
            "ru": "Неудачная попытка доставки товара - Клиент просит забрать товар"
        },
        "Items on way": {
            "uz": "Jo'natma yo'lda",
            "ru": "Посылка в пути"
        }
    },
    "ems_ips": {
        "Items on way": {
            "uz": "Jo'natma yo'lda",
            "ru": "Посылка в пути"
        },
        "Receive item at office of exchange (Inb)": {
            "uz": "Ayirboshlash punktida qabul qilindi",
            "ru": "Принято в пункте обмена"
        },
        "Receive item at office of exchange (Otb)": {
            "uz": "Ayirboshlash punktida qabul qilindi",
            "ru": "Принято в пункте обмена"
        },
        "Send item to customs (Inb)": {
            "uz": "Bojxonaga jo'natildi",
            "ru": "Отправлено на таможню"
        },
        "Send item to customs (Otb)": {
            "uz": "Bojxonaga jo'natildi",
            "ru": "Отправлено на таможню"
        },
        "Return item from customs (Inb)": {
            "uz": "Bojxonadan chiqarildi",
            "ru": " Выпущено из таможни"
        },
        "Return item from customs (Otb)": {
            "uz": "Bojxonadan chiqarildi",
            "ru": " Выпущено из таможни"
        },
        "Send item to domestic location (Inb)": {
            "uz": "Mahalliy punktga yuborildi",
            "ru": "Отправлено в местный пункт"
        },
        "Send item to domestic location (Otb)": {
            "uz": "Mahalliy punktga yuborildi",
            "ru": "Отправлено в местный пункт"
        },
        "Record item customs information (inb)": {
            "uz": "Bojxona ma'lumotlari ro'yxatga olinmoqda",
            "ru": "Осуществляется запись таможенной информации"
        },
        "Record item customs information (Otb)": {
            "uz": "Bojxona ma'lumotlari ro'yxatga olinmoqda",
            "ru": "Осуществляется запись таможенной информации"
        },
        "Ready for Delivery": {
            "uz": "Yetkazib berishga tayyor",
            "ru": " Готово к доставке"
        },
        "Receive item at delivery office (Inb)": {
            "uz": "Yetkazib berish bo'limiga yuborildi",
            "ru": "Отправлено в отделение доставки"
        },
        "Receive item at delivery office (Otb)": {
            "uz": "Yetkazib berish bo'limiga yuborildi",
            "ru": "Отправлено в отделение доставки"
        },
        "Receive item at regional distribution hub (Inb)": {
            "uz": "Hududiy taqsimlash markaziga qabul qilindi",
            "ru": "Принято в региональном распределительном центре"
        },
        "Receive item at regional distribution hub (Otb)": {
            "uz": "Hududiy taqsimlash markaziga qabul qilindi",
            "ru": "Принято в региональном распределительном центре"
        },
        "Out for delivery": {
            "uz": "Yetkazib berish jarayonida",
            "ru": "В процессе доставки"
        },
        "Sent item from distribution hub (Inb)": {
            "uz": "Taqsimlash markazidan jo'natildi",
            "ru": "Отправлено с распределительного центра"
        },
        "Sent item from distribution hub (Otb)": {
            "uz": "Taqsimlash markazidan jo'natildi",
            "ru": "Отправлено с распределительного центра"
        },
        "Unsuccessful item delivery attempt (Inb)": {
            "uz": "Muvaffaqiyatsiz yetkazib berish",
            "ru": "Неудачная попытка доставки"
        },
        "Unsuccessful item delivery attempt (Otb)": {
            "uz": "Muvaffaqiyatsiz yetkazib berish",
            "ru": "Неудачная попытка доставки"
        },
        "Unsuccessful item delivery attempt": {
            "uz": "Muvaffaqiyatsiz yetkazib berish",
            "ru": "Неудачная попытка доставки"
        },
        "Deliver item (Inb)": {
            "uz": "Jo'natmani yetkazib berildi",
            "ru": "Доставка отправления"
        },
        "Deliver item (Otb)": {
            "uz": "Jo'natmani yetkazib berildi",
            "ru": "Доставка отправления"
        },
        "On the way to sender": {
            "uz": "Jo'natuvchi shaxs tomon yo'lda",
            "ru": "В пути к отправителю"
        },
        "Delivered to sender": {
            "uz": "Jo'natuvchi shaxsga yetkazildi",
            "ru": "Доставлено отправителю"
        },
        "Stop item import (Inb)": {
            "uz": "Jo'natma importi to'xtatildi",
            "ru": "Остановка импорта отправления"
        },
        "Stop item import (Otb)": {
            "uz": "Jo'natma importi to'xtatildi",
            "ru": "Остановка импорта отправления"
        },
        "Insert item into bag (Otb)": {
            "uz": "Jo'natma belgilangan mamlakatga yuborish uchun depeshaga joylandi",
            "ru": "Отправление помещено в депешу для отправки в страну назначения"
        },
        "Insert item into bag (Inb)": {
            "uz": "Jo'natma belgilangan mamlakatga yuborish uchun depeshaga joylandi",
            "ru": "Отправление помещено в депешу для отправки в страну назначения"
        },
        "Insert item into domestic bag": {
            "uz": " Jo'natma belgilangan punktga yuborish uchun depeshaga joylandi",
            "ru": "Отправление помещено в депешу для отправки в пункт назначения"
        },
        "Receive item from customer (Otb)": {
            "uz": "Mijozdan jo'natmani qabul qilish",
            "ru": "Получение отправления от клиента"
        }
    }
}


@method_decorator(cache_page(60*10), name='dispatch')
class Test(APIView):
    permission_classes = [AllowAny, ]
    throttle_classes = [UserRateThrottle, ]

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
            ## faqat ems uchun shart
            if barcode[:1] == "E":
                if response_data_2[0]["InfoFromEdi"] != None:
                    for i in range(len(
                            response_data_2[0]["InfoFromEdi"]["TMailitemInfoFromEDI"][0]["Events"][
                                "TMailitemEventEDI"])):
                        response_data_2[0]["InfoFromEdi"]["TMailitemInfoFromEDI"][0]["Events"]["TMailitemEventEDI"][i][
                            "ReceivedDispatch"] = None
                if response_data_2[0]["OperationalMailitems"] != None:
                    for j in range(
                            len(response_data_2[0]["OperationalMailitems"]["TMailitemInfoFromScanning"][0]["Events"][
                                    "TMailitemEventScanning"])):
                        response_data_2[0]["OperationalMailitems"]["TMailitemInfoFromScanning"][0]["Events"][
                            "TMailitemEventScanning"][j]["ReceivedDispatch"] = None

                #### tarjima uchun keraklik kod
                if response_data_2[0]["InfoFromEdi"] != None:
                    for i in response_data_2[0]["InfoFromEdi"]["TMailitemInfoFromEDI"][0]["Events"][
                        "TMailitemEventEDI"]:
                        if i['IPSEventType']["Name"] in track_translate["ems_ips"]:
                            i['IPSEventType']['LocalName_uz'] = track_translate["ems_ips"][i['IPSEventType']["Name"]][
                                "uz"]
                            i['IPSEventType']['LocalName_ru'] = track_translate["ems_ips"][i['IPSEventType']["Name"]][
                                "ru"]

                if response_data_2[0]["OperationalMailitems"] != None:
                    for i in response_data_2[0]["OperationalMailitems"]["TMailitemInfoFromScanning"][0]["Events"][
                        "TMailitemEventScanning"]:
                        if i['IPSEventType']["Name"] in track_translate["ems_ips"]:
                            i['IPSEventType']['LocalName_uz'] = track_translate["ems_ips"][i['IPSEventType']["Name"]][
                                "uz"]
                            i['IPSEventType']['LocalName_ru'] = track_translate["ems_ips"][i['IPSEventType']["Name"]][
                                "ru"]
                #### infofromedi dan operational Mails items ga qo'shildi
                if response_data_2[0]["InfoFromEdi"] != None:
                    if response_data_2[0]["OperationalMailitems"] != None:
                        for i in response_data_2[0]["InfoFromEdi"]["TMailitemInfoFromEDI"][0]["Events"][
                            "TMailitemEventEDI"]:
                                response_data_2[0]["OperationalMailitems"]["TMailitemInfoFromScanning"][0]["Events"][
                                    "TMailitemEventScanning"].append(i)
                                # response_data_2[0]["InfoFromEdi"]["TMailitemInfoFromEDI"][0]["Events"][
                                #     "TMailitemEventEDI"].remove(i)
                return Response(data=response_data_2, status=status.HTTP_200_OK)

            # bu emsga bo'gliq bo'lmagan ma'lumotlar
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

            #######################
            ## new method for translate ips data
            if response_data_2[0]["InfoFromEdi"] != None:
                for i in response_data_2[0]["InfoFromEdi"]["TMailitemInfoFromEDI"][0]["Events"][
                    "TMailitemEventEDI"]:
                    if i['IPSEventType']['LocalName'] in track_translate["ips"]:
                        i['IPSEventType']['LocalName_uz'] = track_translate["ips"][i['IPSEventType']['LocalName']]["uz"]
                        i['IPSEventType']['LocalName_ru'] = track_translate["ips"][i['IPSEventType']['LocalName']]["ru"]

            if response_data_2[0]["OperationalMailitems"] != None:
                for i in response_data_2[0]["OperationalMailitems"]["TMailitemInfoFromScanning"][0]["Events"][
                    "TMailitemEventScanning"]:
                    if i['IPSEventType']['LocalName'] in track_translate["ips"]:
                        i['IPSEventType']['LocalName_uz'] = track_translate["ips"][i['IPSEventType']['LocalName']]["uz"]
                        i['IPSEventType']['LocalName_ru'] = track_translate["ips"][i['IPSEventType']['LocalName']]["ru"]

            if response_data_2[0]["InfoFromEdi"] != None:
                if response_data_2[0]["OperationalMailitems"] != None:
                    for i in response_data_2[0]["InfoFromEdi"]["TMailitemInfoFromEDI"][0]["Events"][
                        "TMailitemEventEDI"]:
                        response_data_2[0]["OperationalMailitems"]["TMailitemInfoFromScanning"][0]["Events"][
                            "TMailitemEventScanning"].append(i)
                        # response_data_2[0]["InfoFromEdi"]["TMailitemInfoFromEDI"][0]["Events"][
                        #     "TMailitemEventEDI"].remove(i)

            return Response(data=response_data_2, status=status.HTTP_200_OK)

        # header keladigan data
        max_retries = 1  # Maksimal urinishlar soni
        retry_delay = 1  # Qayta urinishdan oldin kutish (soniyada)
        url_header = f"https://prodapi.pochta.uz/api/v1/public/order/{barcode}"
        url_shipox = f"https://prodapi.pochta.uz/api/v1/public/order/{barcode}/history_items"
        headers = {
            'Content-Type': 'application/json',
            'Accept': 'application/json',
            'Authorization': f'Bearer {gettoken()}'
        }
        for attempt in range(max_retries):
            try:
                # APIga so'rov yuborish
                data_header = requests.get(url_header, headers={
            'Content-Type': 'application/json',
            'Accept': 'application/json',
            'Authorization': f'Bearer {gettoken()}'
        }, timeout=10)
                data_shipox = requests.get(url_shipox, headers={
            'Content-Type': 'application/json',
            'Accept': 'application/json',
            'Authorization': f'Bearer {gettoken()}'
        }, timeout=10)

                data_header = data_header.json()
                data_shipox = data_shipox.json()
                # API'dan muvaffaqiyatli javob olinsa, ma'lumotni qaytarish
                if data_header.get('status') == "success":
                    total_data_2 = {'header': data_header}
                    if barcode[:2] != 'SX' and data_header["data"]['locations'][0]['country']['code'] == 'UZ' and \
                            data_header["data"]['locations'][1]['country']['code'] == 'UZ':

                        total_data_2['shipox'] = data_shipox
                        total_data_2['gdeposilka'] = None
                        for trans in total_data_2["shipox"]["data"]["list"]:
                            if trans['status'] in track_translate["shipox"]:
                                trans["status_uz"] = track_translate["shipox"][trans["status"]]["uz"]
                                trans["status_ru"] = \
                                track_translate["shipox"][trans["status"]]["ru"]
                                trans["status_eng"] = \
                                track_translate["shipox"][trans["status"]]["eng"]
                            if trans['status'] in track_translate["shipox_comment"]:
                                trans["comment_uz"] = track_translate["shipox_comment"][trans["status"]]["uz"]
                                trans["comment_ru"] = \
                                track_translate["shipox_comment"][trans["status"]]["ru"]
                                trans["comment_eng"] = \
                                track_translate["shipox_comment"][trans["status"]]["eng"]
                        return Response(total_data_2, status=status.HTTP_200_OK)

                    total_data_2 = {"header": data_header, "shipox": data_shipox}
                    for trans in total_data_2["shipox"]["data"]["list"]:
                        if trans['status'] in track_translate["shipox"]:
                            trans["status_uz"] = track_translate["shipox"][trans["status"]]["uz"]
                            trans["status_ru"] = \
                                track_translate["shipox"][trans["status"]]["ru"]
                            trans["status_eng"] = \
                                track_translate["shipox"][trans["status"]]["eng"]
                        if trans['status'] in track_translate["shipox_comment"]:
                            trans["comment_uz"] = track_translate["shipox_comment"][trans["status"]]["uz"]
                            trans["comment_ru"] = \
                                track_translate["shipox_comment"][trans["status"]]["ru"]
                            trans["comment_eng"] = \
                                track_translate["shipox_comment"][trans["status"]]["eng"]


                    # # gdeposilka ma'lumotlari shipox bilan bog'liqlari
                    #
                    # url1 = f"https://gdeposylka.ru/api/v4/tracker/detect/{barcode}"
                    # headers = {
                    #     "X-Authorization-Token": "65bbbac85f796f8032e0874411f4d1f5af7185a99e184709bf0c1f38d95486fa2338733760a48704"
                    # }
                    # response1 = requests.get(url1, headers=headers)
                    # data = response1.json()
                    # if len(data["data"]) != 0 and response1.status_code == 200:
                    #     url2 = f"https://gdeposylka.ru{data['data'][0]['tracker_url']}"
                    #     response2 = requests.get(url2, headers=headers)
                    #     response_x = response2.json()
                    #     if len(response_x["messages"]) == 0:
                    #         gdeposylka = {
                    #             "result": response_x['result'],
                    #             'data': {
                    #                 'id': response_x['data']['id'],
                    #                 'tracking_number': response_x['data']['tracking_number'],
                    #                 "tracking_number_secondary": response_x['data']['tracking_number_secondary'],
                    #                 "tracking_number_current": response_x['data']['tracking_number_current'],
                    #                 "courier": response_x['data']['courier'],
                    #                 "is_active": response_x['data']['is_active'],
                    #                 "is_delivered": response_x['data']['is_delivered'],
                    #                 "last_check": response_x['data']['last_check'],
                    #                 'checkpoints': [],
                    #                 "extra": response_x['data']['extra']
                    #             }
                    #         }
                    #         for points in response_x['data']['checkpoints']:
                    #             if points['courier']['slug'] != 'ozbekiston-pochtasi':
                    #                 gdeposylka['data']['checkpoints'].append(points)
                    #         total_data_2['gdeposilka'] = gdeposylka
                    #         for trans_gde in total_data_2["gdeposilka"]["data"]["checkpoints"]:
                    #             if trans_gde['status_name'] in track_translate["gdeposilka"]:
                    #                 trans_gde["status_uz"] = track_translate["gdeposilka"][trans_gde["status_name"]]["uz"]
                    #                 trans_gde["status_ru"] = \
                    #                     track_translate["gdeposilka"][trans_gde["status_name"]]["ru"]
                    #                 trans_gde["status_eng"] = \
                    #                     track_translate["gdeposilka"][trans_gde["status_name"]]["eng"]
                    #



                        #    ????????????????????????????????????????????
                        # else:
                        #     time.sleep(15)
                        #     response2 = requests.get(url2, headers=headers)
                        #     response_x = response2.json()
                        #     if len(response_x['messages']) == 0:
                        #         gdeposylka = {
                        #             "result": response_x['result'],
                        #             'data': {
                        #                 'id': response_x['data']['id'],
                        #                 'tracking_number': response_x['data']['tracking_number'],
                        #                 "tracking_number_secondary": response_x['data']['tracking_number_secondary'],
                        #                 "tracking_number_current": response_x['data']['tracking_number_current'],
                        #                 "courier": response_x['data']['courier'],
                        #                 "is_active": response_x['data']['is_active'],
                        #                 "is_delivered": response_x['data']['is_delivered'],
                        #                 "last_check": response_x['data']['last_check'],
                        #                 'checkpoints': [],
                        #                 "extra": response_x['data']['extra']
                        #             }
                        #         }
                        #         for points in response_x['data']['checkpoints']:
                        #             if points['courier']['slug'] != 'ozbekiston-pochtasi':
                        #                 gdeposylka['data']['checkpoints'].append(points)
                        #         total_data_2['gdeposilka'] = gdeposylka
                        #     else:
                        #         total_data_2['gdeposilka'] = "please try again we are processing the data"
                        # for trans_gde in total_data_2["gdeposilka"]["data"]["checkpoints"]:
                        #     if trans_gde['status_name'] in track_translate["gdeposilka"]:
                        #         trans_gde["status_uz"] = track_translate["gdeposilka"][trans_gde["status_name"]]["uz"]
                        #         trans_gde["status_ru"] = \
                        #             track_translate["gdeposilka"][trans_gde["status_name"]]["ru"]
                        #         trans_gde["status_eng"] = \
                        #             track_translate["gdeposilka"][trans_gde["status_name"]]["eng"]
                        # return Response(total_data_2, status=status.HTTP_200_OK)
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


        # url1 = f"https://gdeposylka.ru/api/v4/tracker/detect/{barcode}"
        # headers = {
        #     "X-Authorization-Token": "65bbbac85f796f8032e0874411f4d1f5af7185a99e184709bf0c1f38d95486fa2338733760a48704"
        # }
        # response1 = requests.get(url1, headers=headers)
        # data = response1.json()
        #
        # if len(data["data"]) != 0 and response1.status_code == 200:
        #     url2 = f"https://gdeposylka.ru{data['data'][0]['tracker_url']}"
        #     response2 = requests.get(url2, headers=headers)
        #     response_x = response2.json()
        #     if len(response_x["messages"]) == 0 and response2.status_code == 200:
        #         total_data_2['gdeposilka'] = response_x
        #     # else:
        #     #     time.sleep(15)
        #     #     response2 = requests.get(url2, headers=headers)
        #     #     response_x = response2.json()
        #     #     if len(response_x['messages']) == 0 and response2.status_code == 200:
        #     #         total_data_2['gdeposilka'] = response_x
        #     #     else:
        #     #         total_data_2['gdeposilka'] = "please try again we are processing the data"
        #     else:
        #         total_data_2['gdeposilka'] = "No data found"
        #     return Response(total_data_2, status=status.HTTP_200_OK)
        total_data_2['gdeposilka'] = None
        return Response(total_data_2, status=status.HTTP_200_OK)


@method_decorator(cache_page(60*3), name='dispatch')
class Barcode_x(APIView):
    permission_classes = [AllowAny, ]
    throttle_classes = [UserRateThrottle, ]

    def get(self, request, barcode):
        # if (barcode[:2] == "RZ" or barcode[:2] == "CZ" or barcode[:1] == "E") and barcode[:3] != "EHM" and barcode[:3] != "EMI":
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

        shits1 = [1251, 1252, 1253, 1262, 1263, 1264, 1256, 1257, 1266, 1267]
        Sheet1 = [
                {"external_status_id": 1251, "note_content": "Receive item at office of exchange (Inb)", "wing_order_status": "in_sorting_facility", "sorder": "1"},
                {"external_status_id": 1252, "note_content": "Send item to customs (Inb)", "wing_order_status": "sent_to_customs", "sorder": "2"},
                {"external_status_id": 1253, "note_content": "Return item from customs (Inb)", "wing_order_status": "returned_from_customs", "sorder": "3"},
                {"external_status_id": 1262, "note_content": "Record item customs information (inb)", "wing_order_status": "hold_on_at_customs", "sorder": "4"},
                {"external_status_id": 1263, "note_content": "Ready for Delivery", "wing_order_status": "ready_for_delivery", "sorder": "5"},
                {"external_status_id": 1264, "note_content": "Out for delivery", "wing_order_status": "out_for_delivery", "sorder": "6"},
                {"external_status_id": 1256, "note_content": "Unsuccessful item delivery attempt (Inb)", "wing_order_status": "delivery_failed", "sorder": "8"},
                {"external_status_id": 1257, "note_content": "Deliver item (Inb)", "wing_order_status": "completed", "sorder": "9"},
                {"external_status_id": 1266, "note_content": "On the way to sender", "wing_order_status": "returning_to_origin", "sorder": "10"},
                {"external_status_id": 1267, "note_content": "Delivered to sender", "wing_order_status": "returned_to_origin", "sorder": "11"}
                ]
        format_ips = {
                                "CustomsReleaseStatus": {
                                    "Code": None,
                                    "Name": None,
                                    "LocalName": None
                                },
                                "Delivery": {
                                    "DeliveryLocation": None,
                                    "DeliveryPostcode": None,
                                    "SignatoryImage": None,
                                    "SignatoryName": None
                                },
                                "DeliveryAgent": {
                                    "Code": None,
                                    "FullCode": None,
                                    "Name": None
                                },
                                "DispatchNumber": None,
                                "EdiEvent": {
                                    "Code": None,
                                    "Name": None
                                },
                                "EventOffice": {
                                    "Code": "UZTASA",
                                    "Name": "TASHKENT PI1"
                                },
                                "IPSEventType": {
                                    "Code": None,
                                    "Name": "Items on way",
                                    "LocalName": "Items on way"
                                },
                                "LocalDateTime": "2025-02-09T15:27:06",
                                "NonDeliveryReason": {
                                    "Code": None,
                                    "Name": None,
                                    "LocalName": None
                                },
                                "NonDeliveryReason": {
                                    "Code": None,
                                    "Name": None,
                                    "LocalName": None
                                },
                                "ReceivedDispatch": None,
                                "RetentionReason": {
                                    "Code": None,
                                    "Name": None,
                                    "LocalName": None
                                },
                                "CustomsOffice": {
                                    "Code": None,
                                    "Name": None
                                },
                                "CustomsOfficeType": {
                                    "Code": None,
                                    "Name": None
                                },
                                "GmtDateTime": "2025-02-09T10:27:06.297",
                                "NextOffice": {
                                    "Code": None,
                                    "Name": None
                                }
        }
        new_codes = []
        if response_data_2[0]["InfoFromEdi"] != None:
            for i in response_data_2[0]["InfoFromEdi"]["TMailitemInfoFromEDI"][0]["Events"]["TMailitemEventScanning"]:
                if i['IPSEventType']['Code'] in new_codes:
                    break
                new_codes.append(i["IPSEventType"]["Code"])

        if response_data_2[0]["OperationalMailitems"] != None:
            for i in response_data_2[0]["OperationalMailitems"]["TMailitemInfoFromScanning"][0]["Events"]["TMailitemEventScanning"]:
                if i['IPSEventType']['Code'] in new_codes:
                    break
                new_codes.append(i["IPSEventType"]["Code"])

        search_data = None
        for data in shits1:
            if data not in new_codes:
                for its in Sheet1:
                    if data == its["external_status_id"]:
                        search_data = its["wing_order_status"]

                        # format_ips nusxasini yaratish (chuqur nusxa olish)
                        format_ips_copy = copy.deepcopy(format_ips)

                        format_ips_copy["IPSEventType"]["Name"] = its["note_content"]
                        format_ips_copy["IPSEventType"]["LocalName"] = its["note_content"]
                        break

                shipox = requests.get(f"https://prodapi.pochta.uz/api/v1/public/order/{barcode}/history_items")
                if shipox.status_code != 200:
                    return Response(data=response_data_2, status=status.HTTP_200_OK)

                addition_data = shipox.json()["data"]["list"]
                for item in addition_data:
                    if item["status"] == search_data:
                        if item["warehouse"]:
                            format_ips_copy["EventOffice"]["Name"] = item["warehouse"]["name"]
                        format_ips_copy["IPSEventType"]["Code"] = f"{data}"
                        format_ips_copy["LocalDateTime"] = item["date"]
                        format_ips_copy["GmtDateTime"] = item["date"]
                        # Nusxa olingan format_ips obyektini listga qo'shish
                        response_data_2[0]["OperationalMailitems"]["TMailitemInfoFromScanning"][0]["Events"][
                            "TMailitemEventScanning"].append(format_ips_copy)

        return Response(data=response_data_2, status=status.HTTP_200_OK)


change_date = datetime(2025, 3, 11).date()


@method_decorator(cache_page(60*3), name='dispatch')
class Barcode_new(APIView):
    def get(self, request, barcode):
        if not barcode.startswith(("RZ", "CZ", "E")):
            first = {
                "code": "order_not_found",
                "message": "Order Not Found",
                "request_id": "69f059d0-1748-42cc-982c-7a322c4e81fa",
                "status": "error"
            }
            return Response(data=first, status=status.HTTP_400_BAD_REQUEST)

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
            return Response(data=first, status=status.HTTP_400_BAD_REQUEST)
        response_data_2 = response_data

        ###### shipox ips uchun
        url_header = f"https://prodapi.pochta.uz/api/v1/public/order/{barcode}"
        url_shipox = f"https://prodapi.pochta.uz/api/v1/customer/order/{barcode}/history_items"

        max_retries = 2  # Maksimal urinishlar soni
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
                }, timeout=10).json()
                data_shipox = requests.get(url_shipox, headers={
                    'Content-Type': 'application/json',
                    'Accept': 'application/json',
                    'Authorization': f'Bearer {gettoken()}'
                }, timeout=10).json()
            except ConnectTimeout:
                # Agar ulanish timeoutga uchrasa, qayta urinib ko'riladi
                if attempt < max_retries - 1:
                    time.sleep(retry_delay)  # Kutish va yana urinib ko'rish
                else:
                    data_header = {
                        "code": "Server TimeOut Error",
                        "message": "Server Error",
                        "status": "error"
                    }
                    data_shipox = {
                        "code": "Server TimeOut Error",
                        "message": "Server Error",
                        "status": "error"
                    }

        data_header = data_header
        data_shipox = data_shipox
        full_track_temu = []

        if response_data_2[0]["InfoFromEdi"] != None:
            for i in response_data_2[0]["InfoFromEdi"]["TMailitemInfoFromEDI"][0]["Events"]["TMailitemEventEDI"]:
                if i["IPSEventType"]["Name"] == "Items on way":
                    try:
                        gmt_datetime_str = i["GmtDateTime"]
                        local_datetime = datetime.strptime(gmt_datetime_str, "%Y-%m-%dT%H:%M:%S.%f")
                    except ValueError:
                        local_datetime = datetime.strptime(gmt_datetime_str, "%Y-%m-%dT%H:%M:%S")
                    compare_date = change_date  # Faqat sana qismi olinadi
                    local_datetime = local_datetime.date()
                    if local_datetime <= compare_date:
                        for i in response_data_2[0]["InfoFromEdi"]["TMailitemInfoFromEDI"][0]["Events"][
                            "TMailitemEventEDI"]:
                            form = {
                                "EventOffice": {
                                    "Code": "UZTASA",
                                    "Name": "TASHKENT PI1"
                                },
                                "IPSEventType": {
                                    "Code": None,
                                    "Name": None,
                                    "LocalName": None
                                },
                                "date": None,
                                "NonDeliveryReason": {
                                    "Code": None,
                                    "Name": None,
                                    "LocalName": None
                                },
                            }
                            form["EventOffice"]["Name"] = i["EventOffice"]["Name"]
                            form["IPSEventType"]["Name"] = i["IPSEventType"]["Name"]
                            form["IPSEventType"]["Code"] = i["IPSEventType"]["Code"]
                            form["IPSEventType"]["LocalName"] = i["IPSEventType"]["LocalName"]
                            form["date"] = i['GmtDateTime']
                            form["NonDeliveryReason"]["Code"] = i["NonDeliveryReason"]["Code"]
                            form["NonDeliveryReason"]["Name"] = i['NonDeliveryReason']['Name']
                            form["NonDeliveryReason"]["LocalName"] = i['NonDeliveryReason']['LocalName']
                            full_track_temu.append(form)
                        if response_data_2[0]["OperationalMailitems"] != None:
                            for j in \
                                    response_data_2[0]["OperationalMailitems"]["TMailitemInfoFromScanning"][0][
                                        "Events"][
                                        "TMailitemEventScanning"]:
                                form_op = {
                                    "EventOffice": {
                                        "Code": "UZTASA",
                                        "Name": "TASHKENT PI1"
                                    },
                                    "IPSEventType": {
                                        "Code": None,
                                        "Name": None,
                                        "LocalName": None
                                    },
                                    "date": None,
                                    "NonDeliveryReason": {
                                        "Code": None,
                                        "Name": None,
                                        "LocalName": None
                                    },
                                }
                                form_op["EventOffice"]["Name"] = j["EventOffice"]["Name"]
                                form_op["IPSEventType"]["Name"] = j["IPSEventType"]["Name"]
                                form_op["IPSEventType"]["Code"] = j["IPSEventType"]["Code"]
                                form_op["IPSEventType"]["LocalName"] = j["IPSEventType"]["LocalName"]
                                form_op["date"] = j['GmtDateTime']
                                form_op["NonDeliveryReason"]["Code"] = j["NonDeliveryReason"]["Code"]
                                form_op["NonDeliveryReason"]["Name"] = j['NonDeliveryReason']['Name']
                                form_op["NonDeliveryReason"]["LocalName"] = j['NonDeliveryReason']['LocalName']
                                full_track_temu.append(form_op)
                        if not any(item_x["IPSEventType"]["Name"][:12] == "Deliver item" for item_x in
                                   full_track_temu):
                            if data_header['status'] != 'success':
                                return data_header
                            if data_shipox['status'] != 'success':
                                return data_shipox
                            for data in data_shipox['data']["list"]:
                                if data["status"] == 'issued_to_recipient':
                                    form_f = {
                                        "EventOffice": {
                                            "Code": "UZTASA",
                                            "Name": "TASHKENT PI1"
                                        },
                                        "IPSEventType": {
                                            "Code": None,
                                            "Name": None,
                                            "LocalName": None
                                        },
                                        "date": None,
                                        "NonDeliveryReason": {
                                            "Code": None,
                                            "Name": None,
                                            "LocalName": None
                                        },
                                    }
                                    form_f['IPSEventType']["Name"] = "Deliver item"
                                    form_f['IPSEventType']["LocalName"] = "Deliver item"
                                    form_f['IPSEventType']["Code"] = "1257"
                                    form_f["date"] = data['date']
                                    full_track_temu.append(form_f)
                                    break
                                if data["status"] == 'completed':
                                    form_j = {
                                        "EventOffice": {
                                            "Code": "UZTASA",
                                            "Name": "TASHKENT PI1"
                                        },
                                        "IPSEventType": {
                                            "Code": None,
                                            "Name": None,
                                            "LocalName": None
                                        },
                                        "date": None,
                                        "NonDeliveryReason": {
                                            "Code": None,
                                            "Name": None,
                                            "LocalName": None
                                        },
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

                        return Response(data=full_data, status=status.HTTP_200_OK)

        if response_data_2[0]["OperationalMailitems"] != None:
            for j in response_data_2[0]["OperationalMailitems"]["TMailitemInfoFromScanning"][0]["Events"][
                "TMailitemEventScanning"]:
                if j["IPSEventType"]["Name"] == "Items on way":
                    gmt_datetime_str = j.get("GmtDateTime")
                    if gmt_datetime_str:
                        try:
                            local_datetime = datetime.strptime(gmt_datetime_str, "%Y-%m-%dT%H:%M:%S.%f")
                        except ValueError:
                            local_datetime = datetime.strptime(gmt_datetime_str, "%Y-%m-%dT%H:%M:%S")

                    compare_date = change_date  # Faqat sana qismi olinadi
                    local_datetime = local_datetime.date()
                    if local_datetime <= compare_date:
                        for op in \
                                response_data_2[0]["OperationalMailitems"]["TMailitemInfoFromScanning"][0]["Events"][
                                    "TMailitemEventScanning"]:
                            form = {
                                "EventOffice": {
                                    "Code": "UZTASA",
                                    "Name": "TASHKENT PI1"
                                },
                                "IPSEventType": {
                                    "Code": None,
                                    "Name": None,
                                    "LocalName": None
                                },
                                "date": None,
                                "NonDeliveryReason": {
                                    "Code": None,
                                    "Name": None,
                                    "LocalName": None
                                },
                            }
                            form["EventOffice"]["Name"] = op["EventOffice"]["Name"]
                            form["IPSEventType"]["Name"] = op["IPSEventType"]["Name"]
                            form["IPSEventType"]["Code"] = op["IPSEventType"]["Code"]
                            form["IPSEventType"]["LocalName"] = op["IPSEventType"]["LocalName"]
                            form["date"] = op['GmtDateTime']
                            form["NonDeliveryReason"]["Code"] = op["NonDeliveryReason"]["Code"]
                            form["NonDeliveryReason"]["Name"] = op['NonDeliveryReason']['Name']
                            form["NonDeliveryReason"]["LocalName"] = op['NonDeliveryReason']['LocalName']
                            full_track_temu.append(form)

                        # `InfoFromEdi` bo'lsa, qo'shimcha ma'lumot qo'shamiz
                        if response_data_2[0]["InfoFromEdi"] is not None:
                            for i in response_data_2[0]["InfoFromEdi"]["TMailitemInfoFromEDI"][0]["Events"][
                                "TMailitemEventEDI"]:
                                form_op = {
                                    "EventOffice": {
                                        "Code": "UZTASA",
                                        "Name": "TASHKENT PI1"
                                    },
                                    "IPSEventType": {
                                        "Code": None,
                                        "Name": None,
                                        "LocalName": None
                                    },
                                    "date": None,
                                    "NonDeliveryReason": {
                                        "Code": None,
                                        "Name": None,
                                        "LocalName": None
                                    },
                                }
                                form_op["EventOffice"]["Name"] = i["EventOffice"]["Name"]
                                form_op["IPSEventType"]["Name"] = i["IPSEventType"]["Name"]
                                form_op["IPSEventType"]["Code"] = i["IPSEventType"]["Code"]
                                form_op["IPSEventType"]["LocalName"] = i["IPSEventType"]["LocalName"]
                                form_op["date"] = i['GmtDateTime']
                                form_op["NonDeliveryReason"]["Code"] = i["NonDeliveryReason"]["Code"]
                                form_op["NonDeliveryReason"]["Name"] = i['NonDeliveryReason']['Name']
                                form_op["NonDeliveryReason"]["LocalName"] = i['NonDeliveryReason']['LocalName']
                                full_track_temu.append(form_op)

                        # `Shipox` dan kelgan statusni tekshiramiz
                        if not any(item_x["IPSEventType"]["Name"][:12] == "Deliver item" for item_x in
                                   full_track_temu):
                            if data_header['status'] != 'success':
                                return Response(data=data_header, status=status.HTTP_400_BAD_REQUEST)
                            if data_shipox['status'] != 'success':
                                return Response(data=data_shipox, status=status.HTTP_404_NOT_FOUND)
                            for data in data_shipox['data']["list"]:
                                if data["status"] == 'issued_to_recipient':
                                    form_f = {
                                        "EventOffice": {"Code": "UZTASA", "Name": "TASHKENT PI1"},
                                        "IPSEventType": {"Code": "1257", "Name": "Deliver item",
                                                         "LocalName": "Deliver item"},
                                        "date": data['date'],
                                        "NonDeliveryReason": {
                                            "Code": None,
                                            "Name": None,
                                            "LocalName": None
                                        },
                                    }
                                    full_track_temu.append(form_f)
                                    break
                                elif data["status"] == 'completed':
                                    form_j = {
                                        "EventOffice": {"Code": "UZTASA", "Name": "TASHKENT PI1"},
                                        "IPSEventType": {"Code": "1257", "Name": "Deliver item",
                                                         "LocalName": "Deliver item"},
                                        "date": data['date'],
                                        "NonDeliveryReason": {
                                            "Code": None,
                                            "Name": None,
                                            "LocalName": None
                                        },
                                    }
                                    full_track_temu.append(form_j)
                                    break

                        # Yakuniy ma'lumotni shakllantiramiz
                        full_data = {
                            "header": data_header,
                            "data": full_track_temu,
                        }

                        return Response(data=full_data, status=status.HTTP_200_OK)

        if response_data_2[0]["InfoFromEdi"] != None:
            for i in response_data_2[0]["InfoFromEdi"]["TMailitemInfoFromEDI"][0]["Events"]["TMailitemEventEDI"]:
                if i["IPSEventType"]["Name"] == "Items on way":
                    form = {
                        "EventOffice": {
                            "Code": "UZTASA",
                            "Name": "TASHKENT PI1"
                        },
                        "IPSEventType": {
                            "Code": None,
                            "Name": None,
                            "LocalName": None
                        },
                        "date": None,
                        "NonDeliveryReason": {
                            "Code": None,
                            "Name": None,
                            "LocalName": None
                        },
                    }
                    form["IPSEventType"]["Code"] = i["IPSEventType"]["Name"]
                    form["IPSEventType"]["Code"] = i["IPSEventType"]["Code"]
                    form["IPSEventType"]["LocalName"] = i["IPSEventType"]["LocalName"]
                    form["date"] = i['GmtDateTime']
                    form["NonDeliveryReason"]["Code"] = i["NonDeliveryReason"]["Code"]
                    form["NonDeliveryReason"]["Name"] = i['NonDeliveryReason']['Name']
                    form["NonDeliveryReason"]["LocalName"] = i['NonDeliveryReason']['LocalName']
                    full_track_temu.append(form)
                    break

        if response_data_2[0]["OperationalMailitems"] != None:
            for j in response_data_2[0]["OperationalMailitems"]["TMailitemInfoFromScanning"][0]["Events"][
                "TMailitemEventScanning"]:
                if j["IPSEventType"]["Name"] == "Items on way":
                    form = {
                        "EventOffice": {
                            "Code": "UZTASA",
                            "Name": "TASHKENT PI1"
                        },
                        "IPSEventType": {
                            "Code": None,
                            "Name": None,
                            "LocalName": None
                        },
                        "date": None,
                        "NonDeliveryReason": {
                            "Code": None,
                            "Name": None,
                            "LocalName": None
                        },
                    }
                    form["IPSEventType"]["Name"] = j["IPSEventType"]["Name"]
                    form["IPSEventType"]["Code"] = j["IPSEventType"]["Code"]
                    form["IPSEventType"]["LocalName"] = j["IPSEventType"]["LocalName"]
                    form["date"] = j['GmtDateTime']
                    form["NonDeliveryReason"]["Code"] = j["NonDeliveryReason"]["Code"]
                    form["NonDeliveryReason"]["Name"] = j['NonDeliveryReason']['Name']
                    form["NonDeliveryReason"]["LocalName"] = j['NonDeliveryReason']['LocalName']
                    full_track_temu.append(form)
                    break

        ##############
        #############
        ### buyog'i shipox ma'lumotlari
        #############################

        data_header = data_header
        data_shipox = data_shipox
        last_form = None
        lasted_form = None
        if data_header['status'] != 'success':
            if any(item_x["IPSEventType"]["Name"] == "Items on way" for item_x in
                   full_track_temu):
                full_data = {
                    "header": data_header,
                    "data": full_track_temu,
                }
                return Response(data=full_data, status=status.HTTP_200_OK)
            return Response(data=data_header, status=status.HTTP_200_OK)
        if data_shipox['status'] != 'success':
            if any(item_x["IPSEventType"]["Name"] == "Items on way" for item_x in
                   full_track_temu):
                full_data = {
                    "header": data_shipox,
                    "data": full_track_temu,
                }
                return Response(data=full_data, status=status.HTTP_200_OK)
            return Response(data=data_shipox, status=status.HTTP_200_OK)
        #######################################

        ##### 1-status uchun tekshirish

        for item in data_shipox['data']['list']:
            if item["status"] == 'in_sorting_facility':
                form = {
                    "EventOffice": {
                        "Code": "UZTASA",
                        "Name": "TASHKENT PI1"
                    },
                    "IPSEventType": {
                        "Code": None,
                        "Name": None,
                        "LocalName": None
                    },
                    "date": None,
                    "NonDeliveryReason": {
                        "Code": None,
                        "Name": None,
                        "LocalName": None
                    },
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
                        "Name": "TASHKENT PI1"
                    },
                    "IPSEventType": {
                        "Code": None,
                        "Name": None,
                        "LocalName": None
                    },
                    "date": None,
                    "NonDeliveryReason": {
                        "Code": None,
                        "Name": None,
                        "LocalName": None
                    },
                }
                form['IPSEventType']["Name"] = "Send item to customs"
                form['IPSEventType']["LocalName"] = "Send item to customs"
                form['IPSEventType']["Code"] = "1252"
                form["date"] = item["date"]
                lasted_form = form
        if lasted_form == None:
            if last_form != None:
                form = {
                    "EventOffice": {
                        "Code": "UZTASA",
                        "Name": "TASHKENT PI1"
                    },
                    "IPSEventType": {
                        "Code": None,
                        "Name": None,
                        "LocalName": None
                    },
                    "date": None,
                    "NonDeliveryReason": {
                        "Code": None,
                        "Name": None,
                        "LocalName": None
                    },
                }
                form['IPSEventType']["Name"] = "Send item to customs"
                form['IPSEventType']["LocalName"] = "Send item to customs"
                form['IPSEventType']["Code"] = "1252"
                form["date"] = datetime.fromisoformat(last_form["date"][:19]) + timedelta(minutes=2)
                full_track_temu.append(form)
        else:
            full_track_temu.append(lasted_form)

        ############# 3-status uchun tekshirish

        for item in data_shipox['data']['list']:
            if item["status"] == 'hold_on_at_customs':
                form = {
                    "EventOffice": {
                        "Code": "UZTASA",
                        "Name": "TASHKENT PI1"
                    },
                    "IPSEventType": {
                        "Code": None,
                        "Name": None,
                        "LocalName": None
                    },
                    "date": None,
                    "NonDeliveryReason": {
                        "Code": "I",
                        "Name": None,
                        "LocalName": None
                    },
                }
                form['IPSEventType']["Name"] = "Custom Clearance Exception - Inspection"
                form['IPSEventType']["LocalName"] = "Custom Clearance Exception - Inspection"
                form['IPSEventType']["Code"] = "1262"
                form['NonDeliveryReason']["Name"] = "High-value goods - Official customs declaration required"
                form['NonDeliveryReason'][
                    "LocalName"] = "High-value goods - Official customs declaration required"
                form["date"] = item["date"]
                full_track_temu.append(form)
                break
        #### 4- status uchun tekshirish
        for item in data_shipox['data']['list']:
            if item["status"] == 'returned_from_customs':
                form = {
                    "EventOffice": {
                        "Code": "UZTASA",
                        "Name": "TASHKENT PI1"
                    },
                    "IPSEventType": {
                        "Code": None,
                        "Name": None,
                        "LocalName": None
                    },
                    "date": None,
                    "NonDeliveryReason": {
                        "Code": None,
                        "Name": None,
                        "LocalName": None
                    },
                }
                form['IPSEventType']["Name"] = "Return item from customs"
                form['IPSEventType']["LocalName"] = "Return item from customs"
                form['IPSEventType']["Code"] = "1253"
                form["date"] = item["date"]
                last_form = form

        if last_form:
            full_track_temu.append(last_form)
            form_1 = {
                "EventOffice": {
                    "Code": "UZTASA",
                    "Name": "TASHKENT PI1"
                },
                "IPSEventType": {
                    "Code": None,
                    "Name": None,
                    "LocalName": None
                },
                "date": None,
                "NonDeliveryReason": {
                    "Code": None,
                    "Name": None,
                    "LocalName": None
                },
            }
            form_1['IPSEventType']["Name"] = "Send item to domestic location"
            form_1['IPSEventType']["LocalName"] = "Send item to domestic location"
            form_1['IPSEventType']["Code"] = "1254"
            date_obj = datetime.fromisoformat(last_form["date"][:19]) + timedelta(minutes=10)
            form_1["date"] = date_obj.isoformat()
            full_track_temu.append(form_1)

            ###### yana 20 minut qo'shib qo'shiladi
            form_2 = {
                "EventOffice": {
                    "Code": "UZTASA",
                    "Name": "TASHKENT PI1"
                },
                "IPSEventType": {
                    "Code": None,
                    "Name": None,
                    "LocalName": None
                },
                "date": None,
                "NonDeliveryReason": {
                    "Code": None,
                    "Name": None,
                    "LocalName": None
                },
            }
            form_2['IPSEventType']["Name"] = "Receive item at delivery office"
            form_2['IPSEventType']["LocalName"] = "Receive item at delivery office"
            form_2['IPSEventType']["Code"] = "1255"
            date_obj = datetime.fromisoformat(last_form["date"][:19]) + timedelta(minutes=15)
            form_2["date"] = date_obj.isoformat()
            full_track_temu.append(form_2)

        ############## ready for delivery ga tekshirish

        for item in data_shipox['data']['list']:
            if item["status"] == 'ready_for_delivery':
                for item_x in full_track_temu:
                    if "ready_for_delivery" == item_x["IPSEventType"]["Name"]:
                        item_x["IPSEventType"]["date"] = item["date"]

                if not any(item_x["IPSEventType"]["Name"] == "Return item from customs" for item_x in
                           full_track_temu):
                    form = {
                        "EventOffice": {
                            "Code": "UZTASA",
                            "Name": "TASHKENT PI1"
                        },
                        "IPSEventType": {
                            "Code": None,
                            "Name": None,
                            "LocalName": None
                        },
                        "date": None,
                        "NonDeliveryReason": {
                            "Code": None,
                            "Name": None,
                            "LocalName": None
                        },
                    }
                    form['IPSEventType']["Name"] = "Return item from customs"
                    form['IPSEventType']["LocalName"] = "Return item from customs"
                    form['IPSEventType']["Code"] = "1253"
                    date_obj = datetime.fromisoformat(item["date"][:19]) - timedelta(minutes=20)
                    form["date"] = date_obj.isoformat()
                    full_track_temu.append(form)

                    ########### 10 min qo'shib qo'shiladi
                    form_1 = {
                        "EventOffice": {
                            "Code": "UZTASA",
                            "Name": "TASHKENT PI1"
                        },
                        "IPSEventType": {
                            "Code": None,
                            "Name": None,
                            "LocalName": None
                        },
                        "date": None,
                        "NonDeliveryReason": {
                            "Code": None,
                            "Name": None,
                            "LocalName": None
                        },
                    }
                    form_1['IPSEventType']["Name"] = "Send item to domestic location"
                    form_1['IPSEventType']["LocalName"] = "Send item to domestic location"
                    form_1['IPSEventType']["Code"] = "1254"
                    date_obj = datetime.fromisoformat(item["date"][:19]) - timedelta(minutes=10)
                    form_1["date"] = date_obj.isoformat()
                    full_track_temu.append(form_1)

                    ###### yana 20 minut qo'shib qo'shiladi
                    form_2 = {
                        "EventOffice": {
                            "Code": "UZTASA",
                            "Name": "TASHKENT PI1"
                        },
                        "IPSEventType": {
                            "Code": None,
                            "Name": None,
                            "LocalName": None
                        },
                        "date": None,
                        "NonDeliveryReason": {
                            "Code": None,
                            "Name": None,
                            "LocalName": None
                        },
                    }
                    form_2['IPSEventType']["Name"] = "Receive item at delivery office"
                    form_2['IPSEventType']["LocalName"] = "Receive item at delivery office"
                    form_2['IPSEventType']["Code"] = "1255"
                    date_obj = datetime.fromisoformat(item["date"][:19]) - timedelta(minutes=5)
                    form_2["date"] = date_obj.isoformat()
                    full_track_temu.append(form_2)

                form_3 = {
                    "EventOffice": {
                        "Code": "UZTASA",
                        "Name": "TASHKENT PI1"
                    },
                    "IPSEventType": {
                        "Code": None,
                        "Name": None,
                        "LocalName": None
                    },
                    "date": None,
                    "NonDeliveryReason": {
                        "Code": None,
                        "Name": None,
                        "LocalName": None
                    },
                }
                form_3['IPSEventType']["Name"] = "Ready for Delivery"
                form_3['IPSEventType']["LocalName"] = "Ready for Delivery"
                form_3['IPSEventType']["Code"] = "1263"
                form_3["date"] = item['date']
                full_track_temu.append(form_3)
                break

        wrong_deliverieds = ['receiver_dead', 'not_at_home', 'retention_period_has_expired',
                             'receiver_not_lives_there', 'incomplete_address',
                             'receiver_refuse', 'didnt_appear_on_notice', 'defect',
                             'organization_with_given_address_not_found', 'retention_period_has_expired']
        for item in data_shipox['data']['list']:
            if item["status"] in wrong_deliverieds:
                first_index = next(
                    (i for i, item in enumerate(full_track_temu) if item["IPSEventType"]["Code"] == "1263"),
                    None)
                if first_index is None:
                    form_12 = {
                        "EventOffice": {
                            "Code": "UZTASA",
                            "Name": "TASHKENT PI1"
                        },
                        "IPSEventType": {
                            "Code": None,
                            "Name": None,
                            "LocalName": None
                        },
                        "date": None,
                        "NonDeliveryReason": {
                            "Code": None,
                            "Name": None,
                            "LocalName": None
                        },
                    }
                    form_12['IPSEventType']["Name"] = "Ready for Delivery"
                    form_12['IPSEventType']["LocalName"] = "Ready for Delivery"
                    form_12['IPSEventType']["Code"] = "1263"
                    form_12["date"] = datetime.fromisoformat(item["date"][:19]) - timedelta(minutes=4)
                    full_track_temu.append(form_12)

                form_2 = {
                    "EventOffice": {
                        "Code": "UZTASA",
                        "Name": "TASHKENT PI1"
                    },
                    "IPSEventType": {
                        "Code": None,
                        "Name": None,
                        "LocalName": None
                    },
                    "date": None,
                    "NonDeliveryReason": {
                        "Code": None,
                        "Name": None,
                        "LocalName": None
                    },
                }
                form_2['IPSEventType'][
                    "Name"] = "Unsuccessful item delivery attempt - Addressee not available"
                form_2['IPSEventType'][
                    "LocalName"] = "Unsuccessful item delivery attempt - Addressee not available"
                form_2['IPSEventType']["Code"] = "1256"
                form_2["date"] = item["date"]
                full_track_temu.append(form_2)

                form_3 = {
                    "EventOffice": {
                        "Code": "UZTASA",
                        "Name": "TASHKENT PI1"
                    },
                    "IPSEventType": {
                        "Code": None,
                        "Name": None,
                        "LocalName": None
                    },
                    "date": None,
                    "NonDeliveryReason": {
                        "Code": None,
                        "Name": None,
                        "LocalName": None
                    },
                }
                form_3['IPSEventType'][
                    "Name"] = "Unsuccessful item delivery attempt -Customer request pickup"
                form_3['IPSEventType'][
                    "LocalName"] = "Unsuccessful item delivery attempt -Customer requested pickup"
                form_3['IPSEventType']["Code"] = "1268"
                date_obj = datetime.fromisoformat(item["date"][:19]) + timedelta(minutes=2)
                form_3["date"] = date_obj.isoformat()
                full_track_temu.append(form_3)
                break

            ############### out for deliveryga tekshirish
        for item in data_shipox['data']['list']:
            if item["status"] == 'out_for_delivery':
                first_index = next(
                    (i for i, item in enumerate(full_track_temu) if item["IPSEventType"]["Code"] == "1263"),
                    None)
                if first_index is None:
                    form_3 = {
                        "EventOffice": {
                            "Code": "UZTASA",
                            "Name": "TASHKENT PI1"
                        },
                        "IPSEventType": {
                            "Code": None,
                            "Name": None,
                            "LocalName": None
                        },
                        "date": None,
                        "NonDeliveryReason": {
                            "Code": None,
                            "Name": None,
                            "LocalName": None
                        },
                    }
                    form_3['IPSEventType']["Name"] = "Ready for Delivery"
                    form_3['IPSEventType']["LocalName"] = "Ready for Delivery"
                    form_3['IPSEventType']["Code"] = "1263"
                    form_3["date"] = datetime.fromisoformat(item["date"][:19]) - timedelta(minutes=5)
                    full_track_temu.append(form_3)

                second_index = next(
                    (i for i, item in enumerate(full_track_temu) if item["IPSEventType"]["Code"] == "1256"),
                    None)
                if second_index is not None:
                    form_13 = {
                        "EventOffice": {
                            "Code": "UZTASA",
                            "Name": "TASHKENT PI1"
                        },
                        "IPSEventType": {
                            "Code": None,
                            "Name": None,
                            "LocalName": None
                        },
                        "date": None,
                        "NonDeliveryReason": {
                            "Code": None,
                            "Name": None,
                            "LocalName": None
                        },
                    }
                    form_13['IPSEventType']["Name"] = "Ready for Delivery"
                    form_13['IPSEventType']["LocalName"] = "Ready for Delivery"
                    form_13['IPSEventType']["Code"] = "1263"
                    form_13["date"] = datetime.fromisoformat(item["date"][:19]) - timedelta(minutes=5)
                    full_track_temu.append(form_13)

                form_11 = {
                    "EventOffice": {
                        "Code": "UZTASA",
                        "Name": "TASHKENT PI1"
                    },
                    "IPSEventType": {
                        "Code": None,
                        "Name": None,
                        "LocalName": None
                    },
                    "date": None,
                    "NonDeliveryReason": {
                        "Code": None,
                        "Name": None,
                        "LocalName": None
                    },
                }

                form_11['IPSEventType']["Name"] = "Out for delivery"
                form_11['IPSEventType']["LocalName"] = "Out for delivery"
                form_11['IPSEventType']["Code"] = "1264"
                form_11["date"] = item['date']
                full_track_temu.append(form_11)
                break

        ######## delivered uchun tekshirish
        for item in data_shipox['data']['list']:
            if item["status"] == 'completed':
                if not any(item_x["IPSEventType"]["Name"] == "Out for delivery" for item_x in full_track_temu):
                    form_2 = {
                        "EventOffice": {
                            "Code": "UZTASA",
                            "Name": "TASHKENT PI1"
                        },
                        "IPSEventType": {
                            "Code": None,
                            "Name": None,
                            "LocalName": None
                        },
                        "date": None,
                        "NonDeliveryReason": {
                            "Code": None,
                            "Name": None,
                            "LocalName": None
                        },
                    }
                    form_2['IPSEventType']["Name"] = "Out for delivery"
                    form_2['IPSEventType']["LocalName"] = "Out for delivery"
                    form_2['IPSEventType']["Code"] = "1264"
                    date_obj = datetime.fromisoformat(item["date"][:19]) - timedelta(minutes=5)
                    form_2["date"] = date_obj.isoformat()
                    full_track_temu.append(form_2)

                if not any(item_x["IPSEventType"]["Name"] == "Ready for Delivery" for item_x in
                           full_track_temu):
                    form_3 = {
                        "EventOffice": {
                            "Code": "UZTASA",
                            "Name": "TASHKENT PI1"
                        },
                        "IPSEventType": {
                            "Code": None,
                            "Name": None,
                            "LocalName": None
                        },
                        "date": None,
                        "NonDeliveryReason": {
                            "Code": None,
                            "Name": None,
                            "LocalName": None
                        },
                    }
                    form_3['IPSEventType']["Name"] = "Ready for Delivery"
                    form_3['IPSEventType']["LocalName"] = "Ready for Delivery"
                    form_3['IPSEventType']["Code"] = "1263"
                    date_obj = datetime.fromisoformat(item["date"][:19]) - timedelta(minutes=10)
                    form_3["date"] = date_obj.isoformat()
                    full_track_temu.append(form_3)

                form_j = {
                    "EventOffice": {
                        "Code": "UZTASA",
                        "Name": "TASHKENT PI1"
                    },
                    "IPSEventType": {
                        "Code": None,
                        "Name": None,
                        "LocalName": None
                    },
                    "date": None,
                    "NonDeliveryReason": {
                        "Code": None,
                        "Name": None,
                        "LocalName": None
                    },
                }
                form_j['IPSEventType']["Name"] = "Deliver item"
                form_j['IPSEventType']["LocalName"] = "Deliver item"
                form_j['IPSEventType']["Code"] = "1257"
                form_j["date"] = item['date']
                full_track_temu.append(form_j)
                break

            if item["status"] == 'issued_to_recipient':
                if not any(item_x["IPSEventType"]["Name"] == "Out for delivery" for item_x in full_track_temu):
                    form_2 = {
                        "EventOffice": {
                            "Code": "UZTASA",
                            "Name": "TASHKENT PI1"
                        },
                        "IPSEventType": {
                            "Code": None,
                            "Name": None,
                            "LocalName": None
                        },
                        "date": None,
                        "NonDeliveryReason": {
                            "Code": None,
                            "Name": None,
                            "LocalName": None
                        },
                    }
                    form_2['IPSEventType']["Name"] = "Out for delivery"
                    form_2['IPSEventType']["LocalName"] = "Out for delivery"
                    form_2['IPSEventType']["Code"] = "1264"
                    date_obj = datetime.fromisoformat(item["date"][:19]) - timedelta(minutes=5)
                    form_2["date"] = date_obj.isoformat()
                    full_track_temu.append(form_2)

                if not any(item_x["IPSEventType"]["Name"] == "Ready for Delivery" for item_x in
                           full_track_temu):
                    form_2 = {
                        "EventOffice": {
                            "Code": "UZTASA",
                            "Name": "TASHKENT PI1"
                        },
                        "IPSEventType": {
                            "Code": None,
                            "Name": None,
                            "LocalName": None
                        },
                        "date": None,
                        "NonDeliveryReason": {
                            "Code": None,
                            "Name": None,
                            "LocalName": None
                        },
                    }
                    form_2['IPSEventType']["Name"] = "Ready for Delivery"
                    form_2['IPSEventType']["LocalName"] = "Ready for Delivery"
                    form_2['IPSEventType']["Code"] = "1263"
                    date_obj = datetime.fromisoformat(item["date"][:19]) - timedelta(minutes=10)
                    form_2["date"] = date_obj.isoformat()
                    full_track_temu.append(form_2)

                form_f = {
                    "EventOffice": {
                        "Code": "UZTASA",
                        "Name": "TASHKENT PI1"
                    },
                    "IPSEventType": {
                        "Code": None,
                        "Name": None,
                        "LocalName": None
                    },
                    "date": None,
                    "NonDeliveryReason": {
                        "Code": None,
                        "Name": None,
                        "LocalName": None
                    },
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
                        "Name": "TASHKENT PI1"
                    },
                    "IPSEventType": {
                        "Code": None,
                        "Name": None,
                        "LocalName": None
                    },
                    "date": None,
                    "NonDeliveryReason": {
                        "Code": None,
                        "Name": None,
                        "LocalName": None
                    },
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
                if not any(item_x["IPSEventType"]["Name"] == "On the way to sender" for item_x in
                           full_track_temu):
                    form_s = {
                        "EventOffice": {
                            "Code": "UZTASA",
                            "Name": "TASHKENT PI1"
                        },
                        "IPSEventType": {
                            "Code": None,
                            "Name": None,
                            "LocalName": None
                        },
                        "date": None,
                        "NonDeliveryReason": {
                            "Code": None,
                            "Name": None,
                            "LocalName": None
                        },
                    }
                    form_s['IPSEventType']["Name"] = "On the way to sender"
                    form_s['IPSEventType']["LocalName"] = "On the way to sender"
                    form_s['IPSEventType']["Code"] = "1266"
                    date_obj = datetime.fromisoformat(item["date"][:19]) - timedelta(minutes=5)
                    form_s["date"] = date_obj.isoformat()
                    full_track_temu.append(form_s)
                form_f = {
                    "EventOffice": {
                        "Code": "UZTASA",
                        "Name": "TASHKENT PI1"
                    },
                    "IPSEventType": {
                        "Code": None,
                        "Name": None,
                        "LocalName": None
                    },
                    "date": None,
                    "NonDeliveryReason": {
                        "Code": None,
                        "Name": None,
                        "LocalName": None
                    },
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

        return Response(data=full_data, status=status.HTTP_200_OK)


@method_decorator(cache_page(60*3), name='dispatch')
class Barcode_new_x(APIView):
    def post(self, request):
        barcodes = request.data.get("barcodes", [])  # JSON dan barcodelarni olish

        if not isinstance(barcodes, list) or len(barcodes) < 2 or len(barcodes) > 15:
            return Response(
                {"code": "bad_request", "message": "number of barcodes would not be few than 2 yoki more than 15"},
                status=status.HTTP_400_BAD_REQUEST
            )

        max_workers = min(5, len(barcodes))  # Parallel ishlash uchun workerlar soni
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            results = list(executor.map(self.process_barcode, barcodes))

        return Response(results, status=status.HTTP_200_OK)

    def process_barcode(self, barcode):
        if not barcode.startswith(("RZ", "CZ", "E")):
            first = {
                "code": "order_not_found",
                "message": "Order Not Found",
                "request_id": "69f059d0-1748-42cc-982c-7a322c4e81fa",
                "status": "error"
            }
            return first

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
            return first
        response_data_2 = response_data

        ###### shipox ips uchun
        url_header = f"https://prodapi.pochta.uz/api/v1/public/order/{barcode}"
        url_shipox = f"https://prodapi.pochta.uz/api/v1/customer/order/{barcode}/history_items"

        max_retries = 2  # Maksimal urinishlar soni
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
                }, timeout=10).json()
                data_shipox = requests.get(url_shipox, headers={
                    'Content-Type': 'application/json',
                    'Accept': 'application/json',
                    'Authorization': f'Bearer {gettoken()}'
                }, timeout=10).json()
            except ConnectTimeout:
                # Agar ulanish timeoutga uchrasa, qayta urinib ko'riladi
                if attempt < max_retries - 1:
                    time.sleep(retry_delay)  # Kutish va yana urinib ko'rish
                else:
                    data_header = {
                        "code": "Server TimeOut Error",
                        "message": "Server Error",
                        "status": "error"
                    }
                    data_shipox = {
                        "code": "Server TimeOut Error",
                        "message": "Server Error",
                        "status": "error"
                    }

        data_header = data_header
        data_shipox = data_shipox
        full_track_temu = []

        if response_data_2[0]["InfoFromEdi"] != None:
            for i in response_data_2[0]["InfoFromEdi"]["TMailitemInfoFromEDI"][0]["Events"]["TMailitemEventEDI"]:
                if i["IPSEventType"]["Name"] == "Items on way":
                    try:
                        gmt_datetime_str = i["GmtDateTime"]
                        local_datetime = datetime.strptime(gmt_datetime_str, "%Y-%m-%dT%H:%M:%S.%f")
                    except ValueError:
                        local_datetime = datetime.strptime(gmt_datetime_str, "%Y-%m-%dT%H:%M:%S")
                    compare_date = change_date  # Faqat sana qismi olinadi
                    local_datetime = local_datetime.date()
                    if local_datetime <= compare_date:
                        for i in response_data_2[0]["InfoFromEdi"]["TMailitemInfoFromEDI"][0]["Events"][
                            "TMailitemEventEDI"]:
                            form = {
                                "EventOffice": {
                                    "Code": "UZTASA",
                                    "Name": "TASHKENT PI1"
                                },
                                "IPSEventType": {
                                    "Code": None,
                                    "Name": None,
                                    "LocalName": None
                                },
                                "date": None,
                                "NonDeliveryReason": {
                                    "Code": None,
                                    "Name": None,
                                    "LocalName": None
                                },
                            }
                            form["EventOffice"]["Name"] = i["EventOffice"]["Name"]
                            form["IPSEventType"]["Name"] = i["IPSEventType"]["Name"]
                            form["IPSEventType"]["Code"] = i["IPSEventType"]["Code"]
                            form["IPSEventType"]["LocalName"] = i["IPSEventType"]["LocalName"]
                            form["date"] = i['GmtDateTime']
                            form["NonDeliveryReason"]["Code"] = i["NonDeliveryReason"]["Code"]
                            form["NonDeliveryReason"]["Name"] = i['NonDeliveryReason']['Name']
                            form["NonDeliveryReason"]["LocalName"] = i['NonDeliveryReason']['LocalName']
                            full_track_temu.append(form)
                        if response_data_2[0]["OperationalMailitems"] != None:
                            for j in \
                                    response_data_2[0]["OperationalMailitems"]["TMailitemInfoFromScanning"][0][
                                        "Events"][
                                        "TMailitemEventScanning"]:
                                form_op = {
                                    "EventOffice": {
                                        "Code": "UZTASA",
                                        "Name": "TASHKENT PI1"
                                    },
                                    "IPSEventType": {
                                        "Code": None,
                                        "Name": None,
                                        "LocalName": None
                                    },
                                    "date": None,
                                    "NonDeliveryReason": {
                                        "Code": None,
                                        "Name": None,
                                        "LocalName": None
                                    },
                                }
                                form_op["EventOffice"]["Name"] = j["EventOffice"]["Name"]
                                form_op["IPSEventType"]["Name"] = j["IPSEventType"]["Name"]
                                form_op["IPSEventType"]["Code"] = j["IPSEventType"]["Code"]
                                form_op["IPSEventType"]["LocalName"] = j["IPSEventType"]["LocalName"]
                                form_op["date"] = j['GmtDateTime']
                                form_op["NonDeliveryReason"]["Code"] = j["NonDeliveryReason"]["Code"]
                                form_op["NonDeliveryReason"]["Name"] = j['NonDeliveryReason']['Name']
                                form_op["NonDeliveryReason"]["LocalName"] = j['NonDeliveryReason']['LocalName']
                                full_track_temu.append(form_op)
                        if not any(item_x["IPSEventType"]["Name"][:12] == "Deliver item" for item_x in
                                   full_track_temu):
                            if data_header['status'] != 'success':
                                return data_header
                            if data_shipox['status'] != 'success':
                                return data_shipox
                            for data in data_shipox['data']["list"]:
                                if data["status"] == 'issued_to_recipient':
                                    form_f = {
                                        "EventOffice": {
                                            "Code": "UZTASA",
                                            "Name": "TASHKENT PI1"
                                        },
                                        "IPSEventType": {
                                            "Code": None,
                                            "Name": None,
                                            "LocalName": None
                                        },
                                        "date": None,
                                        "NonDeliveryReason": {
                                            "Code": None,
                                            "Name": None,
                                            "LocalName": None
                                        },
                                    }
                                    form_f['IPSEventType']["Name"] = "Deliver item"
                                    form_f['IPSEventType']["LocalName"] = "Deliver item"
                                    form_f['IPSEventType']["Code"] = "1257"
                                    form_f["date"] = data['date']
                                    full_track_temu.append(form_f)
                                    break
                                if data["status"] == 'completed':
                                    form_j = {
                                        "EventOffice": {
                                            "Code": "UZTASA",
                                            "Name": "TASHKENT PI1"
                                        },
                                        "IPSEventType": {
                                            "Code": None,
                                            "Name": None,
                                            "LocalName": None
                                        },
                                        "date": None,
                                        "NonDeliveryReason": {
                                            "Code": None,
                                            "Name": None,
                                            "LocalName": None
                                        },
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

                        return full_data

        if response_data_2[0]["OperationalMailitems"] != None:
            for j in response_data_2[0]["OperationalMailitems"]["TMailitemInfoFromScanning"][0]["Events"][
                "TMailitemEventScanning"]:
                if j["IPSEventType"]["Name"] == "Items on way":
                    gmt_datetime_str = j.get("GmtDateTime")
                    if gmt_datetime_str:
                        try:
                            local_datetime = datetime.strptime(gmt_datetime_str, "%Y-%m-%dT%H:%M:%S.%f")
                        except ValueError:
                            local_datetime = datetime.strptime(gmt_datetime_str, "%Y-%m-%dT%H:%M:%S")

                    compare_date = change_date  # Faqat sana qismi olinadi
                    local_datetime = local_datetime.date()
                    if local_datetime <= compare_date:
                        for op in \
                                response_data_2[0]["OperationalMailitems"]["TMailitemInfoFromScanning"][0]["Events"][
                                    "TMailitemEventScanning"]:
                            form = {
                                "EventOffice": {
                                    "Code": "UZTASA",
                                    "Name": "TASHKENT PI1"
                                },
                                "IPSEventType": {
                                    "Code": None,
                                    "Name": None,
                                    "LocalName": None
                                },
                                "date": None,
                                "NonDeliveryReason": {
                                    "Code": None,
                                    "Name": None,
                                    "LocalName": None
                                },
                            }
                            form["EventOffice"]["Name"] = op["EventOffice"]["Name"]
                            form["IPSEventType"]["Name"] = op["IPSEventType"]["Name"]
                            form["IPSEventType"]["Code"] = op["IPSEventType"]["Code"]
                            form["IPSEventType"]["LocalName"] = op["IPSEventType"]["LocalName"]
                            form["date"] = op['GmtDateTime']
                            form["NonDeliveryReason"]["Code"] = op["NonDeliveryReason"]["Code"]
                            form["NonDeliveryReason"]["Name"] = op['NonDeliveryReason']['Name']
                            form["NonDeliveryReason"]["LocalName"] = op['NonDeliveryReason']['LocalName']
                            full_track_temu.append(form)

                        # `InfoFromEdi` bo'lsa, qo'shimcha ma'lumot qo'shamiz
                        if response_data_2[0]["InfoFromEdi"] is not None:
                            for i in response_data_2[0]["InfoFromEdi"]["TMailitemInfoFromEDI"][0]["Events"][
                                "TMailitemEventEDI"]:
                                form_op = {
                                    "EventOffice": {
                                        "Code": "UZTASA",
                                        "Name": "TASHKENT PI1"
                                    },
                                    "IPSEventType": {
                                        "Code": None,
                                        "Name": None,
                                        "LocalName": None
                                    },
                                    "date": None,
                                    "NonDeliveryReason": {
                                        "Code": None,
                                        "Name": None,
                                        "LocalName": None
                                    },
                                }
                                form_op["EventOffice"]["Name"] = i["EventOffice"]["Name"]
                                form_op["IPSEventType"]["Name"] = i["IPSEventType"]["Name"]
                                form_op["IPSEventType"]["Code"] = i["IPSEventType"]["Code"]
                                form_op["IPSEventType"]["LocalName"] = i["IPSEventType"]["LocalName"]
                                form_op["date"] = i['GmtDateTime']
                                form_op["NonDeliveryReason"]["Code"] = i["NonDeliveryReason"]["Code"]
                                form_op["NonDeliveryReason"]["Name"] = i['NonDeliveryReason']['Name']
                                form_op["NonDeliveryReason"]["LocalName"] = i['NonDeliveryReason']['LocalName']
                                full_track_temu.append(form_op)

                        # `Shipox` dan kelgan statusni tekshiramiz
                        if not any(item_x["IPSEventType"]["Name"][:12] == "Deliver item" for item_x in
                                   full_track_temu):
                            if data_header['status'] != 'success':
                                return data_header
                            if data_shipox['status'] != 'success':
                                return data_shipox
                            for data in data_shipox['data']["list"]:
                                if data["status"] == 'issued_to_recipient':
                                    form_f = {
                                        "EventOffice": {"Code": "UZTASA", "Name": "TASHKENT PI1"},
                                        "IPSEventType": {"Code": "1257", "Name": "Deliver item",
                                                         "LocalName": "Deliver item"},
                                        "date": data['date'],
                                        "NonDeliveryReason": {
                                            "Code": None,
                                            "Name": None,
                                            "LocalName": None
                                        },
                                    }
                                    full_track_temu.append(form_f)
                                    break
                                elif data["status"] == 'completed':
                                    form_j = {
                                        "EventOffice": {"Code": "UZTASA", "Name": "TASHKENT PI1"},
                                        "IPSEventType": {"Code": "1257", "Name": "Deliver item",
                                                         "LocalName": "Deliver item"},
                                        "date": data['date'],
                                        "NonDeliveryReason": {
                                            "Code": None,
                                            "Name": None,
                                            "LocalName": None
                                        },
                                    }
                                    full_track_temu.append(form_j)
                                    break

                        # Yakuniy ma'lumotni shakllantiramiz
                        full_data = {
                            "header": data_header,
                            "data": full_track_temu,
                        }

                        return full_data

        if response_data_2[0]["InfoFromEdi"] != None:
            for i in response_data_2[0]["InfoFromEdi"]["TMailitemInfoFromEDI"][0]["Events"]["TMailitemEventEDI"]:
                if i["IPSEventType"]["Name"] == "Items on way":
                    form = {
                        "EventOffice": {
                            "Code": "UZTASA",
                            "Name": "TASHKENT PI1"
                        },
                        "IPSEventType": {
                            "Code": None,
                            "Name": None,
                            "LocalName": None
                        },
                        "date": None,
                        "NonDeliveryReason": {
                            "Code": None,
                            "Name": None,
                            "LocalName": None
                        },
                    }
                    form["IPSEventType"]["Code"] = i["IPSEventType"]["Name"]
                    form["IPSEventType"]["Code"] = i["IPSEventType"]["Code"]
                    form["IPSEventType"]["LocalName"] = i["IPSEventType"]["LocalName"]
                    form["date"] = i['GmtDateTime']
                    form["NonDeliveryReason"]["Code"] = i["NonDeliveryReason"]["Code"]
                    form["NonDeliveryReason"]["Name"] = i['NonDeliveryReason']['Name']
                    form["NonDeliveryReason"]["LocalName"] = i['NonDeliveryReason']['LocalName']
                    full_track_temu.append(form)
                    break

        if response_data_2[0]["OperationalMailitems"] != None:
            for j in response_data_2[0]["OperationalMailitems"]["TMailitemInfoFromScanning"][0]["Events"][
                "TMailitemEventScanning"]:
                if j["IPSEventType"]["Name"] == "Items on way":
                    form = {
                        "EventOffice": {
                            "Code": "UZTASA",
                            "Name": "TASHKENT PI1"
                        },
                        "IPSEventType": {
                            "Code": None,
                            "Name": None,
                            "LocalName": None
                        },
                        "date": None,
                        "NonDeliveryReason": {
                            "Code": None,
                            "Name": None,
                            "LocalName": None
                        },
                    }
                    form["IPSEventType"]["Name"] = j["IPSEventType"]["Name"]
                    form["IPSEventType"]["Code"] = j["IPSEventType"]["Code"]
                    form["IPSEventType"]["LocalName"] = j["IPSEventType"]["LocalName"]
                    form["date"] = j['GmtDateTime']
                    form["NonDeliveryReason"]["Code"] = j["NonDeliveryReason"]["Code"]
                    form["NonDeliveryReason"]["Name"] = j['NonDeliveryReason']['Name']
                    form["NonDeliveryReason"]["LocalName"] = j['NonDeliveryReason']['LocalName']
                    full_track_temu.append(form)
                    break

        ##############
        #############
        ### buyog'i shipox ma'lumotlari
        #############################

        data_header = data_header
        data_shipox = data_shipox
        last_form = None
        lasted_form = None
        if data_header['status'] != 'success':
            if any(item_x["IPSEventType"]["Name"] == "Items on way" for item_x in
                   full_track_temu):
                full_data = {
                    "header": data_header,
                    "data": full_track_temu,
                }
                return full_data
            return data_header
        if data_shipox['status'] != 'success':
            if any(item_x["IPSEventType"]["Name"] == "Items on way" for item_x in
                   full_track_temu):
                full_data = {
                    "header": data_shipox,
                    "data": full_track_temu,
                }
                return full_data
            return data_shipox
        #######################################

        ##### 1-status uchun tekshirish

        for item in data_shipox['data']['list']:
            if item["status"] == 'in_sorting_facility':
                form = {
                    "EventOffice": {
                        "Code": "UZTASA",
                        "Name": "TASHKENT PI1"
                    },
                    "IPSEventType": {
                        "Code": None,
                        "Name": None,
                        "LocalName": None
                    },
                    "date": None,
                    "NonDeliveryReason": {
                        "Code": None,
                        "Name": None,
                        "LocalName": None
                    },
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
                        "Name": "TASHKENT PI1"
                    },
                    "IPSEventType": {
                        "Code": None,
                        "Name": None,
                        "LocalName": None
                    },
                    "date": None,
                    "NonDeliveryReason": {
                        "Code": None,
                        "Name": None,
                        "LocalName": None
                    },
                }
                form['IPSEventType']["Name"] = "Send item to customs"
                form['IPSEventType']["LocalName"] = "Send item to customs"
                form['IPSEventType']["Code"] = "1252"
                form["date"] = item["date"]
                lasted_form = form
        if lasted_form == None:
            if last_form != None:
                form = {
                    "EventOffice": {
                        "Code": "UZTASA",
                        "Name": "TASHKENT PI1"
                    },
                    "IPSEventType": {
                        "Code": None,
                        "Name": None,
                        "LocalName": None
                    },
                    "date": None,
                    "NonDeliveryReason": {
                        "Code": None,
                        "Name": None,
                        "LocalName": None
                    },
                }
                form['IPSEventType']["Name"] = "Send item to customs"
                form['IPSEventType']["LocalName"] = "Send item to customs"
                form['IPSEventType']["Code"] = "1252"
                form["date"] = datetime.fromisoformat(last_form["date"][:19]) + timedelta(minutes=2)
                full_track_temu.append(form)
        else:
            full_track_temu.append(lasted_form)

        ############# 3-status uchun tekshirish

        for item in data_shipox['data']['list']:
            if item["status"] == 'hold_on_at_customs':
                form = {
                    "EventOffice": {
                        "Code": "UZTASA",
                        "Name": "TASHKENT PI1"
                    },
                    "IPSEventType": {
                        "Code": None,
                        "Name": None,
                        "LocalName": None
                    },
                    "date": None,
                    "NonDeliveryReason": {
                        "Code": "I",
                        "Name": None,
                        "LocalName": None
                    },
                }
                form['IPSEventType']["Name"] = "Custom Clearance Exception - Inspection"
                form['IPSEventType']["LocalName"] = "Custom Clearance Exception - Inspection"
                form['IPSEventType']["Code"] = "1262"
                form['NonDeliveryReason']["Name"] = "High-value goods - Official customs declaration required"
                form['NonDeliveryReason'][
                    "LocalName"] = "High-value goods - Official customs declaration required"
                form["date"] = item["date"]
                full_track_temu.append(form)
                break
        #### 4- status uchun tekshirish
        for item in data_shipox['data']['list']:
            if item["status"] == 'returned_from_customs':
                form = {
                    "EventOffice": {
                        "Code": "UZTASA",
                        "Name": "TASHKENT PI1"
                    },
                    "IPSEventType": {
                        "Code": None,
                        "Name": None,
                        "LocalName": None
                    },
                    "date": None,
                    "NonDeliveryReason": {
                        "Code": None,
                        "Name": None,
                        "LocalName": None
                    },
                }
                form['IPSEventType']["Name"] = "Return item from customs"
                form['IPSEventType']["LocalName"] = "Return item from customs"
                form['IPSEventType']["Code"] = "1253"
                form["date"] = item["date"]
                last_form = form

        if last_form:
            full_track_temu.append(last_form)
            form_1 = {
                "EventOffice": {
                    "Code": "UZTASA",
                    "Name": "TASHKENT PI1"
                },
                "IPSEventType": {
                    "Code": None,
                    "Name": None,
                    "LocalName": None
                },
                "date": None,
                "NonDeliveryReason": {
                    "Code": None,
                    "Name": None,
                    "LocalName": None
                },
            }
            form_1['IPSEventType']["Name"] = "Send item to domestic location"
            form_1['IPSEventType']["LocalName"] = "Send item to domestic location"
            form_1['IPSEventType']["Code"] = "1254"
            date_obj = datetime.fromisoformat(last_form["date"][:19]) + timedelta(minutes=10)
            form_1["date"] = date_obj.isoformat()
            full_track_temu.append(form_1)

            ###### yana 20 minut qo'shib qo'shiladi
            form_2 = {
                "EventOffice": {
                    "Code": "UZTASA",
                    "Name": "TASHKENT PI1"
                },
                "IPSEventType": {
                    "Code": None,
                    "Name": None,
                    "LocalName": None
                },
                "date": None,
                "NonDeliveryReason": {
                    "Code": None,
                    "Name": None,
                    "LocalName": None
                },
            }
            form_2['IPSEventType']["Name"] = "Receive item at delivery office"
            form_2['IPSEventType']["LocalName"] = "Receive item at delivery office"
            form_2['IPSEventType']["Code"] = "1255"
            date_obj = datetime.fromisoformat(last_form["date"][:19]) + timedelta(minutes=15)
            form_2["date"] = date_obj.isoformat()
            full_track_temu.append(form_2)

        ############## ready for delivery ga tekshirish

        for item in data_shipox['data']['list']:
            if item["status"] == 'ready_for_delivery':
                for item_x in full_track_temu:
                    if "ready_for_delivery" == item_x["IPSEventType"]["Name"]:
                        item_x["IPSEventType"]["date"] = item["date"]

                if not any(item_x["IPSEventType"]["Name"] == "Return item from customs" for item_x in
                           full_track_temu):
                    form = {
                        "EventOffice": {
                            "Code": "UZTASA",
                            "Name": "TASHKENT PI1"
                        },
                        "IPSEventType": {
                            "Code": None,
                            "Name": None,
                            "LocalName": None
                        },
                        "date": None,
                        "NonDeliveryReason": {
                            "Code": None,
                            "Name": None,
                            "LocalName": None
                        },
                    }
                    form['IPSEventType']["Name"] = "Return item from customs"
                    form['IPSEventType']["LocalName"] = "Return item from customs"
                    form['IPSEventType']["Code"] = "1253"
                    date_obj = datetime.fromisoformat(item["date"][:19]) - timedelta(minutes=20)
                    form["date"] = date_obj.isoformat()
                    full_track_temu.append(form)

                    ########### 10 min qo'shib qo'shiladi
                    form_1 = {
                        "EventOffice": {
                            "Code": "UZTASA",
                            "Name": "TASHKENT PI1"
                        },
                        "IPSEventType": {
                            "Code": None,
                            "Name": None,
                            "LocalName": None
                        },
                        "date": None,
                        "NonDeliveryReason": {
                            "Code": None,
                            "Name": None,
                            "LocalName": None
                        },
                    }
                    form_1['IPSEventType']["Name"] = "Send item to domestic location"
                    form_1['IPSEventType']["LocalName"] = "Send item to domestic location"
                    form_1['IPSEventType']["Code"] = "1254"
                    date_obj = datetime.fromisoformat(item["date"][:19]) - timedelta(minutes=10)
                    form_1["date"] = date_obj.isoformat()
                    full_track_temu.append(form_1)

                    ###### yana 20 minut qo'shib qo'shiladi
                    form_2 = {
                        "EventOffice": {
                            "Code": "UZTASA",
                            "Name": "TASHKENT PI1"
                        },
                        "IPSEventType": {
                            "Code": None,
                            "Name": None,
                            "LocalName": None
                        },
                        "date": None,
                        "NonDeliveryReason": {
                            "Code": None,
                            "Name": None,
                            "LocalName": None
                        },
                    }
                    form_2['IPSEventType']["Name"] = "Receive item at delivery office"
                    form_2['IPSEventType']["LocalName"] = "Receive item at delivery office"
                    form_2['IPSEventType']["Code"] = "1255"
                    date_obj = datetime.fromisoformat(item["date"][:19]) - timedelta(minutes=5)
                    form_2["date"] = date_obj.isoformat()
                    full_track_temu.append(form_2)

                form_3 = {
                    "EventOffice": {
                        "Code": "UZTASA",
                        "Name": "TASHKENT PI1"
                    },
                    "IPSEventType": {
                        "Code": None,
                        "Name": None,
                        "LocalName": None
                    },
                    "date": None,
                    "NonDeliveryReason": {
                        "Code": None,
                        "Name": None,
                        "LocalName": None
                    },
                }
                form_3['IPSEventType']["Name"] = "Ready for Delivery"
                form_3['IPSEventType']["LocalName"] = "Ready for Delivery"
                form_3['IPSEventType']["Code"] = "1263"
                form_3["date"] = item['date']
                full_track_temu.append(form_3)
                break

        wrong_deliverieds = ['receiver_dead', 'not_at_home', 'retention_period_has_expired',
                             'receiver_not_lives_there', 'incomplete_address',
                             'receiver_refuse', 'didnt_appear_on_notice', 'defect',
                             'organization_with_given_address_not_found', 'retention_period_has_expired']
        for item in data_shipox['data']['list']:
            if item["status"] in wrong_deliverieds:
                first_index = next(
                    (i for i, item in enumerate(full_track_temu) if item["IPSEventType"]["Code"] == "1263"),
                    None)
                if first_index is None:
                    form_12 = {
                        "EventOffice": {
                            "Code": "UZTASA",
                            "Name": "TASHKENT PI1"
                        },
                        "IPSEventType": {
                            "Code": None,
                            "Name": None,
                            "LocalName": None
                        },
                        "date": None,
                        "NonDeliveryReason": {
                            "Code": None,
                            "Name": None,
                            "LocalName": None
                        },
                    }
                    form_12['IPSEventType']["Name"] = "Ready for Delivery"
                    form_12['IPSEventType']["LocalName"] = "Ready for Delivery"
                    form_12['IPSEventType']["Code"] = "1263"
                    form_12["date"] = datetime.fromisoformat(item["date"][:19]) - timedelta(minutes=4)
                    full_track_temu.append(form_12)

                form_2 = {
                    "EventOffice": {
                        "Code": "UZTASA",
                        "Name": "TASHKENT PI1"
                    },
                    "IPSEventType": {
                        "Code": None,
                        "Name": None,
                        "LocalName": None
                    },
                    "date": None,
                    "NonDeliveryReason": {
                        "Code": None,
                        "Name": None,
                        "LocalName": None
                    },
                }
                form_2['IPSEventType'][
                    "Name"] = "Unsuccessful item delivery attempt - Addressee not available"
                form_2['IPSEventType'][
                    "LocalName"] = "Unsuccessful item delivery attempt - Addressee not available"
                form_2['IPSEventType']["Code"] = "1256"
                form_2["date"] = item["date"]
                full_track_temu.append(form_2)

                form_3 = {
                    "EventOffice": {
                        "Code": "UZTASA",
                        "Name": "TASHKENT PI1"
                    },
                    "IPSEventType": {
                        "Code": None,
                        "Name": None,
                        "LocalName": None
                    },
                    "date": None,
                    "NonDeliveryReason": {
                        "Code": None,
                        "Name": None,
                        "LocalName": None
                    },
                }
                form_3['IPSEventType'][
                    "Name"] = "Unsuccessful item delivery attempt -Customer request pickup"
                form_3['IPSEventType'][
                    "LocalName"] = "Unsuccessful item delivery attempt -Customer requested pickup"
                form_3['IPSEventType']["Code"] = "1268"
                date_obj = datetime.fromisoformat(item["date"][:19]) + timedelta(minutes=2)
                form_3["date"] = date_obj.isoformat()
                full_track_temu.append(form_3)
                break

            ############### out for deliveryga tekshirish
        for item in data_shipox['data']['list']:
            if item["status"] == 'out_for_delivery':
                first_index = next(
                    (i for i, item in enumerate(full_track_temu) if item["IPSEventType"]["Code"] == "1263"),
                    None)
                if first_index is None:
                    form_3 = {
                        "EventOffice": {
                            "Code": "UZTASA",
                            "Name": "TASHKENT PI1"
                        },
                        "IPSEventType": {
                            "Code": None,
                            "Name": None,
                            "LocalName": None
                        },
                        "date": None,
                        "NonDeliveryReason": {
                            "Code": None,
                            "Name": None,
                            "LocalName": None
                        },
                    }
                    form_3['IPSEventType']["Name"] = "Ready for Delivery"
                    form_3['IPSEventType']["LocalName"] = "Ready for Delivery"
                    form_3['IPSEventType']["Code"] = "1263"
                    form_3["date"] = datetime.fromisoformat(item["date"][:19]) - timedelta(minutes=5)
                    full_track_temu.append(form_3)

                second_index = next(
                    (i for i, item in enumerate(full_track_temu) if item["IPSEventType"]["Code"] == "1256"),
                    None)
                if second_index is not None:
                    form_13 = {
                        "EventOffice": {
                            "Code": "UZTASA",
                            "Name": "TASHKENT PI1"
                        },
                        "IPSEventType": {
                            "Code": None,
                            "Name": None,
                            "LocalName": None
                        },
                        "date": None,
                        "NonDeliveryReason": {
                            "Code": None,
                            "Name": None,
                            "LocalName": None
                        },
                    }
                    form_13['IPSEventType']["Name"] = "Ready for Delivery"
                    form_13['IPSEventType']["LocalName"] = "Ready for Delivery"
                    form_13['IPSEventType']["Code"] = "1263"
                    form_13["date"] = datetime.fromisoformat(item["date"][:19]) - timedelta(minutes=5)
                    full_track_temu.append(form_13)

                form_11 = {
                    "EventOffice": {
                        "Code": "UZTASA",
                        "Name": "TASHKENT PI1"
                    },
                    "IPSEventType": {
                        "Code": None,
                        "Name": None,
                        "LocalName": None
                    },
                    "date": None,
                    "NonDeliveryReason": {
                        "Code": None,
                        "Name": None,
                        "LocalName": None
                    },
                }

                form_11['IPSEventType']["Name"] = "Out for delivery"
                form_11['IPSEventType']["LocalName"] = "Out for delivery"
                form_11['IPSEventType']["Code"] = "1264"
                form_11["date"] = item['date']
                full_track_temu.append(form_11)
                break

        ######## delivered uchun tekshirish
        for item in data_shipox['data']['list']:
            if item["status"] == 'completed':
                if not any(item_x["IPSEventType"]["Name"] == "Out for delivery" for item_x in full_track_temu):
                    form_2 = {
                        "EventOffice": {
                            "Code": "UZTASA",
                            "Name": "TASHKENT PI1"
                        },
                        "IPSEventType": {
                            "Code": None,
                            "Name": None,
                            "LocalName": None
                        },
                        "date": None,
                        "NonDeliveryReason": {
                            "Code": None,
                            "Name": None,
                            "LocalName": None
                        },
                    }
                    form_2['IPSEventType']["Name"] = "Out for delivery"
                    form_2['IPSEventType']["LocalName"] = "Out for delivery"
                    form_2['IPSEventType']["Code"] = "1264"
                    date_obj = datetime.fromisoformat(item["date"][:19]) - timedelta(minutes=5)
                    form_2["date"] = date_obj.isoformat()
                    full_track_temu.append(form_2)

                if not any(item_x["IPSEventType"]["Name"] == "Ready for Delivery" for item_x in
                           full_track_temu):
                    form_3 = {
                        "EventOffice": {
                            "Code": "UZTASA",
                            "Name": "TASHKENT PI1"
                        },
                        "IPSEventType": {
                            "Code": None,
                            "Name": None,
                            "LocalName": None
                        },
                        "date": None,
                        "NonDeliveryReason": {
                            "Code": None,
                            "Name": None,
                            "LocalName": None
                        },
                    }
                    form_3['IPSEventType']["Name"] = "Ready for Delivery"
                    form_3['IPSEventType']["LocalName"] = "Ready for Delivery"
                    form_3['IPSEventType']["Code"] = "1263"
                    date_obj = datetime.fromisoformat(item["date"][:19]) - timedelta(minutes=10)
                    form_3["date"] = date_obj.isoformat()
                    full_track_temu.append(form_3)

                form_j = {
                    "EventOffice": {
                        "Code": "UZTASA",
                        "Name": "TASHKENT PI1"
                    },
                    "IPSEventType": {
                        "Code": None,
                        "Name": None,
                        "LocalName": None
                    },
                    "date": None,
                    "NonDeliveryReason": {
                        "Code": None,
                        "Name": None,
                        "LocalName": None
                    },
                }
                form_j['IPSEventType']["Name"] = "Deliver item"
                form_j['IPSEventType']["LocalName"] = "Deliver item"
                form_j['IPSEventType']["Code"] = "1257"
                form_j["date"] = item['date']
                full_track_temu.append(form_j)
                break

            if item["status"] == 'issued_to_recipient':
                if not any(item_x["IPSEventType"]["Name"] == "Out for delivery" for item_x in full_track_temu):
                    form_2 = {
                        "EventOffice": {
                            "Code": "UZTASA",
                            "Name": "TASHKENT PI1"
                        },
                        "IPSEventType": {
                            "Code": None,
                            "Name": None,
                            "LocalName": None
                        },
                        "date": None,
                        "NonDeliveryReason": {
                            "Code": None,
                            "Name": None,
                            "LocalName": None
                        },
                    }
                    form_2['IPSEventType']["Name"] = "Out for delivery"
                    form_2['IPSEventType']["LocalName"] = "Out for delivery"
                    form_2['IPSEventType']["Code"] = "1264"
                    date_obj = datetime.fromisoformat(item["date"][:19]) - timedelta(minutes=5)
                    form_2["date"] = date_obj.isoformat()
                    full_track_temu.append(form_2)

                if not any(item_x["IPSEventType"]["Name"] == "Ready for Delivery" for item_x in
                           full_track_temu):
                    form_2 = {
                        "EventOffice": {
                            "Code": "UZTASA",
                            "Name": "TASHKENT PI1"
                        },
                        "IPSEventType": {
                            "Code": None,
                            "Name": None,
                            "LocalName": None
                        },
                        "date": None,
                        "NonDeliveryReason": {
                            "Code": None,
                            "Name": None,
                            "LocalName": None
                        },
                    }
                    form_2['IPSEventType']["Name"] = "Ready for Delivery"
                    form_2['IPSEventType']["LocalName"] = "Ready for Delivery"
                    form_2['IPSEventType']["Code"] = "1263"
                    date_obj = datetime.fromisoformat(item["date"][:19]) - timedelta(minutes=10)
                    form_2["date"] = date_obj.isoformat()
                    full_track_temu.append(form_2)

                form_f = {
                    "EventOffice": {
                        "Code": "UZTASA",
                        "Name": "TASHKENT PI1"
                    },
                    "IPSEventType": {
                        "Code": None,
                        "Name": None,
                        "LocalName": None
                    },
                    "date": None,
                    "NonDeliveryReason": {
                        "Code": None,
                        "Name": None,
                        "LocalName": None
                    },
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
                        "Name": "TASHKENT PI1"
                    },
                    "IPSEventType": {
                        "Code": None,
                        "Name": None,
                        "LocalName": None
                    },
                    "date": None,
                    "NonDeliveryReason": {
                        "Code": None,
                        "Name": None,
                        "LocalName": None
                    },
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
                if not any(item_x["IPSEventType"]["Name"] == "On the way to sender" for item_x in
                           full_track_temu):
                    form_s = {
                        "EventOffice": {
                            "Code": "UZTASA",
                            "Name": "TASHKENT PI1"
                        },
                        "IPSEventType": {
                            "Code": None,
                            "Name": None,
                            "LocalName": None
                        },
                        "date": None,
                        "NonDeliveryReason": {
                            "Code": None,
                            "Name": None,
                            "LocalName": None
                        },
                    }
                    form_s['IPSEventType']["Name"] = "On the way to sender"
                    form_s['IPSEventType']["LocalName"] = "On the way to sender"
                    form_s['IPSEventType']["Code"] = "1266"
                    date_obj = datetime.fromisoformat(item["date"][:19]) - timedelta(minutes=5)
                    form_s["date"] = date_obj.isoformat()
                    full_track_temu.append(form_s)
                form_f = {
                    "EventOffice": {
                        "Code": "UZTASA",
                        "Name": "TASHKENT PI1"
                    },
                    "IPSEventType": {
                        "Code": None,
                        "Name": None,
                        "LocalName": None
                    },
                    "date": None,
                    "NonDeliveryReason": {
                        "Code": None,
                        "Name": None,
                        "LocalName": None
                    },
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

        return full_data
