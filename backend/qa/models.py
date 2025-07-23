import uuid
from django.db import models
from django.conf import settings


class QAQuestion(models.Model):
    """学生提问模型 - 严格按照API规范"""
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
        verbose_name = '问题'
        verbose_name_plural = '问题'
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.student.username}: {self.question_text[:50]}"


class QAAnswer(models.Model):
    """问题回答模型 - 严格按照API规范"""
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
        verbose_name = '回答'
        verbose_name_plural = '回答'

    def __str__(self):
        return f"回答: {self.question.question_text[:30]}"
