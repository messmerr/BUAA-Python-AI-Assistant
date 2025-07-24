from rest_framework import status, permissions
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from django.http import StreamingHttpResponse
from drf_spectacular.utils import extend_schema, OpenApiResponse, OpenApiParameter
from .models import QASession, QAMessage, QAQuestion
from .serializers import (
    QASessionListSerializer,
    QASessionDetailSerializer,
    ChatMessageCreateSerializer,
    QAQuestionCreateSerializer,
    QAQuestionDetailSerializer,
    QAQuestionListSerializer
)
from ai_services import ask_gemini
import json


class IsStudent(permissions.BasePermission):
    """学生权限"""
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.role == 'student'


class IsTeacher(permissions.BasePermission):
    """教师权限"""
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.role == 'teacher'


# 新的聊天API
@extend_schema(
    request=ChatMessageCreateSerializer,
    responses={
        200: OpenApiResponse(description="聊天成功"),
        400: OpenApiResponse(description="请求参数错误"),
        403: OpenApiResponse(description="权限不足"),
    },
    description="发送聊天消息"
)
@api_view(['POST'])
@permission_classes([IsStudent])
def chat_message(request):
    """发送聊天消息"""
    serializer = ChatMessageCreateSerializer(data=request.data)

    if not serializer.is_valid():
        return Response({
            'code': 400,
            'message': '请求参数错误',
            'errors': serializer.errors
        }, status=status.HTTP_400_BAD_REQUEST)

    try:
        # 创建或获取会话
        subject = serializer.validated_data.get('subject', '通用')
        session = serializer.create_or_get_session(request.user, subject)

        # 保存用户消息
        user_message = serializer.validated_data['message']
        serializer.save_message(session, 'user', user_message)

        # 获取上下文消息
        context_messages = serializer.get_context_messages(session)

        # 构建AI提示词
        context_text = ""
        for msg in context_messages:
            role_text = "用户" if msg.role == 'user' else "AI助手"
            context_text += f"{role_text}: {msg.content}\n"

        prompt = f"""
你是一位专业的AI助教，请根据对话历史回答学生的问题。

对话历史：
{context_text}

用户: {user_message}

请提供详细、准确的回答。如果是编程问题，请提供代码示例。
"""

        # 调用AI生成回答
        ai_response = ask_gemini(prompt, temperature=0.7)

        # 保存AI回答
        serializer.save_message(session, 'ai', ai_response)

        # 更新会话时间
        session.save()

        return Response({
            'code': 200,
            'message': '聊天成功',
            'data': {
                'session_id': str(session.id),
                'ai_response': ai_response,
                'created_at': session.updated_at
            }
        }, status=status.HTTP_200_OK)

    except Exception as e:
        return Response({
            'code': 500,
            'message': f'聊天失败: {str(e)}'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@extend_schema(
    parameters=[
        OpenApiParameter('page', int, description='页码'),
        OpenApiParameter('page_size', int, description='每页数量'),
        OpenApiParameter('subject', str, description='学科筛选'),
    ],
    responses={
        200: OpenApiResponse(description="获取成功"),
    },
    description="获取会话列表"
)
@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def list_sessions(request):
    """获取会话列表"""
    # 获取查询参数
    page = int(request.GET.get('page', 1))
    page_size = int(request.GET.get('page_size', 10))
    subject_filter = request.GET.get('subject', None)

    # 构建查询
    queryset = QASession.objects.all()

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
    sessions = queryset[start:end]

    # 序列化
    serializer = QASessionListSerializer(sessions, many=True)

    return Response({
        'code': 200,
        'message': '获取成功',
        'data': {
            'sessions': serializer.data,
            'pagination': {
                'page': page,
                'page_size': page_size,
                'total': total,
                'total_pages': (total + page_size - 1) // page_size
            }
        }
    }, status=status.HTTP_200_OK)


@extend_schema(
    responses={
        200: QASessionDetailSerializer,
        404: OpenApiResponse(description="会话不存在"),
        403: OpenApiResponse(description="权限不足"),
    },
    description="获取会话详情"
)
@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def get_session_detail(request, session_id):
    """获取会话详情"""
    session = get_object_or_404(QASession, id=session_id)

    # 权限检查：学生只能查看自己的会话，教师可以查看所有会话
    if request.user.role == 'student' and session.student != request.user:
        return Response({
            'code': 403,
            'message': '权限不足，只能查看自己的会话'
        }, status=status.HTTP_403_FORBIDDEN)

    serializer = QASessionDetailSerializer(session)
    return Response({
        'code': 200,
        'message': '获取成功',
        'data': serializer.data
    }, status=status.HTTP_200_OK)


# 保留旧的API以兼容现有前端
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
