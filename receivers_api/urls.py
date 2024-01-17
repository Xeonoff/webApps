from django.contrib import admin
from django.urls import path
from django.urls import path, include
from rest_framework import routers
from receivers_selection_api.views.viewReceiver import *
from receivers_selection_api.views.viewSending import *
from receivers_selection_api.views.viewSendingReceiver import *
from receivers_selection_api.views.authView import *
from receivers_selection_api.views.viewSendingUpd import *
from rest_framework import permissions
from django.urls import path, include
from drf_yasg.views import get_schema_view
from drf_yasg import openapi

router = routers.DefaultRouter()

schema_view = get_schema_view(
   openapi.Info(
      title="Snippets API",
      default_version='v1',
      description="Test description",
      terms_of_service="https://www.google.com/policies/terms/",
      contact=openapi.Contact(email="contact@snippets.local"),
      license=openapi.License(name="BSD License"),
   ),
   public=True,
   permission_classes=(permissions.AllowAny,),
)

router.register(r'users', UserViewSet, basename='user')

urlpatterns = [
    path('send/', update_sending_status, name='sending-status-update'),
    path('api-auth/', include('rest_framework.urls', namespace='rest_framework')),
    path('admin/', admin.site.urls),
    path('', include(router.urls)),
    
    path('swagger/', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),

    path('accounts/login/', login_view, name='login'),
    path('accounts/logout/', logout_view, name='logout'),
    path('accounts/check/', check, name='check'),

    path(r'receivers/', process_Receiverlist.as_view(), name='receivers-process'),
    path(r'receivers/<int:pk>/', procces_receiver_detail.as_view(), name='receiver-detail-process'),

    path(r'links/', process_MM.as_view(), name = 'links'),
    
    path(r'sending/', process_SendingList.as_view(), name='sending-list-process'),
    path(r'sending/current/', Current_Inp_View.as_view(), name='request-current'),
    path(r'sending/<int:pk>/', process_sending_detail.as_view(), name='sending-detail-process'),
]
