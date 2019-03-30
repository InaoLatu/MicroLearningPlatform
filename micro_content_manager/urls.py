from django.urls import path

from . import views

app_name = 'micro_content_manager'
urlpatterns = [
    path('', views.index, name='index'),
    path('newMicroContent/<int:v>/<int:q>', views.MicroContentCreationView.as_view(), name='micro_content_creation'),
    path('micro_content_data/<int:id>/', views.MicroContentInfoView.as_view(), name='micro_content_data'),
    path('mc_search/', views.MicroContentSearchView.as_view(), name='micro_content_search'),
    path('edit/<int:pk>', views.MicroContentEditView.as_view(), name='edit'),
    path('doTheMicroContent/<int:id>', views.DoTheMicroContentView.as_view(), name='do_the_micro_content'),
    path('createSelection/', views.CreateSelectionView.as_view(), name='create_selection'),
    path('vote', views.vote, name='micro_content_vote'),
    path('store/<int:questions>', views.StoreView.as_view(), name='store'),
    path('update', views.update, name='update'),
    path('download', views.download, name='download'),
    path('json', views.json, name='json'),
]