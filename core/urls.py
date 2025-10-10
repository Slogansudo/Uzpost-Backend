
from django.contrib import admin
from django.urls import path, include, re_path
from django.conf import settings
from django.conf.urls.static import static
from rest_framework_simplejwt.views import (TokenObtainPairView,
                                            TokenRefreshView)
from django.conf.urls import handler404
from django.views.static import serve


from django.contrib.auth.decorators import login_required
from .views import protected_media

handler404 = 'db_models.views.custom_404'

urlpatterns = [
    path('_manage/admin/', admin.site.urls),
    path('api/v1/admin/', include('rest_api.urls')),
    path('api/v1/public/', include('rest_api_customers.urls')),
    path('api/v1/manage/', include('rest_api_management.urls')),
    path('api/v1/calculator/', include('calculator.urls')),
<<<<<<< HEAD

=======
    path('api/v1/maps/', include('maps.urls')),
>>>>>>> 2d32d04 (full complated uzpost backend)
    #path('api/v1/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    #path('api/v1/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('', include('models.urls')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
else:
    urlpatterns += [
        re_path(r'^download_media/(?P<path>.*)$', protected_media, name='protected_media'),
        re_path(r'^media/(?P<path>.*)$', serve, {'document_root': settings.MEDIA_ROOT}),
        re_path(r'^static/(?P<path>.*)$', serve, {'document_root': settings.STATIC_ROOT}),
    ]
