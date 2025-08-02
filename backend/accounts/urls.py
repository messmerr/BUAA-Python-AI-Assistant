from django.urls import path
from . import views

app_name = 'accounts'

urlpatterns = [
    # 用户认证
    path('register/', views.register_view, name='register'),
    path('login/', views.login_view, name='login'),
    path('refresh/', views.CustomTokenRefreshView.as_view(), name='token_refresh'),
    
    # 用户信息
    path('profile/', views.profile_view, name='profile'),
    path('students/', views.get_students, name='get_students'),  # GET - 获取学生列表
]
