from django.urls import path
from . import views

app_name = 'qa'

urlpatterns = [
    # 新的聊天API
    path('chat/', views.chat_message, name='chat_message'),  # POST - 发送聊天消息
    path('sessions/', views.list_sessions, name='list_sessions'),  # GET - 获取会话列表
    path('sessions/<uuid:session_id>/', views.get_session_detail, name='session_detail'),  # GET - 获取会话详情

    # 保留旧的API以兼容现有前端
    path('questions/', views.submit_question, name='submit_question'),  # POST - 提交问题
    path('questions/list/', views.list_questions, name='list_questions'),  # GET - 获取问题列表
    path('questions/<uuid:question_id>/', views.get_question_detail, name='question_detail'),  # GET - 获取问题详情
]
