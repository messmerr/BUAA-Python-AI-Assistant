import uuid
from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    """用户模型，继承Django内置的AbstractUser"""
    USER_ROLE_CHOICES = (
        ('teacher', '教师'),
        ('student', '学生'),
    )

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    role = models.CharField(max_length=10, choices=USER_ROLE_CHOICES, default='student')
    real_name = models.CharField(max_length=50, blank=True, verbose_name='真实姓名')
    student_id = models.CharField(max_length=20, blank=True, null=True, verbose_name='学号')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='更新时间')

    class Meta:
        db_table = 'users'
        verbose_name = '用户'
        verbose_name_plural = '用户'

    def __str__(self):
        return f"{self.username} ({self.get_role_display()})"
