from django.contrib import admin
from .models import QAQuestion, QAAnswer


class QAAnswerInline(admin.StackedInline):
    """回答内联编辑"""
    model = QAAnswer
    extra = 0
    readonly_fields = ('ai_answer', 'created_at')


@admin.register(QAQuestion)
class QAQuestionAdmin(admin.ModelAdmin):
    """问题管理"""
    inlines = [QAAnswerInline]
    list_display = ('student', 'question_text', 'subject', 'created_at')
    list_filter = ('subject', 'created_at')
    search_fields = ('student__username', 'question_text', 'subject')
    readonly_fields = ('created_at',)
    ordering = ('-created_at',)

    def get_queryset(self, request):
        return super().get_queryset(request).select_related('student')


@admin.register(QAAnswer)
class QAAnswerAdmin(admin.ModelAdmin):
    """回答管理"""
    list_display = ('question', 'created_at')
    list_filter = ('created_at',)
    search_fields = ('question__question_text', 'ai_answer')
    readonly_fields = ('question', 'ai_answer', 'created_at')
    ordering = ('-created_at',)

    def get_queryset(self, request):
        return super().get_queryset(request).select_related('question__student')
