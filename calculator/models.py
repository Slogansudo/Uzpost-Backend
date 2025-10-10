from django.db import models
<<<<<<< HEAD


class Warehouse(models.Model):
    warehouse_name = models.CharField(max_length=255)        # Ombor nomi
    warehouse_lat = models.FloatField()                      # Latitude
    warehouse_lon = models.FloatField()                      # Longitude
    city_id = models.IntegerField()                          # Shahar ID
    city_name = models.CharField(max_length=100)             # Shahar nomi
    city_code = models.CharField(max_length=100)              # Shahar kodi
    region_name = models.CharField(max_length=100)           # Viloyat nomi
    index = models.CharField(max_length=20)                  # Indeks

    def __str__(self):
        return self.warehouse_name

    class Meta:
        ordering = ('id',)
        db_table = 'warehouse'
        indexes = [
            models.Index(fields=['id'])
        ]


class FullIndex(models.Model):
    index = models.CharField(max_length=20)
    region = models.CharField(max_length=100)
    geolocation = models.TextField(null=True, blank=True)
    comments = models.TextField(null=True, blank=True)

    class Meta:
        ordering = ('id',)
        db_table = 'fullindex'
        indexes = [
            models.Index(fields=['id'])
        ]


class PostalOffice(models.Model):
    ems_international_post = models.CharField(max_length=500, null=True, blank=True)
    one_step = models.CharField(max_length=500, null=True, blank=True)
    index = models.CharField(max_length=200, null=True, blank=True)
    geolocation = models.TextField(null=True, blank=True)
    comments = models.TextField(null=True, blank=True)
    lat = models.CharField(max_length=200, null=True, blank=True)
    lng = models.CharField(max_length=200, null=True, blank=True)
    name_uz = models.CharField(max_length=500, null=True, blank=True)
    name_eng = models.CharField(max_length=500, null=True, blank=True)
    name_ru = models.CharField(max_length=500, null=True, blank=True)
    region = models.CharField(max_length=500, null=True, blank=True)
    city = models.CharField(max_length=500, null=True, blank=True)
    district = models.CharField(max_length=500, blank=True, null=True)
    mfy = models.CharField(max_length=500, null=True, blank=True)
    street = models.CharField(max_length=500, blank=True, null=True)
    village = models.CharField(max_length=500, blank=True, null=True)
    house = models.CharField(max_length=500, blank=True, null=True)
    apartment = models.CharField(max_length=500, blank=True, null=True)
    working_days = models.CharField(max_length=500, blank=True, null=True)
    working_days_2 = models.CharField(max_length=500, blank=True, null=True)
    working_hours = models.CharField(max_length=500, blank=True, null=True)
    working_hours_2 = models.CharField(max_length=500, blank=True, null=True)
    weekend_days = models.CharField(max_length=500, blank=True, null=True)

    class Meta:
        ordering = ('id',)
        db_table = 'postaloffice'
        indexes = [
            models.Index(fields=['id'])
        ]

=======
from models.models import CustomUser


class OrderCart(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name="orders")
    weight = models.FloatField()
    barcode = models.CharField(max_length=400)
    fromjurisdiction = models.CharField(max_length=500)
    tojurisdiction = models.CharField(max_length=500)
    from_phone_number = models.CharField(max_length=100)
    to_phone_number = models.CharField(max_length=100)
    full_name = models.CharField(max_length=250)
    from_country_code = models.CharField(max_length=400)
    to_country_code = models.CharField(max_length=400)
    price = models.FloatField()
    price_code = models.CharField(max_length=400)
    payment_type = models.CharField(max_length=400)
    shipment_type = models.CharField(max_length=400)
    shipox_created_at = models.CharField(max_length=400)
    shipox_last_status_date = models.CharField(max_length=400)
    order_status = models.BooleanField(default=True)
    archiving_status = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ('id',)
        db_table = 'ordercart'
        indexes = [
            models.Index(fields=['id', "user", 'barcode', 'created_at', "weight", 'price', "created_at", "archiving_status"])
        ]
>>>>>>> 2d32d04 (full complated uzpost backend)
