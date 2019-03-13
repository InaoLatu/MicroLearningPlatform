from django.urls import path

from . import views

app_name = 'micro_content_manager'
urlpatterns = [
    path('', views.index, name='index'),
    path('newMC/', views.MicroContentCreationView.as_view(), name='micro_content_creation'),
    path('micro_content_data/<int:id>/', views.MicroContentInfoView.as_view(), name='micro_content_data'),
    path('mc_search/', views.MicroContentSearchView.as_view(), name='micro_content_search'),
    path('create', views.create, name='create'),
    path('edit', views.edit, name='edit'),
    path('store', views.store, name='store'),
    path('update', views.update, name='update'),
    path('download', views.download, name='download'),
    path('json', views.json, name='json'),
]