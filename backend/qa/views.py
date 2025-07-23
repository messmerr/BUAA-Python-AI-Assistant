from rest_framework import status, permissions
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from drf_spectacular.utils import extend_schema, OpenApiResponse, OpenApiParameter
from .models import QAQuestion
from .serializers import (
    QAQuestionCreateSerializer,
    QAQuestionDetailSerializer,
    QAQuestionListSerializer
)


class IsStudent(permissions.BasePermission):
    """学生权限"""
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.role == 'student'


class IsTeacher(permissions.BasePermission):
    """教师权限"""
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.role == 'teacher'


@extend_schema(
    request=QAQuestionCreateSerializer,
    responses={
        201: OpenApiResponse(description="问题提交成功"),
        400: OpenApiResponse(description="请求参数错误"),
        403: OpenApiResponse(description="权限不足"),
    },
    description="学生提交问题"
)
@api_view(['POST'])
@permission_classes([IsStudent])
def submit_question(request):
    """学生提交问题 - 仅学生可用"""
    serializer = QAQuestionCreateSerializer(
        data=request.data,
        context={'student': request.user}
    )

    if serializer.is_valid():
        question = serializer.save()
        return Response({
            'code': 201,
            'message': '问题提交成功',
            'data': {
                'question_id': str(question.id),
                'ai_answer': question.ai_answer,
                'created_at': question.created_at
            }
        }, status=status.HTTP_201_CREATED)

    return Response({
        'code': 400,
        'message': '问题提交失败',
        'errors': serializer.errors
    }, status=status.HTTP_400_BAD_REQUEST)


@extend_schema(
    responses={
        200: QAQuestionDetailSerializer,
        404: OpenApiResponse(description="问题不存在"),
        403: OpenApiResponse(description="权限不足"),
    },
    description="获取问题详情和AI回答"
)
@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def get_question_detail(request, question_id):
    """获取问题详情和AI回答"""
    question = get_object_or_404(QAQuestion, id=question_id)

    # 权限检查：学生只能查看自己的问题，教师可以查看所有问题
    if request.user.role == 'student' and question.student != request.user:
        return Response({
            'code': 403,
            'message': '权限不足，只能查看自己的问题'
        }, status=status.HTTP_403_FORBIDDEN)

    serializer = QAQuestionDetailSerializer(question)
    return Response({
        'code': 200,
        'message': '获取成功',
        'data': serializer.data
    }, status=status.HTTP_200_OK)


@extend_schema(
    parameters=[
        OpenApiParameter('page', int, description='页码'),
        OpenApiParameter('page_size', int, description='每页数量'),
        OpenApiParameter('subject', str, description='学科筛选'),
    ],
    responses={
        200: OpenApiResponse(description="获取成功"),
    },
    description="获取问题列表"
)
@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def list_questions(request):
    """获取问题列表"""
    # 获取查询参数
    page = int(request.GET.get('page', 1))
    page_size = int(request.GET.get('page_size', 10))
    subject_filter = request.GET.get('subject', None)

    # 构建查询
    queryset = QAQuestion.objects.all()

    # 根据用户角色过滤
    if request.user.role == 'student':
        queryset = queryset.filter(student=request.user)

    # 学科过滤
    if subject_filter:
        queryset = queryset.filter(subject__icontains=subject_filter)

    # 分页
    total = queryset.count()
    start = (page - 1) * page_size
    end = start + page_size
    questions = queryset[start:end]

    # 序列化
    serializer = QAQuestionListSerializer(questions, many=True)

    return Response({
        'code': 200,
        'message': '获取成功',
        'data': {
            'questions': serializer.data,
            'pagination': {
                'page': page,
                'page_size': page_size,
                'total': total,
                'total_pages': (total + page_size - 1) // page_size
            }
        }
    }, status=status.HTTP_200_OK)
