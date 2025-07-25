from django.urls import path
from . import views

app_name = 'reports'

urlpatterns = [
    # 学习报告
    path('generate/', views.generate_report, name='generate_report'),  # POST - 生成学习报告
    path('list/', views.list_reports, name='list_reports'),  # GET - 获取报告列表
    path('<uuid:report_id>/', views.get_report_detail, name='report_detail'),  # GET - 获取报告详情
]
