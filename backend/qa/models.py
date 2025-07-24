import uuid
from django.db import models
from django.conf import settings


class QASession(models.Model):
    """问答会话模型"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    student = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='qa_sessions',
        verbose_name='学生'
    )
    subject = models.CharField(max_length=100, verbose_name="对话主题", default="通用")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="创建时间")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="更新时间")

    class Meta:
        db_table = 'qa_sessions'
        verbose_name = '问答会话'
        verbose_name_plural = '问答会话'
        ordering = ['-updated_at']

    def __str__(self):
        return f"{self.student.username} - {self.subject} - {self.created_at.strftime('%Y-%m-%d %H:%M')}"


class QAMessage(models.Model):
    """问答消息模型"""
    ROLE_CHOICES = [
        ('user', '用户'),
        ('ai', 'AI助手'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    session = models.ForeignKey(
        QASession,
        on_delete=models.CASCADE,
        related_name='messages',
        verbose_name='所属会话'
    )
    role = models.CharField(max_length=10, choices=ROLE_CHOICES, verbose_name="角色")
    content = models.TextField(verbose_name="消息内容")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="创建时间")

    class Meta:
        db_table = 'qa_messages'
        verbose_name = '问答消息'
        verbose_name_plural = '问答消息'
        ordering = ['created_at']

    def __str__(self):
        return f"{self.get_role_display()} - {self.content[:50]}"


# 保留旧模型以兼容现有数据，但标记为废弃
class QAQuestion(models.Model):
    """学生提问模型 - 已废弃，保留用于数据迁移"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    student = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='qa_questions',
        verbose_name='学生'
    )
    question_text = models.TextField(verbose_name='问题内容')
    subject = models.CharField(max_length=50, blank=True, verbose_name='学科')
    context = models.TextField(blank=True, verbose_name='问题上下文')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')

    class Meta:
        db_table = 'qa_questions'
        verbose_name = '问题(废弃)'
        verbose_name_plural = '问题(废弃)'
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.student.username}: {self.question_text[:50]}"


class QAAnswer(models.Model):
    """问题回答模型 - 已废弃，保留用于数据迁移"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    question = models.OneToOneField(
        QAQuestion,
        on_delete=models.CASCADE,
        related_name='answer',
        verbose_name='所属问题'
    )
    ai_answer = models.TextField(verbose_name='AI回答')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')

    class Meta:
        db_table = 'qa_answers'
        verbose_name = '回答(废弃)'
        verbose_name_plural = '回答(废弃)'

    def __str__(self):
        return f"回答: {self.question.question_text[:30]}"
