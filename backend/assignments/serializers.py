from rest_framework import serializers
from django.utils import timezone
from .models import Assignment, Question, Submission, Answer
from ai_services import ask_gemini


class QuestionSerializer(serializers.ModelSerializer):
    """问题序列化器 - 严格按照API规范"""
    
    class Meta:
        model = Question
        fields = ['id', 'question_text', 'reference_answer', 'score']
        extra_kwargs = {
            'id': {'read_only': True},
        }


class AssignmentCreateSerializer(serializers.ModelSerializer):
    """作业创建序列化器 - 严格按照API规范"""
    questions = QuestionSerializer(many=True)

    class Meta:
        model = Assignment
        fields = ['title', 'description', 'subject', 'questions', 'deadline', 'total_score']
    
    def create(self, validated_data):
        """创建作业和问题"""
        questions_data = validated_data.pop('questions')
        assignment = Assignment.objects.create(**validated_data)
        
        for i, question_data in enumerate(questions_data):
            Question.objects.create(
                assignment=assignment,
                order=i + 1,
                **question_data
            )
        
        return assignment


class AssignmentListSerializer(serializers.ModelSerializer):
    """作业列表序列化器 - 严格按照API规范"""
    is_completed = serializers.SerializerMethodField()
    obtained_score = serializers.SerializerMethodField()

    class Meta:
        model = Assignment
        fields = [
            'id', 'title', 'description', 'subject', 'deadline',
            'total_score', 'submission_count', 'is_completed',
            'obtained_score', 'created_at'
        ]

    def get_is_completed(self, obj):
        """获取学生是否已完成作业"""
        request = self.context.get('request')
        if request and request.user.role == 'student':
            return Submission.objects.filter(
                assignment=obj,
                student=request.user
            ).exists()
        return None

    def get_obtained_score(self, obj):
        """获取学生获得的分数"""
        request = self.context.get('request')
        if request and request.user.role == 'student':
            try:
                submission = Submission.objects.get(
                    assignment=obj,
                    student=request.user
                )
                return submission.obtained_score
            except Submission.DoesNotExist:
                return None
        return None


class AssignmentDetailSerializer(serializers.ModelSerializer):
    """作业详情序列化器 - 严格按照API规范"""
    questions = QuestionSerializer(many=True, read_only=True)
    is_completed = serializers.SerializerMethodField()
    obtained_score = serializers.SerializerMethodField()

    class Meta:
        model = Assignment
        fields = [
            'id', 'title', 'description', 'subject', 'questions',
            'deadline', 'total_score', 'is_completed',
            'obtained_score', 'created_at'
        ]

    def get_is_completed(self, obj):
        """获取学生是否已完成作业"""
        request = self.context.get('request')
        if request and request.user.role == 'student':
            return Submission.objects.filter(
                assignment=obj,
                student=request.user
            ).exists()
        return None

    def get_obtained_score(self, obj):
        """获取学生获得的分数"""
        request = self.context.get('request')
        if request and request.user.role == 'student':
            try:
                submission = Submission.objects.get(
                    assignment=obj,
                    student=request.user
                )
                return submission.obtained_score
            except Submission.DoesNotExist:
                return None
        return None


class AnswerSubmissionSerializer(serializers.Serializer):
    """答案提交序列化器 - 严格按照API规范"""
    question_id = serializers.UUIDField()
    answer_text = serializers.CharField()


class AssignmentSubmissionSerializer(serializers.Serializer):
    """作业提交序列化器 - 严格按照API规范"""
    answers = AnswerSubmissionSerializer(many=True)
    
    def validate_answers(self, value):
        """验证答案数据"""
        if not value:
            raise serializers.ValidationError("至少需要提交一个答案")
        return value
    
    def create(self, validated_data):
        """创建作业提交并进行AI批改"""
        assignment = self.context['assignment']
        student = self.context['student']
        answers_data = validated_data['answers']
        
        # 检查是否已经提交过
        if Submission.objects.filter(assignment=assignment, student=student).exists():
            raise serializers.ValidationError("您已经提交过这个作业")
        
        # 创建提交记录
        submission = Submission.objects.create(
            assignment=assignment,
            student=student,
            status='grading'
        )
        
        # 创建答案记录并进行AI批改
        total_score = 0
        for answer_data in answers_data:
            try:
                question = Question.objects.get(
                    id=answer_data['question_id'],
                    assignment=assignment
                )
            except Question.DoesNotExist:
                submission.delete()
                raise serializers.ValidationError(f"问题 {answer_data['question_id']} 不存在")
            
            ai_score, ai_feedback = self._check_exact_match(
                question, answer_data['answer_text']
            )
            
            if ai_score is None:
            # 使用AI批改答案
                ai_score, ai_feedback = self._grade_answer_with_ai(
                    question, answer_data['answer_text']
                )
            
            # 创建答案记录
            Answer.objects.create(
                submission=submission,
                question=question,
                answer_text=answer_data['answer_text'],
                obtained_score=ai_score,
                ai_feedback=ai_feedback
            )
            
            total_score += ai_score
        
        # 更新提交记录
        submission.obtained_score = total_score
        submission.status = 'graded'
        submission.graded_at = timezone.now()
        submission.overall_feedback = self._generate_overall_feedback(submission)
        submission.save()
        
        return submission
    
    def _check_exact_match(self, question, student_answer):
        normalized_reference = question.reference_answer
        normalized_student = student_answer
        
        print(f"[DEBUG] 标准答案: '{normalized_reference}'")
        print(f"[DEBUG] 学生答案: '{normalized_student}'")
        
        # 完全匹配
        if normalized_reference == normalized_student:
            return question.score, "你的答案完全正确！"
        
        return None, None
    
    def _grade_answer_with_ai(self, question, student_answer):
        """使用AI批改单个答案 - 使用XML标签格式"""
        try:
            prompt = f"""
请作为一名专业教师，批改以下学生答案。

题目：{question.question_text}
参考答案：{question.reference_answer}
学生答案：{student_answer}
满分：{question.score}分

评分标准：
- 答案完全正确且完整：满分
- 答案基本正确但有小错误：80-90%分数
- 答案部分正确：50-70%分数
- 答案有严重错误但有部分理解：20-40%分数
- 答案完全错误或无关：0分

请严格按照以下XML格式回复，不要添加任何其他内容：

<score>{question.score}分制下的具体分数，只写数字</score>
<feedback>详细的批改意见和建议，包括优点、不足和改进建议</feedback>
"""

            print(f"[DEBUG] 开始AI批改，题目：{question.question_text[:30]}...")
            ai_response = ask_gemini(prompt, temperature=0.3)
            print(f"[DEBUG] AI响应：{ai_response[:200]}...")

            # 使用XML标签解析AI响应
            score = 0
            feedback = "AI批改暂时不可用"

            # 解析分数标签
            try:
                import re
                score_match = re.search(r'<score>(.*?)</score>', ai_response, re.DOTALL)
                if score_match:
                    score_text = score_match.group(1).strip()
                    # 提取数字
                    score_numbers = re.findall(r'\d+', score_text)
                    if score_numbers:
                        score = int(score_numbers[0])
                        score = max(0, min(score, question.score))  # 确保分数在有效范围内
                        print(f"[DEBUG] 解析得分：{score}")
                    else:
                        print(f"[DEBUG] 分数标签中未找到数字：{score_text}")
                else:
                    print(f"[DEBUG] 未找到<score>标签")
            except Exception as parse_error:
                print(f"[DEBUG] 分数解析失败：{parse_error}")
                score = 0

            # 解析反馈标签
            try:
                feedback_match = re.search(r'<feedback>(.*?)</feedback>', ai_response, re.DOTALL)
                if feedback_match:
                    feedback = feedback_match.group(1).strip()
                    print(f"[DEBUG] 解析反馈：{feedback[:50]}...")
                else:
                    print(f"[DEBUG] 未找到<feedback>标签")
                    # 如果没有找到标签，尝试使用整个响应作为反馈
                    feedback = ai_response.strip()
            except Exception as parse_error:
                print(f"[DEBUG] 反馈解析失败：{parse_error}")
                feedback = ai_response.strip()

            print(f"[DEBUG] 最终结果：分数={score}, 反馈长度={len(feedback)}")
            return score, feedback

        except Exception as e:
            # AI批改失败时的降级处理
            print(f"[DEBUG] AI批改异常：{str(e)}")
            return 0, f"AI批改失败，请联系教师人工批改。错误：{str(e)}"
    
    def _generate_overall_feedback(self, submission):
        """生成总体反馈 - 使用XML标签格式"""
        try:
            answers = submission.answers.all()
            total_possible = submission.assignment.total_score
            total_obtained = submission.obtained_score
            percentage = (total_obtained / total_possible) * 100 if total_possible > 0 else 0

            prompt = f"""
请为学生的作业提交生成一个总体评价和建议。

作业标题：{submission.assignment.title}
总分：{total_possible}分
获得分数：{total_obtained}分
得分率：{percentage:.1f}%

各题详情：
"""
            for answer in answers:
                prompt += f"- {answer.question.question_text[:50]}... 得分：{answer.obtained_score}/{answer.question.score}\n"

            prompt += """
请严格按照以下XML格式回复，提供简洁的总体评价和学习建议（100字以内）：

<overall_feedback>总体评价和学习建议</overall_feedback>
"""

            ai_response = ask_gemini(prompt, temperature=0.5, max_tokens=200)

            # 解析总体反馈标签
            try:
                import re
                feedback_match = re.search(r'<overall_feedback>(.*?)</overall_feedback>', ai_response, re.DOTALL)
                if feedback_match:
                    return feedback_match.group(1).strip()
                else:
                    # 如果没有找到标签，使用整个响应
                    return ai_response.strip()
            except:
                return ai_response.strip()

        except Exception:
            # 降级处理
            if percentage >= 90:
                return "优秀！继续保持这种学习状态。"
            elif percentage >= 80:
                return "良好，还有进步空间，建议复习错误的知识点。"
            elif percentage >= 60:
                return "及格，需要加强基础知识的学习和理解。"
            else:
                return "需要努力，建议重新学习相关知识点并多做练习。"


class AnswerDetailSerializer(serializers.ModelSerializer):
    """答案详情序列化器 - 严格按照API规范"""
    question_id = serializers.UUIDField(source='question.id')
    question_text = serializers.CharField(source='question.question_text')
    reference_answer = serializers.CharField(source='question.reference_answer')
    score = serializers.IntegerField(source='question.score')
    student_answer = serializers.CharField(source='answer_text')
    
    class Meta:
        model = Answer
        fields = [
            'question_id', 'question_text', 'student_answer', 
            'reference_answer', 'score', 'obtained_score', 'ai_feedback'
        ]


class SubmissionDetailSerializer(serializers.ModelSerializer):
    """提交详情序列化器 - 严格按照API规范"""
    assignment_title = serializers.CharField(source='assignment.title')
    total_score = serializers.IntegerField(source='assignment.total_score')
    answers = AnswerDetailSerializer(many=True, read_only=True)

    class Meta:
        model = Submission
        fields = [
            'id', 'assignment_title', 'submitted_at', 'graded_at',
            'total_score', 'obtained_score', 'answers', 'overall_feedback'
        ]
