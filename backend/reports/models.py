import uuid
from django.db import models
from django.conf import settings


class LearningReport(models.Model):
    """学习报告模型"""
    PERIOD_CHOICES = [
        ('week', '一周'),
        ('month', '一个月'),
        ('semester', '一学期'),
        ('all', '全部时间'),
    ]

    STATUS_CHOICES = [
        ('generating', '生成中'),
        ('completed', '已完成'),
        ('failed', '生成失败'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    student = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='learning_reports',
        verbose_name='学生'
    )
    generated_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='generated_reports',
        verbose_name='生成者',
        help_text='可以是学生自己或教师'
    )
    period = models.CharField(max_length=20, choices=PERIOD_CHOICES, verbose_name='时间段')
    subjects = models.JSONField(default=list, verbose_name='科目列表')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='generating', verbose_name='状态')

    # 统计数据
    total_assignments = models.IntegerField(default=0, verbose_name='总作业数')
    completed_assignments = models.IntegerField(default=0, verbose_name='已完成作业数')
    average_score = models.FloatField(default=0.0, verbose_name='平均得分')
    total_questions = models.IntegerField(default=0, verbose_name='总提问数')

    # 报告内容
    report_content = models.TextField(blank=True, verbose_name='报告内容')

    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='更新时间')

    class Meta:
        db_table = 'learning_reports'
        verbose_name = '学习报告'
        verbose_name_plural = '学习报告'
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.student.real_name} - {self.get_period_display()} - {self.created_at.strftime('%Y-%m-%d')}"
