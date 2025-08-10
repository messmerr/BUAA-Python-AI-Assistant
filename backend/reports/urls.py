from django.urls import path
from . import views

app_name = 'reports'

urlpatterns = [
    # 学习报告
    path('generate/', views.generate_report, name='generate_report'),
    path('list/', views.list_reports, name='list_reports'),
    path('<uuid:report_id>/', views.get_report_detail, name='report_detail'),
    
    # 班级报告 - 确保这个路由存在且正确
    path('class/generate/', views.generate_class_report, name='generate_class_report'),
]

