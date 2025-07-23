from django.urls import path
from . import views

app_name = 'qa'

urlpatterns = [
    # 智能答疑
    path('questions/', views.submit_question, name='submit_question'),  # POST - 提交问题
    path('questions/list/', views.list_questions, name='list_questions'),  # GET - 获取问题列表
    path('questions/<uuid:question_id>/', views.get_question_detail, name='question_detail'),  # GET - 获取问题详情
]
