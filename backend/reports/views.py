from rest_framework import status, permissions
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from django.db.models import Q, Avg, Count
from django.utils import timezone
from datetime import datetime, timedelta
from drf_spectacular.utils import extend_schema, OpenApiResponse, OpenApiParameter

from .models import LearningReport
from .serializers import (
    LearningReportCreateSerializer,
    LearningReportListSerializer,
    LearningReportDetailSerializer
)
try:
    from accounts.models import User
except ImportError:
    from django.contrib.auth import get_user_model
    User = get_user_model()

try:
    from assignments.models import Assignment, Submission, Answer
except ImportError:
    Assignment = None
    Submission = None
    Answer = None

try:
    from qa.models import QASession, QAMessage, QAQuestion
except ImportError:
    QASession = None
    QAMessage = None
    QAQuestion = None

try:
    from ai_services import ask_gemini
except ImportError:
    def ask_gemini(prompt, temperature=0.7):
        return "AI服务暂时不可用，这是一个模拟的学习报告内容。"
import json


class IsStudent(permissions.BasePermission):
    """学生权限"""
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.role == 'student'


class IsTeacher(permissions.BasePermission):
    """教师权限"""
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.role == 'teacher'


def get_time_range(period):
    """根据时间段获取时间范围"""
    now = timezone.now()

    if period == 'week':
        start_time = now - timedelta(days=7)
    elif period == 'month':
        start_time = now - timedelta(days=30)
    elif period == 'semester':
        start_time = now - timedelta(days=120)  # 约4个月
    else:  # 'all'
        start_time = datetime(2020, 1, 1, tzinfo=timezone.get_current_timezone())

    return start_time, now


def collect_student_data(student, period, subjects):
    """收集学生的学习数据"""
    start_time, end_time = get_time_range(period)

    # 构建查询条件
    assignment_filter = Q(created_at__gte=start_time, created_at__lte=end_time)
    qa_filter = Q(created_at__gte=start_time, created_at__lte=end_time)

    if subjects:
        assignment_filter &= Q(subject__in=subjects)
        qa_filter &= Q(subject__in=subjects)

    # 收集作业数据
    assignments = []
    submissions = []
    if Assignment is not None and Submission is not None:
        try:
            assignments = Assignment.objects.filter(assignment_filter)
            submissions = Submission.objects.filter(
                student=student,
                assignment__in=assignments
            ).select_related('assignment').prefetch_related('answers__question')
        except Exception as e:
            print(f"[DEBUG] 获取作业数据失败: {e}")

    # 收集问答数据
    qa_sessions = []
    if QASession is not None:
        try:
            qa_sessions = QASession.objects.filter(
                student=student,
                updated_at__gte=start_time,
                updated_at__lte=end_time
            ).prefetch_related('messages')
            if subjects:
                qa_sessions = qa_sessions.filter(subject__in=subjects)
        except Exception as e:
            print(f"[DEBUG] 获取QA会话数据失败: {e}")

    # 也收集旧的QA数据以兼容
    old_qa_questions = []
    if QAQuestion is not None:
        try:
            old_qa_questions = QAQuestion.objects.filter(
                student=student,
                created_at__gte=start_time,
                created_at__lte=end_time
            ).select_related('answer')
            if subjects:
                old_qa_questions = old_qa_questions.filter(subject__in=subjects)
        except Exception as e:
            print(f"[DEBUG] 获取旧QA数据失败: {e}")

    return {
        'assignments': assignments,
        'submissions': submissions,
        'qa_sessions': qa_sessions,
        'old_qa_questions': old_qa_questions,
        'time_range': (start_time, end_time)
    }


def calculate_statistics(data):
    """计算统计数据"""
    assignments = data['assignments']
    submissions = data['submissions']
    qa_sessions = data['qa_sessions']
    old_qa_questions = data['old_qa_questions']

    # 作业统计
    total_assignments = len(assignments) if hasattr(assignments, '__len__') else (assignments.count() if assignments else 0)
    completed_assignments = len(submissions) if hasattr(submissions, '__len__') else (submissions.count() if submissions else 0)

    # 计算平均得分
    total_score = 0
    total_possible = 0

    if submissions:
        try:
            for submission in submissions:
                if hasattr(submission, 'total_score') and hasattr(submission, 'assignment'):
                    total_score += submission.total_score or 0
                    total_possible += getattr(submission.assignment, 'total_score', 0)
        except Exception as e:
            print(f"[DEBUG] 计算得分失败: {e}")

    average_score = (total_score / total_possible * 100) if total_possible > 0 else 0

    # 问答统计
    qa_count = len(qa_sessions) if hasattr(qa_sessions, '__len__') else (qa_sessions.count() if qa_sessions else 0)
    old_qa_count = len(old_qa_questions) if hasattr(old_qa_questions, '__len__') else (old_qa_questions.count() if old_qa_questions else 0)
    total_questions = qa_count + old_qa_count

    return {
        'total_assignments': total_assignments,
        'completed_assignments': completed_assignments,
        'average_score': round(average_score, 2),
        'total_questions': total_questions
    }


def generate_report_content(student, data, statistics, period, subjects):
    """使用AI生成报告内容"""
    start_time, end_time = data['time_range']

    # 构建详细的数据上下文
    context_data = {
        'student_info': {
            'name': student.real_name,
            'student_id': student.student_id,
            'username': student.username
        },
        'time_period': {
            'period': period,
            'start_date': start_time.strftime('%Y-%m-%d'),
            'end_date': end_time.strftime('%Y-%m-%d')
        },
        'subjects': subjects if subjects else ['所有科目'],
        'statistics': statistics,
        'assignments_detail': [],
        'qa_detail': []
    }

    # 收集作业详情
    if data['submissions']:
        try:
            for submission in data['submissions']:
                if hasattr(submission, 'assignment') and hasattr(submission, 'total_score'):
                    assignment_detail = {
                        'title': getattr(submission.assignment, 'title', '未知作业'),
                        'subject': getattr(submission.assignment, 'subject', '未知科目'),
                        'score': submission.total_score or 0,
                        'max_score': getattr(submission.assignment, 'total_score', 0),
                        'score_percentage': round((submission.total_score / submission.assignment.total_score * 100), 2) if getattr(submission.assignment, 'total_score', 0) > 0 else 0,
                        'submitted_at': submission.submitted_at.strftime('%Y-%m-%d %H:%M') if hasattr(submission, 'submitted_at') else '未知时间',
                        'questions_performance': []
                    }

                    # 收集每道题的表现
                    try:
                        if hasattr(submission, 'answers'):
                            for answer in submission.answers.all():
                                question_perf = {
                                    'question': getattr(answer.question, 'question_text', '未知问题')[:100] + ('...' if len(getattr(answer.question, 'question_text', '')) > 100 else ''),
                                    'student_answer': getattr(answer, 'answer_text', '无答案')[:200] + ('...' if len(getattr(answer, 'answer_text', '')) > 200 else ''),
                                    'score': getattr(answer, 'score', 0),
                                    'max_score': getattr(answer.question, 'score', 0),
                                    'feedback': getattr(answer, 'feedback', '无反馈')[:200] + ('...' if len(getattr(answer, 'feedback', '')) > 200 else '')
                                }
                                assignment_detail['questions_performance'].append(question_perf)
                    except Exception as e:
                        print(f"[DEBUG] 收集答案详情失败: {e}")

                    context_data['assignments_detail'].append(assignment_detail)
        except Exception as e:
            print(f"[DEBUG] 收集作业详情失败: {e}")

    # 收集问答详情
    if data['qa_sessions']:
        try:
            for session in data['qa_sessions']:
                if hasattr(session, 'messages'):
                    try:
                        messages = session.messages.all()
                        if messages:
                            qa_detail = {
                                'subject': getattr(session, 'subject', '未知科目'),
                                'created_at': session.created_at.strftime('%Y-%m-%d %H:%M') if hasattr(session, 'created_at') else '未知时间',
                                'message_count': len(messages),
                                'conversation_summary': []
                            }

                            for message in messages[:10]:  # 只取前10条消息
                                qa_detail['conversation_summary'].append({
                                    'role': getattr(message, 'role', 'unknown'),
                                    'content': getattr(message, 'content', '无内容')[:150] + ('...' if len(getattr(message, 'content', '')) > 150 else '')
                                })

                            context_data['qa_detail'].append(qa_detail)
                    except Exception as e:
                        print(f"[DEBUG] 处理会话消息失败: {e}")
        except Exception as e:
            print(f"[DEBUG] 收集QA会话详情失败: {e}")

    # 收集旧问答数据
    if data['old_qa_questions']:
        try:
            for question in data['old_qa_questions']:
                if hasattr(question, 'answer') and question.answer:
                    qa_detail = {
                        'subject': getattr(question, 'subject', '未知科目'),
                        'created_at': question.created_at.strftime('%Y-%m-%d %H:%M') if hasattr(question, 'created_at') else '未知时间',
                        'question': getattr(question, 'question_text', '无问题')[:200] + ('...' if len(getattr(question, 'question_text', '')) > 200 else ''),
                        'ai_answer': getattr(question.answer, 'ai_answer', '无回答')[:200] + ('...' if len(getattr(question.answer, 'ai_answer', '')) > 200 else '')
                    }
                    context_data['qa_detail'].append(qa_detail)
        except Exception as e:
            print(f"[DEBUG] 收集旧QA数据详情失败: {e}")

    # 构建AI提示词
    prompt = f"""
你是一位专业的教育分析师，请根据以下学生的学习数据生成一份详细的学习报告。

学生信息：
- 姓名：{context_data['student_info']['name']}
- 学号：{context_data['student_info']['student_id']}
- 分析时间段：{context_data['time_period']['start_date']} 至 {context_data['time_period']['end_date']} ({period})
- 涉及科目：{', '.join(context_data['subjects'])}

学习统计：
- 总作业数：{statistics['total_assignments']}
- 已完成作业数：{statistics['completed_assignments']}
- 平均得分：{statistics['average_score']}%
- 提问次数：{statistics['total_questions']}

作业详情：
{json.dumps(context_data['assignments_detail'], ensure_ascii=False, indent=2)}

问答记录：
{json.dumps(context_data['qa_detail'], ensure_ascii=False, indent=2)}

请生成一份结构化的学习报告，包含以下部分：

1. **学习概况总结**
   - 整体学习表现评价
   - 主要学习成果

2. **作业完成情况分析**
   - 作业完成率分析
   - 得分情况分析
   - 各科目表现对比

3. **知识掌握情况**
   - 强项知识点
   - 薄弱环节识别
   - 具体问题分析

4. **学习行为分析**
   - 提问频率和质量
   - 学习主动性评价
   - 问题解决能力

5. **改进建议**
   - 针对性学习建议
   - 具体改进措施
   - 推荐学习资源

请用专业、客观、建设性的语言撰写报告，字数控制在1000-1500字。
"""

    try:
        print(f"[DEBUG] 开始生成学习报告，学生：{student.real_name}")
        ai_response = ask_gemini(prompt, temperature=0.7)
        print(f"[DEBUG] AI报告生成成功，长度：{len(ai_response)}")
        return ai_response
    except Exception as e:
        print(f"[DEBUG] AI报告生成失败：{str(e)}")
        return f"报告生成失败，错误信息：{str(e)}"


def generate_simple_report(student, period, subjects, statistics):
    """生成简化版报告（当数据收集失败时使用）"""
    return f"""
# {student.real_name} 学习报告

## 基本信息
- 学生姓名：{student.real_name}
- 学号：{student.student_id}
- 报告时间段：{period}
- 涉及科目：{', '.join(subjects) if subjects else '所有科目'}

## 学习统计
- 总作业数：{statistics['total_assignments']}
- 已完成作业数：{statistics['completed_assignments']}
- 平均得分：{statistics['average_score']}%
- 提问次数：{statistics['total_questions']}

## 学习评价
根据您的学习数据，我们为您生成了这份简化的学习报告。

### 作业完成情况
您在此时间段内共有 {statistics['total_assignments']} 份作业，完成了 {statistics['completed_assignments']} 份，
完成率为 {round(statistics['completed_assignments']/statistics['total_assignments']*100, 2) if statistics['total_assignments'] > 0 else 0}%。

### 学习表现
您的平均得分为 {statistics['average_score']}%，{'表现优秀' if statistics['average_score'] >= 80 else '还有提升空间' if statistics['average_score'] >= 60 else '需要加强学习'}。

### 学习建议
1. 继续保持良好的学习习惯
2. 多与AI助教互动，积极提问
3. 及时完成作业，巩固知识点
4. 定期复习，查漏补缺

---
*本报告由AI助教系统自动生成*
"""


@extend_schema(
    request=LearningReportCreateSerializer,
    responses={
        201: OpenApiResponse(description="报告生成成功"),
        400: OpenApiResponse(description="请求参数错误"),
        403: OpenApiResponse(description="权限不足"),
    },
    description="生成学习报告"
)
@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def generate_report(request):
    """生成学习报告"""
    serializer = LearningReportCreateSerializer(
        data=request.data,
        context={'request': request}
    )

    if not serializer.is_valid():
        return Response({
            'code': 400,
            'message': '请求参数错误',
            'errors': serializer.errors
        }, status=status.HTTP_400_BAD_REQUEST)

    try:
        # 确定目标学生
        if request.user.role == 'teacher':
            student_id = serializer.validated_data['student_id']
            student = User.objects.get(id=student_id, role='student')
        else:
            student = request.user

        period = serializer.validated_data['period']
        subjects = serializer.validated_data.get('subjects', [])

        # 创建报告记录
        report = LearningReport.objects.create(
            student=student,
            generated_by=request.user,
            period=period,
            subjects=subjects,
            status='generating'
        )

        # 收集学习数据
        try:
            data = collect_student_data(student, period, subjects)
            print(f"[DEBUG] 数据收集成功")
        except Exception as e:
            print(f"[DEBUG] 数据收集失败: {e}")
            data = {
                'assignments': [],
                'submissions': [],
                'qa_sessions': [],
                'old_qa_questions': [],
                'time_range': (None, None)
            }

        # 计算统计数据
        try:
            statistics = calculate_statistics(data)
            print(f"[DEBUG] 统计计算成功: {statistics}")
        except Exception as e:
            print(f"[DEBUG] 统计计算失败: {e}")
            statistics = {
                'total_assignments': 0,
                'completed_assignments': 0,
                'average_score': 0.0,
                'total_questions': 0
            }

        # 更新统计信息
        report.total_assignments = statistics['total_assignments']
        report.completed_assignments = statistics['completed_assignments']
        report.average_score = statistics['average_score']
        report.total_questions = statistics['total_questions']

        # 生成报告内容
        try:
            report_content = generate_report_content(student, data, statistics, period, subjects)
            print(f"[DEBUG] 报告内容生成成功，长度: {len(report_content)}")
        except Exception as e:
            print(f"[DEBUG] 详细报告生成失败: {e}，使用简化版本")
            report_content = generate_simple_report(student, period, subjects, statistics)

        # 更新报告
        report.report_content = report_content
        report.status = 'completed'
        report.save()

        return Response({
            'code': 201,
            'message': '报告生成成功',
            'data': {
                'report_id': str(report.id),
                'status': report.status,
                'created_at': report.created_at
            }
        }, status=status.HTTP_201_CREATED)

    except User.DoesNotExist:
        return Response({
            'code': 404,
            'message': '指定的学生不存在'
        }, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        # 如果报告已创建，更新状态为失败
        if 'report' in locals():
            report.status = 'failed'
            report.report_content = f'生成失败：{str(e)}'
            report.save()

        return Response({
            'code': 500,
            'message': f'报告生成失败：{str(e)}'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@extend_schema(
    parameters=[
        OpenApiParameter('page', int, description='页码'),
        OpenApiParameter('page_size', int, description='每页数量'),
        OpenApiParameter('status', str, description='状态筛选'),
        OpenApiParameter('period', str, description='时间段筛选'),
    ],
    responses={
        200: OpenApiResponse(description="获取成功"),
    },
    description="获取学习报告列表"
)
@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def list_reports(request):
    """获取学习报告列表"""
    # 获取查询参数
    page = int(request.GET.get('page', 1))
    page_size = int(request.GET.get('page_size', 10))
    status_filter = request.GET.get('status', None)
    period_filter = request.GET.get('period', None)

    # 构建查询
    queryset = LearningReport.objects.all()

    # 根据用户角色过滤
    if request.user.role == 'student':
        queryset = queryset.filter(student=request.user)

    # 状态过滤
    if status_filter:
        queryset = queryset.filter(status=status_filter)

    # 时间段过滤
    if period_filter:
        queryset = queryset.filter(period=period_filter)

    # 分页
    total = queryset.count()
    start = (page - 1) * page_size
    end = start + page_size
    reports = queryset.select_related('student', 'generated_by')[start:end]

    # 序列化
    serializer = LearningReportListSerializer(reports, many=True)

    return Response({
        'code': 200,
        'message': '获取成功',
        'data': {
            'reports': serializer.data,
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
        200: LearningReportDetailSerializer,
        404: OpenApiResponse(description="报告不存在"),
        403: OpenApiResponse(description="权限不足"),
    },
    description="获取学习报告详情"
)
@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def get_report_detail(request, report_id):
    """获取学习报告详情"""
    report = get_object_or_404(LearningReport, id=report_id)

    # 权限检查：学生只能查看自己的报告，教师可以查看所有报告
    if request.user.role == 'student' and report.student != request.user:
        return Response({
            'code': 403,
            'message': '权限不足，只能查看自己的报告'
        }, status=status.HTTP_403_FORBIDDEN)

    serializer = LearningReportDetailSerializer(report)
    return Response({
        'code': 200,
        'message': '获取成功',
        'data': serializer.data
    }, status=status.HTTP_200_OK)
