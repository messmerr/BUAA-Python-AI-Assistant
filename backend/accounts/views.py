from rest_framework import status, generics, permissions
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.views import TokenRefreshView
from django.contrib.auth import login
from drf_spectacular.utils import extend_schema, OpenApiResponse
from .models import User
from .serializers import (
    UserRegistrationSerializer,
    UserLoginSerializer,
    UserSerializer,
    UserUpdateSerializer
)


def get_tokens_for_user(user):
    """为用户生成JWT tokens"""
    refresh = RefreshToken.for_user(user)
    return {
        'refresh': str(refresh),
        'access': str(refresh.access_token),
    }


@extend_schema(
    request=UserRegistrationSerializer,
    responses={
        201: OpenApiResponse(description="注册成功"),
        400: OpenApiResponse(description="请求参数错误"),
    },
    description="用户注册接口"
)
@api_view(['POST'])
@permission_classes([permissions.AllowAny])
def register_view(request):
    """用户注册"""
    serializer = UserRegistrationSerializer(data=request.data)
    if serializer.is_valid():
        user = serializer.save()
        return Response({
            'code': 201,
            'message': '注册成功',
            'data': {
                'user_id': str(user.id),
                'username': user.username,
                'role': user.role
            }
        }, status=status.HTTP_201_CREATED)

    return Response({
        'code': 400,
        'message': '注册失败',
        'errors': serializer.errors
    }, status=status.HTTP_400_BAD_REQUEST)


@extend_schema(
    request=UserLoginSerializer,
    responses={
        200: OpenApiResponse(description="登录成功"),
        400: OpenApiResponse(description="登录失败"),
    },
    description="用户登录接口"
)
@api_view(['POST'])
@permission_classes([permissions.AllowAny])
def login_view(request):
    """用户登录"""
    serializer = UserLoginSerializer(data=request.data)
    if serializer.is_valid():
        user = serializer.validated_data['user']
        login(request, user)
        tokens = get_tokens_for_user(user)

        return Response({
            'code': 200,
            'message': '登录成功',
            'data': {
                'access_token': tokens['access'],
                'refresh_token': tokens['refresh'],
                'user': {
                    'id': str(user.id),
                    'username': user.username,
                    'role': user.role,
                    'real_name': user.real_name
                }
            }
        }, status=status.HTTP_200_OK)

    return Response({
        'code': 400,
        'message': '登录失败',
        'errors': serializer.errors
    }, status=status.HTTP_400_BAD_REQUEST)


@extend_schema(
    responses={
        200: UserSerializer,
    },
    description="获取当前用户信息"
)
@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def profile_view(request):
    """获取用户信息"""
    serializer = UserSerializer(request.user)
    return Response({
        'code': 200,
        'message': '获取成功',
        'data': serializer.data
    }, status=status.HTTP_200_OK)


@extend_schema(
    request=UserUpdateSerializer,
    responses={
        200: UserSerializer,
        400: OpenApiResponse(description="更新失败"),
    },
    description="更新用户信息"
)
@api_view(['PUT'])
@permission_classes([permissions.IsAuthenticated])
def update_profile_view(request):
    """更新用户信息"""
    serializer = UserUpdateSerializer(request.user, data=request.data, partial=True)
    if serializer.is_valid():
        user = serializer.save()
        response_serializer = UserSerializer(user)
        return Response({
            'code': 200,
            'message': '更新成功',
            'data': response_serializer.data
        }, status=status.HTTP_200_OK)

    return Response({
        'code': 400,
        'message': '更新失败',
        'errors': serializer.errors
    }, status=status.HTTP_400_BAD_REQUEST)


class CustomTokenRefreshView(TokenRefreshView):
    """自定义Token刷新视图"""

    @extend_schema(
        responses={
            200: OpenApiResponse(description="Token刷新成功"),
            401: OpenApiResponse(description="Token无效"),
        },
        description="刷新访问令牌"
    )
    def post(self, request, *args, **kwargs):
        response = super().post(request, *args, **kwargs)
        if response.status_code == 200:
            return Response({
                'code': 200,
                'message': 'Token刷新成功',
                'data': {
                    'access_token': response.data['access']
                }
            }, status=status.HTTP_200_OK)
        return response
