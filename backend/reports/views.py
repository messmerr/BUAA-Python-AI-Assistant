from rest_framework import status, permissions
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from django.db.models import Q, Avg, Count
from django.utils import timezone
from datetime import datetime, timedelta
from drf_spectacular.utils import extend_schema, OpenApiResponse, OpenApiParameter
import logging

logger = logging.getLogger(__name__)

from .models import LearningReport
from .serializers import (
    LearningReportCreateSerializer,
    LearningReportListSerializer,
    LearningReportDetailSerializer,
    ClassReportCreateSerializer
)
try:
    from accounts.models import User
except ImportError:
    from django.contrib.auth import get_user_model
    User = get_user_model()

try:
    from assignments.models import Assignment, Submission, Answer
except ImportError as e:
    Assignment = None
    Submission = None
    Answer = None

try:
    from qa.models import QASession, QAMessage, QAQuestion
except ImportError as e:
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
            pass

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
            pass

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
            pass

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
                if hasattr(submission, 'obtained_score') and hasattr(submission, 'assignment'):
                    total_score += submission.obtained_score or 0
                    total_possible += getattr(submission.assignment, 'total_score', 0)
        except Exception as e:
            pass

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
                if hasattr(submission, 'assignment') and hasattr(submission, 'obtained_score'):
                    assignment_detail = {
                        'title': getattr(submission.assignment, 'title', '未知作业'),
                        'subject': getattr(submission.assignment, 'subject', '未知科目'),
                        'score': submission.obtained_score or 0,
                        'max_score': getattr(submission.assignment, 'total_score', 0),
                        'score_percentage': round((submission.obtained_score / submission.assignment.total_score * 100), 2) if getattr(submission.assignment, 'total_score', 0) > 0 else 0,
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
                                    'score': getattr(answer, 'obtained_score', 0),
                                    'max_score': getattr(answer.question, 'score', 0),
                                    'feedback': getattr(answer, 'ai_feedback', '无反馈')[:200] + ('...' if len(getattr(answer, 'ai_feedback', '')) > 200 else '')
                                }
                                assignment_detail['questions_performance'].append(question_perf)
                    except Exception as e:
                        pass

                    context_data['assignments_detail'].append(assignment_detail)
        except Exception as e:
            pass

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
                        pass
        except Exception as e:
            pass

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
            pass

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
            ai_response = ask_gemini(prompt, temperature=0.7)
            return ai_response
        except Exception as e:
            return f"报告生成失败，错误信息：{str(e)}"


def generate_simple_report(student, period, subjects, statistics, data=None):
    """生成简化版报告（当AI生成失败时使用）- 优化版"""
    
    # 基础信息
    basic_info = f"""
# {student.real_name} 学习报告

## 基本信息
- 学生姓名：{student.real_name}
- 学号：{student.student_id}
- 报告时间段：{period}
- 涉及科目：{', '.join(subjects) if subjects else '所有科目'}

## 学习统计概览
- 总作业数：{statistics['total_assignments']}
- 已完成作业数：{statistics['completed_assignments']}
- 平均得分：{statistics['average_score']}%
- 提问次数：{statistics['total_questions']}
"""

    # 如果没有data，返回基础版本
    if not data:
        return basic_info + """
## 学习评价
数据收集过程中遇到问题，仅能提供基础统计信息。建议联系技术支持获取详细报告。
"""

    # 作业完成情况详细分析
    assignment_analysis = "\n## 作业完成情况分析\n"
    
    if statistics['total_assignments'] > 0:
        completion_rate = round(statistics['completed_assignments']/statistics['total_assignments']*100, 2)
        assignment_analysis += f"### 完成率分析\n"
        assignment_analysis += f"您的作业完成率为 {completion_rate}%，"
        
        if completion_rate >= 90:
            assignment_analysis += "表现非常优秀，学习态度积极主动。\n\n"
        elif completion_rate >= 70:
            assignment_analysis += "表现良好，建议继续保持。\n\n"
        elif completion_rate >= 50:
            assignment_analysis += "完成情况一般，建议提高学习积极性。\n\n"
        else:
            assignment_analysis += "完成率偏低，需要加强时间管理和学习计划。\n\n"
    
    # 分析具体作业表现
    if data.get('submissions'):
        assignment_analysis += "### 作业得分情况\n"
        try:
            scores = []
            subjects_performance = {}
            
            for submission in data['submissions']:
                if hasattr(submission, 'obtained_score') and hasattr(submission, 'assignment'):
                    score = submission.obtained_score or 0
                    max_score = getattr(submission.assignment, 'total_score', 0)
                    if max_score > 0:
                        percentage = round((score / max_score) * 100, 2)
                        scores.append(percentage)
                        
                        # 按科目统计
                        subject = getattr(submission.assignment, 'subject', '未知科目')
                        if subject not in subjects_performance:
                            subjects_performance[subject] = []
                        subjects_performance[subject].append(percentage)
            
            if scores:
                avg_score = round(sum(scores) / len(scores), 2)
                max_score = max(scores)
                min_score = min(scores)
                
                assignment_analysis += f"- 平均得分：{avg_score}%\n"
                assignment_analysis += f"- 最高得分：{max_score}%\n"
                assignment_analysis += f"- 最低得分：{min_score}%\n"
                
                # 成绩稳定性分析
                if max_score - min_score <= 20:
                    assignment_analysis += "- 成绩表现稳定，学习状态良好\n\n"
                else:
                    assignment_analysis += "- 成绩波动较大，建议保持稳定的学习节奏\n\n"
                
                # 各科目表现
                if len(subjects_performance) > 1:
                    assignment_analysis += "### 各科目表现\n"
                    for subject, subject_scores in subjects_performance.items():
                        subject_avg = round(sum(subject_scores) / len(subject_scores), 2)
                        assignment_analysis += f"- {subject}：平均 {subject_avg}%（{len(subject_scores)}次作业）\n"
                    assignment_analysis += "\n"
        except Exception as e:
            assignment_analysis += "作业详情分析遇到问题，请联系技术支持。\n\n"
    
    # 学习行为分析
    behavior_analysis = "\n## 学习行为分析\n"
    
    # 问答活跃度分析
    total_qa = statistics['total_questions']
    if total_qa > 0:
        behavior_analysis += f"### 提问活跃度\n"
        behavior_analysis += f"在此期间您共提问 {total_qa} 次，"
        
        if total_qa >= 20:
            behavior_analysis += "学习非常主动，善于思考和提问。\n\n"
        elif total_qa >= 10:
            behavior_analysis += "学习比较主动，保持良好的提问习惯。\n\n"
        elif total_qa >= 5:
            behavior_analysis += "有一定的学习主动性，建议多与AI助教互动。\n\n"
        else:
            behavior_analysis += "提问较少，建议遇到问题时积极寻求帮助。\n\n"
        
        # 分析问答内容
        if data.get('qa_sessions') or data.get('old_qa_questions'):
            behavior_analysis += "### 问题类型分析\n"
            try:
                subjects_qa = {}
                
                # 统计新版问答
                if data.get('qa_sessions'):
                    for session in data['qa_sessions']:
                        subject = getattr(session, 'subject', '未知科目')
                        subjects_qa[subject] = subjects_qa.get(subject, 0) + 1
                
                # 统计旧版问答
                if data.get('old_qa_questions'):
                    for question in data['old_qa_questions']:
                        subject = getattr(question, 'subject', '未知科目')
                        subjects_qa[subject] = subjects_qa.get(subject, 0) + 1
                
                if subjects_qa:
                    for subject, count in subjects_qa.items():
                        behavior_analysis += f"- {subject}：{count} 次提问\n"
                    
                    # 找出最关注的科目
                    most_asked_subject = max(subjects_qa, key=subjects_qa.get)
                    behavior_analysis += f"\n您最关注的科目是 **{most_asked_subject}**，说明在该科目上投入了更多精力。\n\n"
            except Exception as e:
                behavior_analysis += "问题类型分析遇到问题。\n\n"
    else:
        behavior_analysis += "### 提问活跃度\n"
        behavior_analysis += "在此期间您没有提问记录，建议遇到学习问题时积极与AI助教互动。\n\n"
    
    # 改进建议
    suggestions = "\n## 个性化学习建议\n"
    
    # 基于完成率的建议
    if statistics['total_assignments'] > 0:
        completion_rate = statistics['completed_assignments']/statistics['total_assignments']
        if completion_rate < 0.8:
            suggestions += "### 📝 作业完成方面\n"
            suggestions += "- 制定每日学习计划，确保按时完成作业\n"
            suggestions += "- 设置作业提醒，避免遗漏\n"
            suggestions += "- 如遇困难及时寻求帮助\n\n"
    
    # 基于得分的建议
    if statistics['average_score'] < 70:
        suggestions += "### 📈 成绩提升方面\n"
        suggestions += "- 加强基础知识复习\n"
        suggestions += "- 多做练习题巩固知识点\n"
        suggestions += "- 分析错题，找出薄弱环节\n\n"
    elif statistics['average_score'] >= 85:
        suggestions += "### 🎯 优秀保持方面\n"
        suggestions += "- 继续保持良好的学习习惯\n"
        suggestions += "- 可以尝试更有挑战性的题目\n"
        suggestions += "- 帮助其他同学，巩固自己的知识\n\n"
    
    # 基于提问情况的建议
    if total_qa < 5:
        suggestions += "### 💬 互动学习方面\n"
        suggestions += "- 遇到疑问时主动提问\n"
        suggestions += "- 利用AI助教解决学习难题\n"
        suggestions += "- 培养批判性思维，多问为什么\n\n"
    
    # 通用建议
    suggestions += "### 🌟 通用学习建议\n"
    suggestions += "- 定期复习已学知识，巩固记忆\n"
    suggestions += "- 保持良好的学习节奏，避免临时抱佛脚\n"
    suggestions += "- 多与同学和老师交流，分享学习心得\n"
    suggestions += "- 关注学习方法，提高学习效率\n\n"
    
    footer = "---\n*本报告基于您的学习数据自动生成，如需更详细的分析请联系任课教师*"
    
    return basic_info + assignment_analysis + behavior_analysis + suggestions + footer


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
            student_id = serializer.validated_data.get('student_id')
            
            if not student_id:
                return Response({
                    'code': 400,
                    'message': '教师生成报告时必须指定学生ID'
                }, status=status.HTTP_400_BAD_REQUEST)
            
            try:
                student = User.objects.get(id=student_id, role='student')
            except User.DoesNotExist:
                return Response({
                    'code': 404,
                    'message': '指定的学生不存在'
                }, status=status.HTTP_404_NOT_FOUND)
        else:
            # 学生只能为自己生成报告
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
        except Exception as e:
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
        except Exception as e:
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
        except Exception as e:
            report_content = generate_simple_report(student, period, subjects, statistics, data)  # 传入data参数

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
    """获取报告列表"""
    # 学生只能看到自己的报告，教师可以看到所有报告
    if request.user.role == 'student':
        reports = LearningReport.objects.filter(student=request.user)
    else:  # teacher
        reports = LearningReport.objects.all()
    
    # 获取查询参数
    page = int(request.GET.get('page', 1))
    page_size = int(request.GET.get('page_size', 10))
    status_filter = request.GET.get('status', None)
    period_filter = request.GET.get('period', None)

    # 构建查询
    queryset = reports

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


def collect_class_data(period, subjects):
    """收集班级数据"""
    from django.contrib.auth import get_user_model
    User = get_user_model()
    
    # 获取时间范围
    start_time, end_time = get_time_range(period)
    
    # 获取所有学生
    students = User.objects.filter(role='student')
    
    # 直接查询所有相关数据，而不是逐个学生收集
    all_assignments = []
    all_submissions = []
    all_qa_sessions = []
    all_old_qa_questions = []
    
    # 构建查询条件
    assignment_filter = Q(created_at__gte=start_time, created_at__lte=end_time)
    qa_filter = Q(created_at__gte=start_time, created_at__lte=end_time)

    if subjects:
        assignment_filter &= Q(subject__in=subjects)
        qa_filter &= Q(subject__in=subjects)

    # 直接查询所有作业数据
    if Assignment is not None and Submission is not None:
        try:
            all_assignments = list(Assignment.objects.filter(assignment_filter))
            all_submissions = list(Submission.objects.filter(
                assignment__in=all_assignments,
                student__role='student'  # 确保只查询学生的提交
            ).select_related('assignment', 'student').prefetch_related('answers__question'))
            pass
        except Exception as e:
            pass

    # 直接查询所有问答数据
    if QASession is not None:
        try:
            all_qa_sessions = list(QASession.objects.filter(
                student__role='student',
                updated_at__gte=start_time,
                updated_at__lte=end_time
            ).select_related('student').prefetch_related('messages'))
            if subjects:
                all_qa_sessions = [s for s in all_qa_sessions if s.subject in subjects]
            pass
        except Exception as e:
            pass

    # 查询旧的QA数据
    if QAQuestion is not None:
        try:
            all_old_qa_questions = list(QAQuestion.objects.filter(
                student__role='student',
                created_at__gte=start_time,
                created_at__lte=end_time
            ).select_related('student', 'answer'))
            if subjects:
                all_old_qa_questions = [q for q in all_old_qa_questions if q.subject in subjects]
            pass
        except Exception as e:
            pass
    
    return {
        'students': list(students),
        'assignments': all_assignments,
        'submissions': all_submissions,
        'qa_sessions': all_qa_sessions,
        'old_qa_questions': all_old_qa_questions,
        'time_range': (start_time, end_time)
    }

def calculate_class_statistics(data):
    """计算班级统计数据"""
    students = data['students']
    submissions = data['submissions']
    assignments = data['assignments']
    qa_sessions = data['qa_sessions']
    old_qa_questions = data['old_qa_questions']
    
    # 基础统计
    total_students = len(students)
    total_assignments = len(assignments)
    total_submissions = len(submissions)
    
    # 完成率统计
    completion_rate = (total_submissions / (total_students * total_assignments) * 100) if (total_students * total_assignments) > 0 else 0
    
    # 按学生计算平均得分率和分数分布
    student_averages = []
    score_distribution = {'0-60': 0, '60-70': 0, '70-80': 0, '80-90': 0, '90-100': 0}
    
    for student in students:
        student_submissions = [s for s in submissions if hasattr(s, 'student') and s.student.id == student.id]
        student_scores = []
        
        for submission in student_submissions:
            if hasattr(submission, 'obtained_score') and hasattr(submission, 'assignment'):
                score = submission.obtained_score or 0
                max_score = getattr(submission.assignment, 'total_score', 0)
                if max_score > 0:
                    percentage = (score / max_score) * 100
                    student_scores.append(percentage)
        
        # 计算学生平均得分率
        if student_scores:
            student_avg = sum(student_scores) / len(student_scores)
            student_averages.append(student_avg)
            
            # 按学生平均得分率统计分布
            if student_avg < 60:
                score_distribution['0-60'] += 1
            elif student_avg < 70:
                score_distribution['60-70'] += 1
            elif student_avg < 80:
                score_distribution['70-80'] += 1
            elif student_avg < 90:
                score_distribution['80-90'] += 1
            else:
                score_distribution['90-100'] += 1
    
    # 班级平均得分率
    average_score = sum(student_averages) / len(student_averages) if student_averages else 0
    
    # 学生表现统计
    student_performance = []
    for student in students:
        student_submissions = [s for s in submissions if hasattr(s, 'student') and s.student.id == student.id]
        student_scores = []
        
        for submission in student_submissions:
            if hasattr(submission, 'obtained_score') and hasattr(submission, 'assignment'):
                score = submission.obtained_score or 0
                max_score = getattr(submission.assignment, 'total_score', 0)
                if max_score > 0:
                    student_scores.append((score / max_score) * 100)
        
        # 学生问答统计
        student_qa_count = 0
        if qa_sessions:
            student_qa_count += len([q for q in qa_sessions if hasattr(q, 'student') and q.student.id == student.id])
        if old_qa_questions:
            student_qa_count += len([q for q in old_qa_questions if hasattr(q, 'student') and q.student.id == student.id])
        
        student_performance.append({
            'student_name': student.real_name,
            'student_id': student.student_id,
            'completed_assignments': len(student_submissions),
            'average_score': round(sum(student_scores) / len(student_scores), 2) if student_scores else 0,
            'qa_count': student_qa_count
        })
    
    # 问答统计
    total_questions = len(qa_sessions) + len(old_qa_questions)
    
    return {
        'total_students': total_students,
        'total_assignments': total_assignments,
        'total_submissions': total_submissions,
        'completion_rate': round(completion_rate, 2),
        'average_score': round(average_score, 2),
        'score_distribution': score_distribution,
        'student_performance': sorted(student_performance, key=lambda x: x['average_score'], reverse=True),
        'total_questions': total_questions
    }

def generate_class_report_content(data, statistics, period, subjects):
    """生成班级报告内容"""
    start_time, end_time = data['time_range']
    
    # 构建班级数据上下文
    context_data = {
        'time_period': {
            'period': period,
            'start_date': start_time.strftime('%Y-%m-%d') if start_time else '未知',
            'end_date': end_time.strftime('%Y-%m-%d') if end_time else '未知'
        },
        'subjects': subjects if subjects else ['所有科目'],
        'statistics': statistics,
        'top_students': statistics['student_performance'][:5],
        'bottom_students': statistics['student_performance'][-3:] if len(statistics['student_performance']) > 3 else [],
        'qa_analysis': []
    }
    
    # 分析高频问题
    try:
        question_keywords = {}
        for session in data.get('qa_sessions', []):
            if hasattr(session, 'subject'):
                subject = session.subject
                question_keywords[subject] = question_keywords.get(subject, 0) + 1
        
        for question in data.get('old_qa_questions', []):
            if hasattr(question, 'subject'):
                subject = question.subject
                question_keywords[subject] = question_keywords.get(subject, 0) + 1
        
        context_data['qa_analysis'] = sorted(question_keywords.items(), key=lambda x: x[1], reverse=True)[:5]
    except Exception as e:
        pass
    
    # 构建AI提示词
    prompt = f"""
你是一位专业的教育分析师，请根据以下班级的整体学习数据生成一份班级分析报告。

班级信息：
- 分析时间段：{context_data['time_period']['start_date']} 至 {context_data['time_period']['end_date']} ({period})
- 涉及科目：{', '.join(context_data['subjects'])}

班级统计：
- 班级总人数：{statistics['total_students']}
- 总作业数：{statistics['total_assignments']}
- 作业完成率：{statistics['completion_rate']}%
- 班级平均分：{statistics['average_score']}%
- 总提问次数：{statistics['total_questions']}

成绩分布：
{json.dumps(statistics['score_distribution'], ensure_ascii=False, indent=2)}

优秀学生（前5名）：
{json.dumps(context_data['top_students'], ensure_ascii=False, indent=2)}

需要关注的学生：
{json.dumps(context_data['bottom_students'], ensure_ascii=False, indent=2)}

高频问题科目：
{json.dumps(context_data['qa_analysis'], ensure_ascii=False, indent=2)}

请生成一份结构化的班级分析报告，包含以下部分：

1. **班级整体表现**
   - 整体学习状况评价
   - 完成率和成绩分析

2. **优秀表现**
   - 表现突出的学生
   - 值得推广的学习方法

3. **需要关注的问题**
   - 学习困难的学生
   - 普遍存在的问题

4. **常见问题汇总**
   - 高频提问的知识点
   - 学生普遍困惑的内容

5. **教学改进建议**
   - 针对班级情况的教学调整
   - 具体的改进措施

请用专业、客观的语言撰写报告，字数控制在800-1200字。
"""

    try:
        ai_response = ask_gemini(prompt, temperature=0.7)
        return ai_response
    except Exception as e:
        return f"班级报告生成失败，错误信息：{str(e)}"


@api_view(['POST'])
@permission_classes([IsTeacher])
def generate_class_report(request):
    """生成班级报告"""
    logger.info("generate_class_report 开始")
    
    # 验证请求数据
    serializer = ClassReportCreateSerializer(data=request.data)
    if not serializer.is_valid():
        logger.error(f"参数验证失败: {serializer.errors}")
        return Response({
            'code': 400,
            'message': '参数错误',
            'errors': serializer.errors
        }, status=status.HTTP_400_BAD_REQUEST)

    period = serializer.validated_data['period']
    subjects = serializer.validated_data.get('subjects', [])
    
    logger.info(f"验证通过 - 时间段: {period}, 科目: {subjects}")

    try:
        # 收集班级数据
        data = collect_class_data(period, subjects)

        # 计算统计数据
        statistics = calculate_class_statistics(data)

        # 生成AI报告内容
        report_content = generate_class_report_content(data, statistics, period, subjects)

        response_data = {
            'statistics': statistics,
            'report_content': report_content,
            'generated_at': timezone.now()
        }

        return Response({
            'code': 200,
            'message': '班级报告生成成功',
            'data': response_data
        }, status=status.HTTP_200_OK)

    except Exception as e:
        logger.error(f"班级报告生成异常: {str(e)}")
        return Response({
            'code': 500,
            'message': f'班级报告生成失败：{str(e)}'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


