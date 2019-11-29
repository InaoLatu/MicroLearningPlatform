from django.contrib import admin
from django.urls import path, include
import users_manager.views as users_manager_views
import micro_content_manager.views as mc_views

urlpatterns = [
    path('micro_content_manager/', include('micro_content_manager.urls')),
    path('admin/', admin.site.urls),
    path('user_page/', users_manager_views.HomeView.as_view(), name='user_page'),
    path('', users_manager_views.LogInView.as_view(), name='login'),
    path('accounts/', include('users_manager.urls')),
    path('accounts/', include('django.contrib.auth.urls')),
    path('json', mc_views.json, name='json'),

]
