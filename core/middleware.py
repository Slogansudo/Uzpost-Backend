#
# from django.utils.deprecation import MiddlewareMixin
# from django.utils import timezone
# from models.models import IPAddressLog
#
#
# class LogIPMiddleware(MiddlewareMixin):
#     def process_request(self, request):
#         ip = self.get_client_ip(request)
#         url = request.path
#         if ip and url:
#             ip_log, created = IPAddressLog.objects.get_or_create(ip_address=ip, url=url)
#             ip_log.request_count += 1
#             ip_log.last_request_time = timezone.now()
#             ip_log.save()
#
#     def get_client_ip(self, request):
#         x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
#         if x_forwarded_for:
#             ip = x_forwarded_for.split(',')[0].strip()
#             #ip = x_forwarded_for.split(',')[0]
#         else:
#             ip = request.META.get('REMOTE_ADDR')
#         return ip
from django.utils.deprecation import MiddlewareMixin
from django.utils import timezone


# from models.models import IPAddressLog  # IP manzil loglarini ushlashni xohlamasangiz, import qilish shart emas


class LogIPMiddleware(MiddlewareMixin):
    def process_request(self, request):
        # IP manzilini olish
        ip = self.get_client_ip(request)
        url = request.path

        # Ushbu kodni o'chirish yoki kommentga olish
        # if ip and url:
        #     ip_log, created = IPAddressLog.objects.get_or_create(ip_address=ip, url=url)
        #     ip_log.request_count += 1
        #     ip_log.last_request_time = timezone.now()
        #     ip_log.save()

    def get_client_ip(self, request):
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0].strip()
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip


from django.conf import settings
from django.http import JsonResponse
from .help import Usersstatictokens


def static_token_required(view_func):
    def wrapped_view(request, *args, **kwargs):
        token = request.headers.get("X-API-Token")
        path = request.path
        if request.method == "POST" and path == "/api/v1/public/authenticate/":
            return view_func(request, *args, **kwargs)
        if request.method == "POST" and path == "/api/v1/public/register/":
            return view_func(request, *args, **kwargs)
        if request.method in ["GET", "POST", "PUT", "DELETE"] and path.startswith("/_manage/admin/"):
            return view_func(request, *args, **kwargs)
        if request.method in ["GET", "POST", "PUT", "DELETE"] and path.startswith("/api/v1/public/test/"):
            return view_func(request, *args, **kwargs)
        if request.method in ["GET", "POST", "PUT", "DELETE"] and path.startswith("/api/v1/public/track/"):
            return view_func(request, *args, **kwargs)
        if token in Usersstatictokens():
            return view_func(request, *args, **kwargs)
        if token in ["abdullo"]:
            return view_func(request, *args, **kwargs)
        return JsonResponse({"error": "Unauthorized"}, status=401)
    return wrapped_view


