from rest_framework import status, permissions
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from django.contrib.auth import get_user_model
from django.db.models import Q, Count, Max, Subquery, OuterRef
from django.core.paginator import Paginator
from drf_spectacular.utils import extend_schema, OpenApiParameter
from drf_spectacular.types import OpenApiTypes

from .models import ChatMessage, ChatSession
from .serializers import (
    ChatUserSerializer, 
    ChatMessageSerializer, 
    SendMessageSerializer
)

User = get_user_model()


@extend_schema(
    summary="获取可聊天用户列表",
    description="获取当前用户可以聊天的用户列表（教师获取学生列表，学生获取教师列表）",
    responses={200: ChatUserSerializer(many=True)}
)
@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def get_chat_users(request):
    """获取可聊天的用户列表"""
    current_user = request.user
    
    # 根据当前用户角色获取可聊天的用户
    if current_user.role == 'teacher':
        # 教师获取学生列表
        target_role = 'student'
    elif current_user.role == 'student':
        # 学生获取教师列表
        target_role = 'teacher'
    else:
        return Response({
            'code': 400,
            'message': '无效的用户角色'
        }, status=status.HTTP_400_BAD_REQUEST)
    
    # 获取目标角色的用户
    users = User.objects.filter(
        role=target_role,
        is_active=True
    ).order_by('real_name')
    
    # 序列化用户数据
    serializer = ChatUserSerializer(
        users, 
        many=True, 
        context={'request': request}
    )
    
    return Response({
        'code': 200,
        'message': '获取成功',
        'data': serializer.data
    })


@extend_schema(
    summary="获取聊天记录",
    description="获取与指定用户的聊天记录",
    parameters=[
        OpenApiParameter(
            name='user_id',
            type=OpenApiTypes.UUID,
            location=OpenApiParameter.PATH,
            description='用户ID'
        ),
        OpenApiParameter(
            name='page',
            type=OpenApiTypes.INT,
            location=OpenApiParameter.QUERY,
            description='页码'
        ),
        OpenApiParameter(
            name='page_size',
            type=OpenApiTypes.INT,
            location=OpenApiParameter.QUERY,
            description='每页数量'
        ),
    ],
    responses={200: ChatMessageSerializer(many=True)}
)
@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def get_chat_messages(request, user_id):
    """获取与指定用户的聊天记录"""
    current_user = request.user
    
    try:
        other_user = User.objects.get(id=user_id)
    except User.DoesNotExist:
        return Response({
            'code': 404,
            'message': '用户不存在'
        }, status=status.HTTP_404_NOT_FOUND)
    
    # 验证是否可以聊天
    if current_user.role == other_user.role:
        return Response({
            'code': 400,
            'message': '只能与不同角色的用户聊天'
        }, status=status.HTTP_400_BAD_REQUEST)
    
    # 获取聊天记录
    messages = ChatMessage.objects.filter(
        Q(sender=current_user, receiver=other_user) |
        Q(sender=other_user, receiver=current_user)
    ).order_by('-created_at')
    
    # 分页
    page = int(request.GET.get('page', 1))
    page_size = int(request.GET.get('page_size', 50))
    
    paginator = Paginator(messages, page_size)
    page_obj = paginator.get_page(page)
    
    # 序列化消息
    serializer = ChatMessageSerializer(page_obj.object_list, many=True)
    
    return Response({
        'code': 200,
        'message': '获取成功',
        'data': {
            'messages': serializer.data,
            'pagination': {
                'page': page,
                'page_size': page_size,
                'total': paginator.count,
                'total_pages': paginator.num_pages
            }
        }
    })


@extend_schema(
    summary="发送消息",
    description="发送聊天消息",
    request=SendMessageSerializer,
    responses={201: ChatMessageSerializer}
)
@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def send_message(request):
    """发送消息"""
    serializer = SendMessageSerializer(
        data=request.data,
        context={'request': request}
    )
    
    if serializer.is_valid():
        message = serializer.save()
        
        # 返回创建的消息
        response_serializer = ChatMessageSerializer(message)
        return Response({
            'code': 201,
            'message': '发送成功',
            'data': response_serializer.data
        }, status=status.HTTP_201_CREATED)
    
    return Response({
        'code': 400,
        'message': '发送失败',
        'errors': serializer.errors
    }, status=status.HTTP_400_BAD_REQUEST)


@extend_schema(
    summary="标记消息为已读",
    description="标记与指定用户的所有未读消息为已读",
    parameters=[
        OpenApiParameter(
            name='user_id',
            type=OpenApiTypes.UUID,
            location=OpenApiParameter.PATH,
            description='用户ID'
        ),
    ]
)
@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def mark_messages_read(request, user_id):
    """标记消息为已读"""
    current_user = request.user
    
    try:
        other_user = User.objects.get(id=user_id)
    except User.DoesNotExist:
        return Response({
            'code': 404,
            'message': '用户不存在'
        }, status=status.HTTP_404_NOT_FOUND)
    
    # 标记对方发给当前用户的未读消息为已读
    updated_count = ChatMessage.objects.filter(
        sender=other_user,
        receiver=current_user,
        is_read=False
    ).update(is_read=True)
    
    return Response({
        'code': 200,
        'message': f'已标记 {updated_count} 条消息为已读'
    })


@extend_schema(
    summary="获取未读消息数量",
    description="获取当前用户的总未读消息数量"
)
@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def get_unread_count(request):
    """获取未读消息数量"""
    current_user = request.user
    
    # 统计当前用户的未读消息总数
    total_unread = ChatMessage.objects.filter(
        receiver=current_user,
        is_read=False
    ).count()
    
    return Response({
        'code': 200,
        'message': '获取成功',
        'data': {
            'total_unread': total_unread
        }
    })