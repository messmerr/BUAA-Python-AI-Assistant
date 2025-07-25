from rest_framework import serializers
from .models import LearningReport
try:
    from accounts.models import User
except ImportError:
    from django.contrib.auth import get_user_model
    User = get_user_model()


class LearningReportCreateSerializer(serializers.Serializer):
    """学习报告创建序列化器"""
    student_id = serializers.UUIDField(required=False, help_text="学生ID，教师生成报告时必填")
    period = serializers.ChoiceField(
        choices=LearningReport.PERIOD_CHOICES,
        default='month',
        help_text="时间段"
    )
    subjects = serializers.ListField(
        child=serializers.CharField(max_length=100),
        required=False,
        default=list,
        help_text="科目列表，为空则包含所有科目"
    )
    
    def validate(self, attrs):
        request = self.context.get('request')
        user = request.user
        
        # 如果是教师，必须提供student_id
        if user.role == 'teacher' and not attrs.get('student_id'):
            raise serializers.ValidationError("教师生成报告时必须指定学生ID")
        
        # 如果是学生，不能指定student_id（只能为自己生成）
        if user.role == 'student' and attrs.get('student_id'):
            raise serializers.ValidationError("学生只能为自己生成报告")
        
        return attrs
    
    def validate_student_id(self, value):
        """验证学生ID"""
        if value:
            try:
                student = User.objects.get(id=value, role='student')
                return value
            except User.DoesNotExist:
                raise serializers.ValidationError("指定的学生不存在")
        return value


class LearningReportListSerializer(serializers.ModelSerializer):
    """学习报告列表序列化器"""
    student_name = serializers.CharField(source='student.real_name', read_only=True)
    generated_by_name = serializers.CharField(source='generated_by.real_name', read_only=True)
    period_display = serializers.CharField(source='get_period_display', read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    
    class Meta:
        model = LearningReport
        fields = [
            'id', 'student_name', 'generated_by_name', 'period', 'period_display',
            'subjects', 'status', 'status_display', 'total_assignments',
            'completed_assignments', 'average_score', 'total_questions',
            'created_at', 'updated_at'
        ]


class LearningReportDetailSerializer(serializers.ModelSerializer):
    """学习报告详情序列化器"""
    student_name = serializers.CharField(source='student.real_name', read_only=True)
    student_id_number = serializers.CharField(source='student.student_id', read_only=True)
    generated_by_name = serializers.CharField(source='generated_by.real_name', read_only=True)
    period_display = serializers.CharField(source='get_period_display', read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    
    class Meta:
        model = LearningReport
        fields = [
            'id', 'student_name', 'student_id_number', 'generated_by_name',
            'period', 'period_display', 'subjects', 'status', 'status_display',
            'total_assignments', 'completed_assignments', 'average_score',
            'total_questions', 'report_content', 'created_at', 'updated_at'
        ]
