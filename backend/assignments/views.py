from rest_framework import status, generics, permissions
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from django.db.models import Q
from drf_spectacular.utils import extend_schema, OpenApiResponse, OpenApiParameter
from .models import Assignment, Submission
from .serializers import (
    AssignmentCreateSerializer,
    AssignmentListSerializer,
    AssignmentDetailSerializer,
    AssignmentSubmissionSerializer,
    SubmissionDetailSerializer
)


class IsTeacher(permissions.BasePermission):
    """教师权限"""
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.role == 'teacher'


class IsStudent(permissions.BasePermission):
    """学生权限"""
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.role == 'student'


@extend_schema(
    request=AssignmentCreateSerializer,
    responses={
        201: OpenApiResponse(description="作业创建成功"),
        400: OpenApiResponse(description="请求参数错误"),
        403: OpenApiResponse(description="权限不足"),
    },
    description="教师创建作业"
)
@api_view(['POST'])
@permission_classes([IsTeacher])
def create_assignment(request):
    """创建作业 - 仅教师"""
    serializer = AssignmentCreateSerializer(data=request.data)
    if serializer.is_valid():
        assignment = serializer.save(created_by=request.user)
        return Response({
            'code': 201,
            'message': '作业创建成功',
            'data': {
                'assignment_id': str(assignment.id),
                'title': assignment.title,
                'created_at': assignment.created_at
            }
        }, status=status.HTTP_201_CREATED)

    return Response({
        'code': 400,
        'message': '作业创建失败',
        'errors': serializer.errors
    }, status=status.HTTP_400_BAD_REQUEST)


@extend_schema(
    parameters=[
        OpenApiParameter('page', int, description='页码'),
        OpenApiParameter('page_size', int, description='每页数量'),
        OpenApiParameter('status', str, description='作业状态'),
    ],
    responses={
        200: OpenApiResponse(description="获取成功"),
    },
    description="获取作业列表"
)
@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def list_assignments(request):
    """获取作业列表"""
    # 获取查询参数
    page = int(request.GET.get('page', 1))
    page_size = int(request.GET.get('page_size', 10))
    status_filter = request.GET.get('status', None)

    # 构建查询
    queryset = Assignment.objects.all()

    # 根据用户角色过滤
    if request.user.role == 'teacher':
        queryset = queryset.filter(created_by=request.user)

    # 状态过滤（简化实现）
    if status_filter:
        from django.utils import timezone
        now = timezone.now()
        if status_filter == 'active':
            queryset = queryset.filter(deadline__gt=now)
        elif status_filter == 'expired':
            queryset = queryset.filter(deadline__lte=now)

    # 分页
    total = queryset.count()
    start = (page - 1) * page_size
    end = start + page_size
    assignments = queryset[start:end]

    # 序列化
    serializer = AssignmentListSerializer(assignments, many=True)

    return Response({
        'code': 200,
        'message': '获取成功',
        'data': {
            'assignments': serializer.data,
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
        200: AssignmentDetailSerializer,
        404: OpenApiResponse(description="作业不存在"),
    },
    description="获取作业详情"
)
@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def get_assignment_detail(request, assignment_id):
    """获取作业详情"""
    assignment = get_object_or_404(Assignment, id=assignment_id)

    # 权限检查：教师只能看自己创建的作业
    if request.user.role == 'teacher' and assignment.created_by != request.user:
        return Response({
            'code': 403,
            'message': '权限不足'
        }, status=status.HTTP_403_FORBIDDEN)

    serializer = AssignmentDetailSerializer(assignment)
    return Response({
        'code': 200,
        'message': '获取成功',
        'data': serializer.data
    }, status=status.HTTP_200_OK)


@extend_schema(
    request=AssignmentSubmissionSerializer,
    responses={
        201: OpenApiResponse(description="作业提交成功"),
        400: OpenApiResponse(description="提交失败"),
        403: OpenApiResponse(description="权限不足"),
        404: OpenApiResponse(description="作业不存在"),
    },
    description="学生提交作业"
)
@api_view(['POST'])
@permission_classes([IsStudent])
def submit_assignment(request, assignment_id):
    """提交作业 - 仅学生"""
    assignment = get_object_or_404(Assignment, id=assignment_id)

    # 检查截止时间
    from django.utils import timezone
    if timezone.now() > assignment.deadline:
        return Response({
            'code': 400,
            'message': '作业已过截止时间'
        }, status=status.HTTP_400_BAD_REQUEST)

    serializer = AssignmentSubmissionSerializer(
        data=request.data,
        context={'assignment': assignment, 'student': request.user}
    )

    if serializer.is_valid():
        submission = serializer.save()
        return Response({
            'code': 201,
            'message': '作业提交成功',
            'data': {
                'submission_id': str(submission.id),
                'submitted_at': submission.submitted_at,
                'status': submission.status
            }
        }, status=status.HTTP_201_CREATED)

    return Response({
        'code': 400,
        'message': '作业提交失败',
        'errors': serializer.errors
    }, status=status.HTTP_400_BAD_REQUEST)


@extend_schema(
    responses={
        200: SubmissionDetailSerializer,
        403: OpenApiResponse(description="权限不足"),
        404: OpenApiResponse(description="提交记录不存在"),
    },
    description="获取作业批改结果"
)
@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def get_submission_result(request, assignment_id, submission_id):
    """获取作业批改结果"""
    assignment = get_object_or_404(Assignment, id=assignment_id)
    submission = get_object_or_404(
        Submission,
        id=submission_id,
        assignment=assignment
    )

    # 权限检查
    if request.user.role == 'student':
        # 学生只能查看自己的提交
        if submission.student != request.user:
            return Response({
                'code': 403,
                'message': '权限不足'
            }, status=status.HTTP_403_FORBIDDEN)
    elif request.user.role == 'teacher':
        # 教师只能查看自己创建的作业的提交
        if assignment.created_by != request.user:
            return Response({
                'code': 403,
                'message': '权限不足'
            }, status=status.HTTP_403_FORBIDDEN)

    serializer = SubmissionDetailSerializer(submission)
    return Response({
        'code': 200,
        'message': '获取成功',
        'data': serializer.data
    }, status=status.HTTP_200_OK)
