from django.urls import path
from . import views

urlpatterns = [
    path('users/', views.get_chat_users, name='chat-users'),
    path('messages/<str:user_id>/', views.get_chat_messages, name='chat-messages'),
    path('messages/', views.send_message, name='send-message'),
    path('messages/<str:user_id>/read/', views.mark_messages_read, name='mark-read'),
    path('unread-count/', views.get_unread_count, name='unread-count'),
]
