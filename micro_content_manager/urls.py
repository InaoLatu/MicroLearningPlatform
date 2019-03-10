from django.urls import path

from . import views

app_name = 'micro_content_manager'
urlpatterns = [
    path('', views.index, name='index'),
    path('newMC/', views.MicroContentCreationView.as_view(), name='micro_content_creation'),
    path('create', views.create, name='create'),
    path('edit', views.edit, name='edit'),
    path('store', views.store, name='store'),
    path('update', views.update, name='update'),
    path('download', views.download, name='download'),
    path('json', views.json, name='json'),
]