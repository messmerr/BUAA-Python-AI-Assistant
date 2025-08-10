from rest_framework import serializers
from .models import QASession, QAMessage, QAQuestion, QAAnswer
from ai_services import ask_gemini


# 新的会话和消息序列化器
class QAMessageSerializer(serializers.ModelSerializer):
    """消息序列化器"""
    class Meta:
        model = QAMessage
        fields = ['id', 'role', 'content', 'created_at']


class QASessionListSerializer(serializers.ModelSerializer):
    """会话列表序列化器"""
    last_message = serializers.SerializerMethodField()
    message_count = serializers.SerializerMethodField()

    class Meta:
        model = QASession
        fields = ['id', 'subject', 'created_at', 'updated_at', 'last_message', 'message_count']

    def get_last_message(self, obj):
        """获取最后一条消息"""
        last_message = obj.messages.last()
        if last_message:
            return {
                'role': last_message.role,
                'content': last_message.content[:100] + ('...' if len(last_message.content) > 100 else ''),
                'created_at': last_message.created_at
            }
        return None

    def get_message_count(self, obj):
        """获取消息数量"""
        return obj.messages.count()


class QASessionDetailSerializer(serializers.ModelSerializer):
    """会话详情序列化器"""
    messages = QAMessageSerializer(many=True, read_only=True)

    class Meta:
        model = QASession
        fields = ['id', 'subject', 'created_at', 'updated_at', 'messages']


class ChatMessageCreateSerializer(serializers.Serializer):
    """聊天消息创建序列化器"""
    session_id = serializers.UUIDField(required=False, allow_null=True)
    message = serializers.CharField(max_length=2000)
    subject = serializers.CharField(max_length=100, required=False, default="通用")

    def create_or_get_session(self, student, subject="通用"):
        """创建或获取会话"""
        session_id = self.validated_data.get('session_id')

        if session_id:
            # 获取现有会话
            try:
                session = QASession.objects.get(id=session_id, student=student)
                return session
            except QASession.DoesNotExist:
                raise serializers.ValidationError("会话不存在")
        else:
            # 创建新会话
            session = QASession.objects.create(
                student=student,
                subject=subject
            )
            return session

    def save_message(self, session, role, content):
        """保存消息"""
        return QAMessage.objects.create(
            session=session,
            role=role,
            content=content
        )

    def get_context_messages(self, session, limit=10):
        """获取上下文消息"""
        return session.messages.order_by('-created_at')[:limit][::-1]


# 保留旧的序列化器以兼容现有API
class QAQuestionCreateSerializer(serializers.ModelSerializer):
    """问题创建序列化器 - 严格按照API规范"""
    ai_answer = serializers.CharField(read_only=True)

    class Meta:
        model = QAQuestion
        fields = ['question_text', 'subject', 'context', 'ai_answer']

    def create(self, validated_data):
        """创建问题并生成AI回答"""
        # 创建问题
        question = QAQuestion.objects.create(
            student=self.context['student'],
            **validated_data
        )

        # 生成AI回答
        ai_answer = self._generate_ai_answer(question)

        # 创建回答记录
        QAAnswer.objects.create(
            question=question,
            ai_answer=ai_answer
        )

        # 将AI回答添加到question对象中，用于序列化返回
        question.ai_answer = ai_answer

        return question
    
    def _generate_ai_answer(self, question):
        """使用AI生成回答 - 使用XML标签格式"""
        try:
            # 构建提示词
            prompt = f"""
你是一位专业的AI助教，请回答学生的问题。

学生问题：{question.question_text}
"""
            
            # 如果有学科信息，添加到提示词中
            if question.subject:
                prompt += f"学科领域：{question.subject}\n"
            
            # 如果有上下文信息，添加到提示词中
            if question.context:
                prompt += f"问题背景：{question.context}\n"
            
            prompt += """
请提供准确、详细、易懂的回答。回答应该：
1. 直接回答问题的核心
2. 提供必要的解释和背景知识
3. 如果适用，给出具体的例子
4. 语言简洁明了，适合学生理解

请严格按照以下XML格式回复：

<answer>详细的回答内容</answer>
"""
            
            ai_response = ask_gemini(prompt, temperature=0.7)
            
            # 解析AI回答
            try:
                import re
                answer_match = re.search(r'<answer>(.*?)</answer>', ai_response, re.DOTALL)
                if answer_match:
                    answer = answer_match.group(1).strip()
                    return answer
                else:
                    return ai_response.strip()
            except Exception as parse_error:
                return ai_response.strip()
                
        except Exception as e:
            return f"抱歉，AI助教暂时无法回答您的问题。请稍后重试或联系人工老师。错误信息：{str(e)}"


class QAAnswerSerializer(serializers.ModelSerializer):
    """回答序列化器 - 严格按照API规范"""
    
    class Meta:
        model = QAAnswer
        fields = ['id', 'ai_answer', 'created_at']


class QAQuestionDetailSerializer(serializers.ModelSerializer):
    """问题详情序列化器 - 严格按照API规范"""
    answer = QAAnswerSerializer(read_only=True)
    student_name = serializers.CharField(source='student.real_name', read_only=True)
    
    class Meta:
        model = QAQuestion
        fields = [
            'id', 'question_text', 'subject', 'context', 
            'created_at', 'student_name', 'answer'
        ]


class QAQuestionListSerializer(serializers.ModelSerializer):
    """问题列表序列化器 - 严格按照API规范"""
    ai_answer = serializers.SerializerMethodField()

    class Meta:
        model = QAQuestion
        fields = [
            'id', 'question_text', 'ai_answer', 'subject', 'created_at'
        ]

    def get_ai_answer(self, obj):
        """获取AI回答"""
        try:
            return obj.answer.ai_answer if hasattr(obj, 'answer') and obj.answer else ""
        except:
            return ""
