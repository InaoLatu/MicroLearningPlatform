from django.urls import path

from . import views
from users_manager import views as user_views
from django.conf import settings
from django.conf.urls.static import static


app_name = 'micro_content_manager'
urlpatterns = [
    path('', user_views.HomeView.as_view()),
    path('newMicroContent/<int:v>/<int:q>', views.MicroContentCreationView.as_view(), name='micro_content_creation'),
    path('micro_content_data/<int:id>/', views.MicroContentInfoView.as_view(), name='micro_content_data'),
    path('mc_search/<int:tab>', views.MicroContentSearchView.as_view(), name='micro_content_search'),
    path('copy/<int:id>', views.MicroContentCopyView.as_view(), name='copy'),
    path('delete/<int:id>', views.MicroContentDeleteView.as_view(), name='delete'),
    path('edit/<int:pk>', views.MicroContentEditView.as_view(), name='edit'),
    path('doTheMicroContent/<int:id>', views.DoTheMicroContentView.as_view(), name='do_the_micro_content'),
    path('createSelection/', views.CreateSelectionView.as_view(), name='create_selection'),
    path('recordVideo/', views.RecordVideoView.as_view(), name='record_video'),
    path('vote', views.vote, name='micro_content_vote'),
    path('store/<int:questions>/', views.StoreView.as_view(), name='store'),
    path('test', views.TestView.as_view(), name='test'),
    path('update', views.update, name='update'),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
