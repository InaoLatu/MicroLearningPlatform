from django.contrib import admin
from django.urls import path, include
import users_manager.views as users_manager_views
import micro_content_manager.views as mc_views

# API
from rest_framework import routers
from rest_framework.urlpatterns import format_suffix_patterns

router = routers.DefaultRouter()
router.register(r'units', mc_views.UnitViewSet)
router.register(r'users', users_manager_views.UserViewSet)
# router.register('^units/{unit}/$', mc_views.unit_detail, basename="unit-detail")

urlpatterns = [
    path('api/', include(router.urls)),
    path('units/', mc_views.UnitList.as_view()),
    path('units/<str:unit>/', mc_views.UnitDetail.as_view()),
    path('micro_content_manager/', include('micro_content_manager.urls')),
    path('admin/', admin.site.urls),
    path('user_page/', users_manager_views.HomeView.as_view(), name='user_page'),
    path('', users_manager_views.LogInView.as_view(), name='login'),
    path('accounts/', include('users_manager.urls')),
    path('accounts/', include('django.contrib.auth.urls')),
    path('microcontent', mc_views.microcontent, name='micro_content'),
]

#API
# urlpatterns = format_suffix_patterns(urlpatterns)
#