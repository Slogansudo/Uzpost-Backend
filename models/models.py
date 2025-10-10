from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.db import models
import uuid



class CustomUserManager(BaseUserManager):
    def create_user(self, phone_number, first_name, last_name, password=None, **extra_fields):
        if not phone_number:
            raise ValueError('The Phone Number field must be set')
        user = self.model(phone_number=phone_number, first_name=first_name, last_name=last_name, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, phone_number, first_name, last_name, password=None, **extra_fields):
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('is_staff', True)
        return self.create_user(phone_number, first_name, last_name, password, **extra_fields)

    def get_by_natural_key(self, phone_number):
        return self.get(phone_number=phone_number)


class CustomUser(AbstractBaseUser, PermissionsMixin):
    static_token = models.CharField(max_length=100, unique=True, null=True, blank=True)
    phone_number = models.CharField(max_length=15, unique=True)
    first_name = models.CharField(max_length=30, null=True, blank=True)
    last_name = models.CharField(max_length=30, null=True, blank=True)
    image = models.ImageField(upload_to='users/', null=True, blank=True)
    region = models.CharField(max_length=50, null=True, blank=True)
    district = models.CharField(max_length=50, null=True, blank=True)
    post_index = models.CharField(max_length=50, null=True, blank=True)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    is_superuser = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    objects = CustomUserManager()

    USERNAME_FIELD = 'phone_number'
    REQUIRED_FIELDS = ['first_name', 'last_name']

    class Meta:
        db_table = 'customuser'

    def __str__(self):
        return self.phone_number

    def has_perm(self, perm, obj=None):
        return self.is_superuser

    def has_module_perms(self, app_label):
        return self.is_superuser


class UsersRequests(models.Model):
    full_name = models.CharField(max_length=50)
    phone_number = models.CharField(max_length=15)
    title = models.CharField(max_length=150)
    description = models.TextField()
    status = models.CharField(max_length=50)
    created_at = models.DateTimeField(auto_now_add=True)
    last_updated = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'users_requests'
        ordering = ('-id',)

    def __str__(self):
        return self.title


class IPAddressLog(models.Model):
    ip_address = models.GenericIPAddressField()
    request_count = models.IntegerField(default=0)
    last_request_time = models.DateTimeField(auto_now=True)
    url = models.CharField(max_length=255)

    class Meta:
        db_table = 'ipaddress_log'
        ordering = ('id', )


class CheckSMS(models.Model):
    massage_id = models.CharField(max_length=255, primary_key=True)
    code = models.CharField(max_length=40)
    phone_number = models.CharField(max_length=15)
    created_at = models.DateTimeField(auto_now_add=True)
    status = models.BooleanField(default=False)

    class Meta:
        db_table = 'checksms'
        indexes = [
            models.Index(fields=['phone_number', 'massage_id'])
        ]
