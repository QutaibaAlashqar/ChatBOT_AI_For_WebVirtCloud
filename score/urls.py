from django.urls import path
from . import views


urlpatterns = [

    path('', views.index, name='index'),
    path('chat/', views.chat_with_bot, name='chat_with_bot'),
    path('cancel/', views.cancel_process, name='cancel_process'),
]