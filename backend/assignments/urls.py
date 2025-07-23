from django.urls import path
from . import views

app_name = 'assignments'

urlpatterns = [
    # 作业管理
    path('', views.create_assignment, name='create_assignment'),  # POST - 创建作业
    path('list/', views.list_assignments, name='list_assignments'),  # GET - 获取作业列表
    path('<uuid:assignment_id>/', views.get_assignment_detail, name='assignment_detail'),  # GET - 获取作业详情
    
    # 作业提交
    path('<uuid:assignment_id>/submissions/', views.submit_assignment, name='submit_assignment'),  # POST - 提交作业
    path('<uuid:assignment_id>/submissions/<uuid:submission_id>/', views.get_submission_result, name='submission_result'),  # GET - 获取批改结果
]
