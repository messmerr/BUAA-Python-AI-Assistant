from django.contrib import admin
from .models import Assignment, Question, Submission, Answer


class QuestionInline(admin.TabularInline):
    """问题内联编辑"""
    model = Question
    extra = 1
    fields = ('question_text', 'reference_answer', 'score', 'order')


@admin.register(Assignment)
class AssignmentAdmin(admin.ModelAdmin):
    """作业管理"""
    inlines = [QuestionInline]
    list_display = ('title', 'created_by', 'deadline', 'total_score', 'submission_count', 'created_at')
    list_filter = ('created_by', 'deadline', 'created_at')
    search_fields = ('title', 'description')
    readonly_fields = ('created_at', 'updated_at', 'submission_count')
    ordering = ('-created_at',)


class AnswerInline(admin.TabularInline):
    """答案内联编辑"""
    model = Answer
    extra = 0
    readonly_fields = ('question', 'answer_text', 'obtained_score', 'ai_feedback')


@admin.register(Submission)
class SubmissionAdmin(admin.ModelAdmin):
    """作业提交管理"""
    inlines = [AnswerInline]
    list_display = ('student', 'assignment', 'status', 'obtained_score', 'submitted_at', 'graded_at')
    list_filter = ('status', 'submitted_at', 'graded_at')
    search_fields = ('student__username', 'assignment__title')
    readonly_fields = ('submitted_at',)
    ordering = ('-submitted_at',)


@admin.register(Question)
class QuestionAdmin(admin.ModelAdmin):
    """问题管理"""
    list_display = ('assignment', 'question_text', 'score', 'order')
    list_filter = ('assignment', 'score')
    search_fields = ('question_text', 'assignment__title')
    ordering = ('assignment', 'order')


@admin.register(Answer)
class AnswerAdmin(admin.ModelAdmin):
    """答案管理"""
    list_display = ('submission', 'question', 'obtained_score')
    list_filter = ('obtained_score', 'submission__submitted_at')
    search_fields = ('submission__student__username', 'question__question_text')
    readonly_fields = ('submission', 'question', 'answer_text')
