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
    """用户信息更新序列化器"""
    current_password = serializers.CharField(write_only=True, required=False)
    new_password = serializers.CharField(write_only=True, required=False, validators=[validate_password])
    confirm_password = serializers.CharField(write_only=True, required=False)

    class Meta:
        model = User
        fields = ['email', 'real_name', 'current_password', 'new_password', 'confirm_password']

    def validate(self, attrs):
        """验证更新数据"""
        new_password = attrs.get('new_password')
        confirm_password = attrs.get('confirm_password')
        current_password = attrs.get('current_password')

        # 如果要修改密码，需要验证当前密码和确认密码
        if new_password:
            if not current_password:
                raise serializers.ValidationError("修改密码时必须提供当前密码")

            if not self.instance.check_password(current_password):
                raise serializers.ValidationError("当前密码错误")

            if new_password != confirm_password:
                raise serializers.ValidationError("新密码和确认密码不匹配")

        return attrs

    def update(self, instance, validated_data):
        """更新用户信息"""
        # 移除密码相关字段，单独处理
        new_password = validated_data.pop('new_password', None)
        validated_data.pop('current_password', None)
        validated_data.pop('confirm_password', None)

        # 更新基本信息
        for attr, value in validated_data.items():
            setattr(instance, attr, value)

        # 更新密码
        if new_password:
            instance.set_password(new_password)

        instance.save()
        return instance
