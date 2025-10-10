from models.models import CustomUser
from django.contrib.auth.hashers import make_password
import requests
import time
from rest_framework.decorators import action
from django.contrib.auth.models import Group, Permission
from requests.auth import HTTPBasicAuth
from models.models import CheckSMS
from random import randint
import uuid
from django.utils import timezone
from datetime import datetime
from datetime import timedelta
from calculator.models import OrderCart
from dotenv import load_dotenv
import os
from django.db.models import Q

load_dotenv()


def send_sms(phone):
    phone_number = phone
    database_number = f"+998{phone_number}"
    last_sms = CheckSMS.objects.filter(phone_number=database_number).order_by('-created_at').first()
    if last_sms:
        if last_sms.status == True:
            last_sms.status = False
            last_sms.save()
        if last_sms:
            time_diff = timezone.now() - last_sms.created_at
            if time_diff < timedelta(minutes=3):
                remaining_time = timedelta(minutes=3) - time_diff
                return f'Please try again after {remaining_time} minutes.'
    sms_code = randint(1000, 9999)
    massage_id = str(uuid.uuid4())
    post_sms = {
        "messages":
            [
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
    results = requests.post("https://send.smsxabar.uz/broker-api/send", json=post_sms,
                            headers={'content-type': 'application/json'},
                            auth=HTTPBasicAuth("uzpost", "q%0-E5~3T#i&"))

    if results.status_code == 200:
        CheckSMS.objects.create(
            massage_id=massage_id,
            code=sms_code,
            phone_number=database_number)
        return results
    return 'Something went wrong'
