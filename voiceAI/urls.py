from django.urls import path
from . import views
from .views import new_thread

urlpatterns = [
    path('', views.index, name='index'),
    path('process_command/', views.process_command, name='process_command'),
    path('voiceAI/new_thread/', new_thread, name='new_thread'),
]
