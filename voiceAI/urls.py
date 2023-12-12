from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('process_command/', views.process_command, name='process_command'),
]
