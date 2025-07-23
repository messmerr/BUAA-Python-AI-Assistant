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
        fields = ['title', 'description', 'questions', 'deadline', 'total_score']
    
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
    
    class Meta:
        model = Assignment
        fields = [
            'id', 'title', 'description', 'deadline', 
            'total_score', 'submission_count', 'created_at'
        ]


class AssignmentDetailSerializer(serializers.ModelSerializer):
    """作业详情序列化器 - 严格按照API规范"""
    questions = QuestionSerializer(many=True, read_only=True)
    
    class Meta:
        model = Assignment
        fields = [
            'id', 'title', 'description', 'questions', 
            'deadline', 'total_score', 'created_at'
        ]


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
    
    def _grade_answer_with_ai(self, question, student_answer):
        """使用AI批改单个答案"""
        try:
            prompt = f"""
请作为一名专业教师，批改以下学生答案：

题目：{question.question_text}
参考答案：{question.reference_answer}
学生答案：{student_answer}
满分：{question.score}分

请按以下格式回复：
分数：[0-{question.score}]
反馈：[具体的批改意见和建议]

评分标准：
- 答案完全正确且完整：满分
- 答案基本正确但有小错误：80-90%分数
- 答案部分正确：50-70%分数
- 答案有严重错误但有部分理解：20-40%分数
- 答案完全错误或无关：0分
"""
            
            ai_response = ask_gemini(prompt, temperature=0.3)
            
            # 解析AI响应
            lines = ai_response.strip().split('\n')
            score = 0
            feedback = "AI批改暂时不可用"
            
            for line in lines:
                if line.startswith('分数：'):
                    try:
                        score_text = line.replace('分数：', '').strip()
                        score = int(float(score_text))
                        score = max(0, min(score, question.score))  # 确保分数在有效范围内
                    except:
                        score = 0
                elif line.startswith('反馈：'):
                    feedback = line.replace('反馈：', '').strip()
            
            return score, feedback
            
        except Exception as e:
            # AI批改失败时的降级处理
            return 0, f"AI批改失败，请联系教师人工批改。错误：{str(e)}"
    
    def _generate_overall_feedback(self, submission):
        """生成总体反馈"""
        try:
            answers = submission.answers.all()
            total_possible = submission.assignment.total_score
            total_obtained = submission.obtained_score
            percentage = (total_obtained / total_possible) * 100 if total_possible > 0 else 0
            
            prompt = f"""
请为学生的作业提交生成一个总体评价和建议：

作业标题：{submission.assignment.title}
总分：{total_possible}分
获得分数：{total_obtained}分
得分率：{percentage:.1f}%

各题详情：
"""
            for answer in answers:
                prompt += f"- {answer.question.question_text[:50]}... 得分：{answer.obtained_score}/{answer.question.score}\n"
            
            prompt += "\n请提供简洁的总体评价和学习建议（100字以内）："
            
            overall_feedback = ask_gemini(prompt, temperature=0.5, max_tokens=200)
            return overall_feedback.strip()
            
        except Exception:
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
        extra_kwargs = {
            'id': {'source': 'id', 'read_only': True},
        }
