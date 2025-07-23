import uuid
from django.db import models
from django.conf import settings


class Assignment(models.Model):
    """作业模型 - 严格按照API规范"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    title = models.CharField(max_length=100, verbose_name='作业标题')
    description = models.TextField(verbose_name='作业描述')
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='created_assignments',
        verbose_name='创建者'
    )
    deadline = models.DateTimeField(verbose_name='截止时间')
    total_score = models.IntegerField(verbose_name='总分')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='更新时间')

    class Meta:
        db_table = 'assignments'
        verbose_name = '作业'
        verbose_name_plural = '作业'
        ordering = ['-created_at']

    def __str__(self):
        return self.title

    @property
    def submission_count(self):
        """提交数量"""
        return self.submissions.count()


class Question(models.Model):
    """作业问题模型 - 严格按照API规范"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    assignment = models.ForeignKey(
        Assignment,
        on_delete=models.CASCADE,
        related_name='questions',
        verbose_name='所属作业'
    )
    question_text = models.TextField(verbose_name='问题内容')
    reference_answer = models.TextField(verbose_name='参考答案')
    score = models.IntegerField(verbose_name='分值')
    order = models.IntegerField(default=0, verbose_name='排序')

    class Meta:
        db_table = 'questions'
        verbose_name = '问题'
        verbose_name_plural = '问题'
        ordering = ['order']

    def __str__(self):
        return f"{self.assignment.title} - 问题{self.order}"


class Submission(models.Model):
    """作业提交模型 - 严格按照API规范"""
    STATUS_CHOICES = (
        ('submitted', '已提交'),
        ('grading', '批改中'),
        ('graded', '已批改'),
    )

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    assignment = models.ForeignKey(
        Assignment,
        on_delete=models.CASCADE,
        related_name='submissions',
        verbose_name='所属作业'
    )
    student = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='submissions',
        verbose_name='学生'
    )
    status = models.CharField(
        max_length=10,
        choices=STATUS_CHOICES,
        default='submitted',
        verbose_name='状态'
    )
    obtained_score = models.IntegerField(default=0, verbose_name='获得分数')
    overall_feedback = models.TextField(blank=True, verbose_name='总体反馈')
    submitted_at = models.DateTimeField(auto_now_add=True, verbose_name='提交时间')
    graded_at = models.DateTimeField(null=True, blank=True, verbose_name='批改时间')

    class Meta:
        db_table = 'submissions'
        verbose_name = '作业提交'
        verbose_name_plural = '作业提交'
        ordering = ['-submitted_at']
        unique_together = ['assignment', 'student']

    def __str__(self):
        return f"{self.student.username} - {self.assignment.title}"


class Answer(models.Model):
    """学生答案模型 - 严格按照API规范"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    submission = models.ForeignKey(
        Submission,
        on_delete=models.CASCADE,
        related_name='answers',
        verbose_name='所属提交'
    )
    question = models.ForeignKey(
        Question,
        on_delete=models.CASCADE,
        related_name='answers',
        verbose_name='所属问题'
    )
    answer_text = models.TextField(verbose_name='学生答案')
    obtained_score = models.IntegerField(null=True, blank=True, verbose_name='获得分数')
    ai_feedback = models.TextField(blank=True, verbose_name='AI反馈')

    class Meta:
        db_table = 'answers'
        verbose_name = '答案'
        verbose_name_plural = '答案'
        unique_together = ['submission', 'question']

    def __str__(self):
        return f"{self.submission.student.username} - {self.question.question_text[:50]}"
