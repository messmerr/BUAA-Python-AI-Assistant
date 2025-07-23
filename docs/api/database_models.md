# AI助教系统数据库模型设计

本文档定义了AI助教系统的数据库模型设计，基于Django ORM实现。

## 一、用户认证系统

### 1. User 模型
```python
class User(AbstractUser):
    """用户模型，继承Django内置的AbstractUser"""
    USER_ROLE_CHOICES = (
        ('teacher', '教师'),
        ('student', '学生'),
    )
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    role = models.CharField(max_length=10, choices=USER_ROLE_CHOICES, default='student')
    real_name = models.CharField(max_length=50, blank=True)
    student_id = models.CharField(max_length=20, blank=True, null=True)
    avatar = models.ImageField(upload_to='avatars/', blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'users'
        verbose_name = '用户'
        verbose_name_plural = '用户'
```

### 2. UserProfile 模型
```python
class UserProfile(models.Model):
    """用户个人资料扩展"""
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    bio = models.TextField(blank=True)
    phone = models.CharField(max_length=20, blank=True)
    address = models.CharField(max_length=200, blank=True)
    birth_date = models.DateField(null=True, blank=True)
    
    class Meta:
        db_table = 'user_profiles'
        verbose_name = '用户资料'
        verbose_name_plural = '用户资料'
```

## 二、作业批改功能

### 1. Assignment 模型
```python
class Assignment(models.Model):
    """作业模型"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    title = models.CharField(max_length=100)
    description = models.TextField()
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='created_assignments')
    deadline = models.DateTimeField()
    total_score = models.IntegerField(default=100)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'assignments'
        verbose_name = '作业'
        verbose_name_plural = '作业'
        ordering = ['-created_at']
```

### 2. Question 模型
```python
class Question(models.Model):
    """作业问题模型"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    assignment = models.ForeignKey(Assignment, on_delete=models.CASCADE, related_name='questions')
    question_text = models.TextField()
    reference_answer = models.TextField()
    score = models.IntegerField()
    order = models.IntegerField(default=0)

    class Meta:
        db_table = 'questions'
        verbose_name = '问题'
        verbose_name_plural = '问题'
        ordering = ['order']
```

### 3. Submission 模型
```python
class Submission(models.Model):
    """作业提交模型"""
    STATUS_CHOICES = (
        ('submitted', '已提交'),
        ('grading', '批改中'),
        ('graded', '已批改'),
    )
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    assignment = models.ForeignKey(Assignment, on_delete=models.CASCADE, related_name='submissions')
    student = models.ForeignKey(User, on_delete=models.CASCADE, related_name='submissions')
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='submitted')
    auto_score = models.IntegerField(default=0)
    final_score = models.IntegerField(null=True, blank=True)
    overall_feedback = models.TextField(blank=True)
    submitted_at = models.DateTimeField(auto_now_add=True)
    graded_at = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        db_table = 'submissions'
        verbose_name = '作业提交'
        verbose_name_plural = '作业提交'
        ordering = ['-submitted_at']
        unique_together = ['assignment', 'student']
```

### 4. Answer 模型
```python
class Answer(models.Model):
    """学生答案模型"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    submission = models.ForeignKey(Submission, on_delete=models.CASCADE, related_name='answers')
    question = models.ForeignKey(Question, on_delete=models.CASCADE, related_name='answers')
    answer_text = models.TextField()
    score = models.IntegerField(null=True, blank=True)
    ai_feedback = models.TextField(blank=True)  # AI生成的反馈

    class Meta:
        db_table = 'answers'
        verbose_name = '答案'
        verbose_name_plural = '答案'
        unique_together = ['submission', 'question']
```

### 5. ImageSubmission 模型 (选做功能)
```python
class ImageSubmission(models.Model):
    """图片作业提交模型"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    submission = models.OneToOneField(Submission, on_delete=models.CASCADE, related_name='image_submission')
    image = models.ImageField(upload_to='assignments/images/')
    extracted_text = models.TextField(blank=True)  # AI OCR提取的文本
    processed_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        db_table = 'image_submissions'
        verbose_name = '图片作业'
        verbose_name_plural = '图片作业'
```

## 三、智能答疑功能

### 1. Question 模型 (QA系统)
```python
class QAQuestion(models.Model):
    """学生提问模型"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    student = models.ForeignKey(User, on_delete=models.CASCADE, related_name='qa_questions')
    question_text = models.TextField()
    subject = models.CharField(max_length=50, blank=True)
    context = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'qa_questions'
        verbose_name = '问题'
        verbose_name_plural = '问题'
        ordering = ['-created_at']
```

### 2. Answer 模型 (QA系统)
```python
class QAAnswer(models.Model):
    """问题回答模型"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    question = models.OneToOneField(QAQuestion, on_delete=models.CASCADE, related_name='answer')
    ai_answer = models.TextField()  # AI生成的回答
    explanation = models.TextField(blank=True)  # 详细解释
    examples = models.JSONField(default=list)  # 相关例子
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'qa_answers'
        verbose_name = '回答'
        verbose_name_plural = '回答'
```

## 四、学习报告功能

### 1. LearningReport 模型
```python
class LearningReport(models.Model):
    """学习报告模型"""
    PERIOD_CHOICES = (
        ('week', '周报'),
        ('month', '月报'),
        ('semester', '学期报告'),
    )
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    student = models.ForeignKey(User, on_delete=models.CASCADE, related_name='learning_reports')
    period = models.CharField(max_length=10, choices=PERIOD_CHOICES)
    start_date = models.DateField()
    end_date = models.DateField()
    summary = models.JSONField()  # 存储总体统计数据
    generated_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'learning_reports'
        verbose_name = '学习报告'
        verbose_name_plural = '学习报告'
        ordering = ['-generated_at']
```

### 2. SubjectPerformance 模型
```python
class SubjectPerformance(models.Model):
    """学科表现模型"""
    TREND_CHOICES = (
        ('up', '上升'),
        ('down', '下降'),
        ('stable', '稳定'),
    )
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    report = models.ForeignKey(LearningReport, on_delete=models.CASCADE, related_name='subject_performances')
    subject = models.CharField(max_length=50)
    assignment_count = models.IntegerField(default=0)
    average_score = models.FloatField(default=0.0)
    improvement_trend = models.CharField(max_length=10, choices=TREND_CHOICES, default='stable')
    
    class Meta:
        db_table = 'subject_performances'
        verbose_name = '学科表现'
        verbose_name_plural = '学科表现'
```

### 3. KnowledgePoint 模型
```python
class KnowledgePoint(models.Model):
    """知识点掌握情况模型"""
    MASTERY_LEVEL_CHOICES = (
        ('excellent', '优秀'),
        ('good', '良好'),
        ('fair', '一般'),
        ('poor', '较差'),
    )
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    report = models.ForeignKey(LearningReport, on_delete=models.CASCADE, related_name='knowledge_points')
    topic = models.CharField(max_length=100)
    mastery_level = models.CharField(max_length=10, choices=MASTERY_LEVEL_CHOICES)
    practice_count = models.IntegerField(default=0)
    
    class Meta:
        db_table = 'knowledge_points'
        verbose_name = '知识点掌握'
        verbose_name_plural = '知识点掌握'

## 五、选做功能模型

### 1. LearningResource 模型 (资源推荐)
```python
class LearningResource(models.Model):
    """学习资源模型"""
    RESOURCE_TYPE_CHOICES = (
        ('video', '视频'),
        ('article', '文章'),
        ('exercise', '练习'),
        ('book', '书籍'),
    )

    DIFFICULTY_CHOICES = (
        ('easy', '简单'),
        ('medium', '中等'),
        ('hard', '困难'),
    )

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    title = models.CharField(max_length=200)
    description = models.TextField()
    resource_type = models.CharField(max_length=10, choices=RESOURCE_TYPE_CHOICES)
    url = models.URLField()
    difficulty = models.CharField(max_length=10, choices=DIFFICULTY_CHOICES)
    subject = models.CharField(max_length=50)
    rating = models.FloatField(default=0.0)
    estimated_time = models.IntegerField(help_text='预计学习时间（分钟）')
    tags = models.JSONField(default=list)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'learning_resources'
        verbose_name = '学习资源'
        verbose_name_plural = '学习资源'
```

### 2. ResourceRecommendation 模型
```python
class ResourceRecommendation(models.Model):
    """资源推荐记录模型"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    student = models.ForeignKey(User, on_delete=models.CASCADE, related_name='recommendations')
    resource = models.ForeignKey(LearningResource, on_delete=models.CASCADE, related_name='recommendations')
    reason = models.TextField()
    recommended_at = models.DateTimeField(auto_now_add=True)
    clicked = models.BooleanField(default=False)
    clicked_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        db_table = 'resource_recommendations'
        verbose_name = '资源推荐'
        verbose_name_plural = '资源推荐'
        unique_together = ['student', 'resource']
```

### 3. FavoriteResource 模型
```python
class FavoriteResource(models.Model):
    """收藏资源模型"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    student = models.ForeignKey(User, on_delete=models.CASCADE, related_name='favorite_resources')
    resource = models.ForeignKey(LearningResource, on_delete=models.CASCADE, related_name='favorited_by')
    favorited_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'favorite_resources'
        verbose_name = '收藏资源'
        verbose_name_plural = '收藏资源'
        unique_together = ['student', 'resource']
```

### 4. ChatMessage 模型 (实时互动)
```python
class ChatMessage(models.Model):
    """聊天消息模型"""
    MESSAGE_TYPE_CHOICES = (
        ('text', '文本'),
        ('image', '图片'),
        ('file', '文件'),
    )

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    sender = models.ForeignKey(User, on_delete=models.CASCADE, related_name='sent_messages')
    recipient = models.ForeignKey(User, on_delete=models.CASCADE, related_name='received_messages')
    message_text = models.TextField()
    message_type = models.CharField(max_length=10, choices=MESSAGE_TYPE_CHOICES, default='text')
    attachment_url = models.URLField(blank=True)
    sent_at = models.DateTimeField(auto_now_add=True)
    read_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        db_table = 'chat_messages'
        verbose_name = '聊天消息'
        verbose_name_plural = '聊天消息'
        ordering = ['-sent_at']
```

### 5. ClassAnalytics 模型 (数据分析)
```python
class ClassAnalytics(models.Model):
    """班级分析数据模型"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    teacher = models.ForeignKey(User, on_delete=models.CASCADE, related_name='class_analytics')
    class_name = models.CharField(max_length=100)
    student_count = models.IntegerField()
    period_start = models.DateField()
    period_end = models.DateField()
    analytics_data = models.JSONField()  # 存储分析结果
    generated_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'class_analytics'
        verbose_name = '班级分析'
        verbose_name_plural = '班级分析'
        ordering = ['-generated_at']
```

## 六、通用模型

### 1. File 模型
```python
class File(models.Model):
    """文件模型"""
    FILE_TYPE_CHOICES = (
        ('avatar', '头像'),
        ('assignment', '作业文件'),
        ('attachment', '附件'),
    )

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    file_name = models.CharField(max_length=255)
    file_path = models.FileField(upload_to='uploads/')
    file_size = models.BigIntegerField()
    file_type = models.CharField(max_length=20, choices=FILE_TYPE_CHOICES)
    mime_type = models.CharField(max_length=100)
    uploaded_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='uploaded_files')
    uploaded_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'files'
        verbose_name = '文件'
        verbose_name_plural = '文件'
```

### 2. SystemConfig 模型
```python
class SystemConfig(models.Model):
    """系统配置模型"""
    key = models.CharField(max_length=100, unique=True)
    value = models.TextField()
    description = models.CharField(max_length=255, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'system_configs'
        verbose_name = '系统配置'
        verbose_name_plural = '系统配置'
```

### 3. AuditLog 模型
```python
class AuditLog(models.Model):
    """审计日志模型"""
    ACTION_CHOICES = (
        ('create', '创建'),
        ('update', '更新'),
        ('delete', '删除'),
        ('login', '登录'),
        ('logout', '登出'),
    )

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='audit_logs')
    action = models.CharField(max_length=20, choices=ACTION_CHOICES)
    resource_type = models.CharField(max_length=50)
    resource_id = models.CharField(max_length=100, blank=True)
    details = models.JSONField(default=dict)
    ip_address = models.GenericIPAddressField()
    user_agent = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'audit_logs'
        verbose_name = '审计日志'
        verbose_name_plural = '审计日志'
        ordering = ['-created_at']
```

## 七、数据库关系图

```
User (用户)
├── UserProfile (用户资料) [1:1]
├── Assignment (创建的作业) [1:N]
├── Submission (作业提交) [1:N]
├── QAQuestion (提问) [1:N]
├── LearningReport (学习报告) [1:N]
├── ChatMessage (发送的消息) [1:N]
├── ChatMessage (接收的消息) [1:N]
├── FavoriteResource (收藏资源) [1:N]
└── File (上传文件) [1:N]

Assignment (作业)
├── Question (问题) [1:N]
└── Submission (提交) [1:N]

Submission (作业提交)
├── Answer (答案) [1:N]
└── ImageSubmission (图片提交) [1:1]

QAQuestion (问题)
├── QAAnswer (回答) [1:1]
├── RelatedTopic (相关知识点) [1:N]
└── WebSearchResult (搜索结果) [1:N]

LearningReport (学习报告)
├── SubjectPerformance (学科表现) [1:N]
└── KnowledgePoint (知识点掌握) [1:N]

LearningResource (学习资源)
├── ResourceRecommendation (推荐记录) [1:N]
└── FavoriteResource (收藏记录) [1:N]
```

## 八、索引建议

为了提高查询性能，建议在以下字段上创建索引：

```python
# 在models.py中添加索引
class Meta:
    indexes = [
        models.Index(fields=['created_at']),
        models.Index(fields=['student', 'created_at']),
        models.Index(fields=['assignment', 'student']),
        models.Index(fields=['role']),
        models.Index(fields=['deadline']),
    ]
```

## 九、数据迁移注意事项

1. **初始数据**: 创建超级用户和默认系统配置
2. **权限设置**: 为不同角色设置适当的权限
3. **测试数据**: 创建测试用户、作业和问题数据
4. **文件存储**: 配置文件上传路径和权限
5. **数据备份**: 定期备份重要数据
```
