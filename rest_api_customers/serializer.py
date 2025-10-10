from models.models import CustomUser
from rest_framework import serializers
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer


class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    def validate(self, attrs):
        data = super().validate(attrs)
        # Faqat `access` tokenni olish va foydalanuvchi ma'lumotlarini qaytarish
        response_data = {
            "data": {
                "id_token": data.get("access"),
                "user": {
                    "marketplace_id": 1,
                    "user_id": self.user.id,
                    "login": self.user.phone_number,
                    "version": 0,
                    "first_name": self.user.first_name,
                    "last_name": self.user.last_name,
                    "region": self.user.region,
                    "district": self.user.district,
                    "index": self.user.post_index,
                    "image": self.user.image.url if self.user.image else None,
                    "activated": self.user.is_active,
                    "created_at": self.user.created_at,
                }
            },
            "status": "success"
        }
        if self.user.static_token:
            response_data["data"]["static_token"] = self.user.static_token
        return response_data


class CustomUserSerializer(serializers.ModelSerializer):
    """
    Userlar ro'yhatdan o'tishi uchun mo'ljallangan serializer class
    """
    class Meta:
        model = CustomUser
        fields = ('phone_number', 'first_name', 'last_name', 'password')
