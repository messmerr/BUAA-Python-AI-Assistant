from django.contrib import admin
from .models import QASession, QAMessage, QAQuestion, QAAnswer


class QAMessageInline(admin.TabularInline):
    """消息内联编辑"""
    model = QAMessage
    extra = 0
    readonly_fields = ('role', 'content', 'created_at')
    ordering = ('created_at',)


@admin.register(QASession)
class QASessionAdmin(admin.ModelAdmin):
    """会话管理"""
    inlines = [QAMessageInline]
    list_display = ('student', 'subject', 'message_count', 'created_at', 'updated_at')
    list_filter = ('subject', 'created_at', 'updated_at')
    search_fields = ('student__username', 'subject')
    readonly_fields = ('created_at', 'updated_at')
    ordering = ('-updated_at',)

    def get_queryset(self, request):
        return super().get_queryset(request).select_related('student')

    def message_count(self, obj):
        return obj.messages.count()
    message_count.short_description = '消息数量'


@admin.register(QAMessage)
class QAMessageAdmin(admin.ModelAdmin):
    """消息管理"""
    list_display = ('session', 'role', 'content_preview', 'created_at')
    list_filter = ('role', 'created_at')
    search_fields = ('session__student__username', 'content')
    readonly_fields = ('created_at',)
    ordering = ('-created_at',)

    def get_queryset(self, request):
        return super().get_queryset(request).select_related('session__student')

    def content_preview(self, obj):
        return obj.content[:100] + ('...' if len(obj.content) > 100 else '')
    content_preview.short_description = '内容预览'


# 保留旧模型的管理界面
class QAAnswerInline(admin.StackedInline):
    """回答内联编辑"""
    model = QAAnswer
    extra = 0
    readonly_fields = ('ai_answer', 'created_at')


@admin.register(QAQuestion)
class QAQuestionAdmin(admin.ModelAdmin):
    """问题管理(废弃)"""
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
