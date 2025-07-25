from django.contrib import admin
from .models import LearningReport


@admin.register(LearningReport)
class LearningReportAdmin(admin.ModelAdmin):
    """学习报告管理"""
    list_display = (
        'student', 'generated_by', 'period', 'status',
        'total_assignments', 'completed_assignments', 'average_score',
        'total_questions', 'created_at'
    )
    list_filter = ('period', 'status', 'created_at', 'subjects')
    search_fields = ('student__username', 'student__real_name', 'generated_by__username')
    readonly_fields = ('created_at', 'updated_at')
    ordering = ('-created_at',)

    fieldsets = (
        ('基本信息', {
            'fields': ('student', 'generated_by', 'period', 'subjects', 'status')
        }),
        ('统计数据', {
            'fields': ('total_assignments', 'completed_assignments', 'average_score', 'total_questions')
        }),
        ('报告内容', {
            'fields': ('report_content',),
            'classes': ('collapse',)
        }),
        ('时间信息', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        })
    )

    def get_queryset(self, request):
        return super().get_queryset(request).select_related('student', 'generated_by')
