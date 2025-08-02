from rest_framework import serializers
from django.contrib.auth import get_user_model
from django.db import models
from .models import ChatMessage

User = get_user_model()


class ChatUserSerializer(serializers.ModelSerializer):
    """聊天用户序列化器"""
    unread_count = serializers.SerializerMethodField()
    last_message = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ['id', 'username', 'real_name', 'role', 'unread_count', 'last_message']

    def get_unread_count(self, obj):
        request = self.context.get('request')
        if request and request.user:
            return ChatMessage.objects.filter(
                sender=obj,
                receiver=request.user,
                is_read=False
            ).count()
        return 0

    def get_last_message(self, obj):
        request = self.context.get('request')
        if request and request.user:
            last_msg = ChatMessage.objects.filter(
                models.Q(sender=obj, receiver=request.user) |
                models.Q(sender=request.user, receiver=obj)
            ).order_by('-created_at').first()
            
            if last_msg:
                return {
                    'content': last_msg.content,
                    'created_at': last_msg.created_at.isoformat(),
                    'is_read': last_msg.is_read
                }
        return None


class ChatMessageSerializer(serializers.ModelSerializer):
    """聊天消息序列化器"""
    sender_name = serializers.CharField(source='sender.real_name', read_only=True)
    receiver_name = serializers.CharField(source='receiver.real_name', read_only=True)

    class Meta:
        model = ChatMessage
        fields = ['id', 'sender', 'receiver', 'content', 'is_read', 'created_at', 'sender_name', 'receiver_name']
        read_only_fields = ['id', 'created_at']


class SendMessageSerializer(serializers.ModelSerializer):
    """发送消息序列化器"""
    receiver_id = serializers.UUIDField(write_only=True)

    class Meta:
        model = ChatMessage
        fields = ['receiver_id', 'content']

    def create(self, validated_data):
        # 正确处理 receiver_id
        receiver_id = validated_data.pop('receiver_id')
        sender = self.context['request'].user
        
        try:
            receiver = User.objects.get(id=receiver_id)
        except User.DoesNotExist:
            raise serializers.ValidationError("接收者不存在")
        
        # 验证是否可以聊天（不同角色）
        if sender.role == receiver.role:
            raise serializers.ValidationError("只能与不同角色的用户聊天")
        
        return ChatMessage.objects.create(
            sender=sender,
            receiver=receiver,
            content=validated_data['content']
        )



