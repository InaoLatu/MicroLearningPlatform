from django.conf.urls import url
from django.urls import path

from . import views

app_name = 'users_manager'
urlpatterns = [
    path('user_data/', views.UserDataView.as_view(), name='user_data'),
    path('edit_user_data/<int:id>', views.EditUserDataView.as_view(), name='edit_user_data'),
    path('password_change/', views.change_password, name='password_change'),
    path('login', views.LogInView.as_view(), name='logIn'),
    path('signup/', views.SignUp.as_view(), name='signup'),
    path('reset/<uidb64>/<token>/', views.PasswordResetConfirmView.as_view(),
         name='password_reset_confirm'),
    url(r'^activate/(?P<uidb64>[0-9A-Za-z_\-]+)/(?P<token>[0-9A-Za-z]{1,13}-[0-9A-Za-z]{1,20})/$',
        views.activate, name='activate')
]
