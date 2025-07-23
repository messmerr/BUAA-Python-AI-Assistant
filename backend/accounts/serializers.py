from rest_framework import serializers
from django.contrib.auth import authenticate
from django.contrib.auth.password_validation import validate_password
from .models import User


class UserSerializer(serializers.ModelSerializer):
    """用户序列化器 - 严格按照API规范"""
    password = serializers.CharField(write_only=True, validators=[validate_password])

    class Meta:
        model = User
        fields = [
            'id', 'username', 'email', 'role', 'real_name',
            'student_id', 'created_at', 'password'
        ]
        extra_kwargs = {
            'password': {'write_only': True},
            'created_at': {'read_only': True},
        }

    def create(self, validated_data):
        """创建用户"""
        password = validated_data.pop('password')
        user = User.objects.create_user(**validated_data)
        user.set_password(password)
        user.save()
        return user


class UserRegistrationSerializer(serializers.ModelSerializer):
    """用户注册序列化器 - 严格按照API规范"""
    password = serializers.CharField(write_only=True, validators=[validate_password])

    class Meta:
        model = User
        fields = [
            'username', 'password', 'email',
            'role', 'real_name', 'student_id'
        ]

    def validate(self, attrs):
        """验证注册数据"""
        # 学生必须提供学号
        if attrs['role'] == 'student' and not attrs.get('student_id'):
            raise serializers.ValidationError("学生必须提供学号")

        return attrs

    def create(self, validated_data):
        """创建用户"""
        password = validated_data.pop('password')
        user = User.objects.create_user(**validated_data)
        user.set_password(password)
        user.save()
        return user


class UserLoginSerializer(serializers.Serializer):
    """用户登录序列化器"""
    username = serializers.CharField()
    password = serializers.CharField(write_only=True)
    
    def validate(self, attrs):
        """验证登录信息"""
        username = attrs.get('username')
        password = attrs.get('password')
        
        if username and password:
            user = authenticate(username=username, password=password)
            if not user:
                raise serializers.ValidationError("用户名或密码错误")
            if not user.is_active:
                raise serializers.ValidationError("用户账户已被禁用")
            attrs['user'] = user
        else:
            raise serializers.ValidationError("必须提供用户名和密码")
            
        return attrs


class UserUpdateSerializer(serializers.ModelSerializer):
    """用户信息更新序列化器 - 严格按照API规范"""

    class Meta:
        model = User
        fields = ['email', 'real_name']  # API规范中只允许更新这两个字段

    def update(self, instance, validated_data):
        """更新用户信息"""
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        return instance
