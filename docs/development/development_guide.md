# AI助教系统开发指南

## 项目概述

本项目是一个基于Django + Vue.js的AI助教系统，旨在辅助教师进行作业批改、答疑，同时帮助学生进行学习。

### 技术栈
- **后端**: Django 4.x + Django REST Framework
- **前端**: Vue 3 + TypeScript + Vite
- **数据库**: SQLite (开发) / PostgreSQL (生产)
- **认证**: JWT Token
- **文件存储**: 本地存储 / 云存储
- **实时通信**: WebSocket (Django Channels)

## 项目结构

```
BUAA-Python-AI-Assistant/
├── backend/                    # Django后端
│   ├── ai_tutor_system/       # 主项目配置
│   ├── apps/                  # 应用模块
│   │   ├── authentication/    # 用户认证
│   │   ├── assignments/       # 作业管理
│   │   ├── qa/               # 智能答疑
│   │   ├── reports/          # 学习报告
│   │   ├── analytics/        # 数据分析
│   │   ├── chat/             # 实时聊天
│   │   └── common/           # 通用功能
│   ├── requirements.txt       # Python依赖
│   └── manage.py
├── frontend/                  # Vue前端
│   ├── src/
│   │   ├── components/       # 组件
│   │   ├── views/           # 页面
│   │   ├── stores/          # Pinia状态管理
│   │   ├── router/          # 路由配置
│   │   ├── api/             # API接口
│   │   └── utils/           # 工具函数
│   ├── package.json
│   └── vite.config.ts
└── docs/                     # 文档
    ├── api/                 # API文档
    ├── development/         # 开发文档
    └── deployment/          # 部署文档
```

## 开发环境搭建

### 后端环境

1. **创建虚拟环境**
```bash
cd backend
python -m venv venv
# Windows
venv\Scripts\activate
# Linux/Mac
source venv/bin/activate
```

2. **安装依赖**
```bash
pip install -r requirements.txt
```

3. **数据库迁移**
```bash
python manage.py makemigrations
python manage.py migrate
```

4. **创建超级用户**
```bash
python manage.py createsuperuser
```

5. **启动开发服务器**
```bash
python manage.py runserver
```

### 前端环境

1. **安装依赖**
```bash
cd frontend
npm install
```

2. **启动开发服务器**
```bash
npm run dev
```

## 开发规范

### 代码规范

#### Python (后端)
- 遵循 PEP 8 代码规范
- 使用 Black 进行代码格式化
- 使用 flake8 进行代码检查
- 函数和类需要添加文档字符串

```python
def create_assignment(title: str, description: str, deadline: datetime) -> Assignment:
    """
    创建新作业
    
    Args:
        title: 作业标题
        description: 作业描述
        deadline: 截止时间
        
    Returns:
        Assignment: 创建的作业对象
        
    Raises:
        ValidationError: 当参数验证失败时
    """
    pass
```

#### TypeScript (前端)
- 使用 ESLint + Prettier 进行代码格式化
- 严格的 TypeScript 类型检查
- 组件使用 Composition API
- 使用 Pinia 进行状态管理

```typescript
interface Assignment {
  id: string
  title: string
  description: string
  deadline: string
  totalScore: number
}

const useAssignmentStore = defineStore('assignment', () => {
  const assignments = ref<Assignment[]>([])
  
  const fetchAssignments = async (): Promise<void> => {
    // 实现逻辑
  }
  
  return { assignments, fetchAssignments }
})
```

### Git 工作流

1. **分支命名规范**
   - `feature/功能名称`: 新功能开发
   - `bugfix/问题描述`: 问题修复
   - `hotfix/紧急修复`: 紧急修复
   - `docs/文档更新`: 文档更新

2. **提交信息规范**
```
type(scope): description

feat(auth): 添加用户注册功能
fix(assignment): 修复作业提交bug
docs(api): 更新API文档
style(frontend): 调整页面样式
refactor(backend): 重构数据库查询逻辑
test(qa): 添加答疑功能测试
```

3. **开发流程**
```bash
# 1. 创建功能分支
git checkout -b feature/assignment-grading

# 2. 开发并提交
git add .
git commit -m "feat(assignment): 实现自动批改功能"

# 3. 推送分支
git push origin feature/assignment-grading

# 4. 创建Pull Request
# 5. 代码审查
# 6. 合并到主分支
```

## API开发指南

### 1. 创建新的API应用

```bash
cd backend
python manage.py startapp new_app
```

### 2. 定义模型

```python
# apps/new_app/models.py
from django.db import models
import uuid

class ExampleModel(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=100)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'example_models'
        verbose_name = '示例模型'
        verbose_name_plural = '示例模型'
```

### 3. 创建序列化器

```python
# apps/new_app/serializers.py
from rest_framework import serializers
from .models import ExampleModel

class ExampleModelSerializer(serializers.ModelSerializer):
    class Meta:
        model = ExampleModel
        fields = '__all__'
        read_only_fields = ('id', 'created_at')
```

### 4. 实现视图

```python
# apps/new_app/views.py
from rest_framework import viewsets, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from .models import ExampleModel
from .serializers import ExampleModelSerializer

class ExampleModelViewSet(viewsets.ModelViewSet):
    queryset = ExampleModel.objects.all()
    serializer_class = ExampleModelSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    @action(detail=True, methods=['post'])
    def custom_action(self, request, pk=None):
        """自定义动作"""
        instance = self.get_object()
        # 实现自定义逻辑
        return Response({'status': 'success'})
```

### 5. 配置URL

```python
# apps/new_app/urls.py
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import ExampleModelViewSet

router = DefaultRouter()
router.register(r'examples', ExampleModelViewSet)

urlpatterns = [
    path('api/v1/', include(router.urls)),
]
```

## 前端开发指南

### 1. 创建新页面

```vue
<!-- src/views/ExampleView.vue -->
<template>
  <div class="example-view">
    <h1>{{ title }}</h1>
    <ExampleComponent :data="data" @update="handleUpdate" />
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import ExampleComponent from '@/components/ExampleComponent.vue'
import { useExampleStore } from '@/stores/example'

const title = ref('示例页面')
const exampleStore = useExampleStore()

const data = computed(() => exampleStore.data)

const handleUpdate = (newData: any) => {
  exampleStore.updateData(newData)
}

onMounted(() => {
  exampleStore.fetchData()
})
</script>

<style scoped>
.example-view {
  padding: 20px;
}
</style>
```

### 2. API服务封装

```typescript
// src/api/example.ts
import { apiClient } from './client'

export interface ExampleData {
  id: string
  name: string
  createdAt: string
}

export const exampleApi = {
  getList: (): Promise<ExampleData[]> => {
    return apiClient.get('/examples/')
  },
  
  getById: (id: string): Promise<ExampleData> => {
    return apiClient.get(`/examples/${id}/`)
  },
  
  create: (data: Partial<ExampleData>): Promise<ExampleData> => {
    return apiClient.post('/examples/', data)
  },
  
  update: (id: string, data: Partial<ExampleData>): Promise<ExampleData> => {
    return apiClient.put(`/examples/${id}/`, data)
  },
  
  delete: (id: string): Promise<void> => {
    return apiClient.delete(`/examples/${id}/`)
  }
}
```

### 3. 状态管理

```typescript
// src/stores/example.ts
import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { exampleApi, type ExampleData } from '@/api/example'

export const useExampleStore = defineStore('example', () => {
  const items = ref<ExampleData[]>([])
  const loading = ref(false)
  const error = ref<string | null>(null)
  
  const itemCount = computed(() => items.value.length)
  
  const fetchData = async () => {
    loading.value = true
    error.value = null
    try {
      items.value = await exampleApi.getList()
    } catch (err) {
      error.value = '获取数据失败'
      console.error(err)
    } finally {
      loading.value = false
    }
  }
  
  const addItem = async (data: Partial<ExampleData>) => {
    try {
      const newItem = await exampleApi.create(data)
      items.value.push(newItem)
    } catch (err) {
      error.value = '创建失败'
      throw err
    }
  }
  
  return {
    items,
    loading,
    error,
    itemCount,
    fetchData,
    addItem
  }
})
```

## 测试指南

### 后端测试

```python
# apps/new_app/tests.py
from django.test import TestCase
from django.contrib.auth import get_user_model
from rest_framework.test import APITestCase
from rest_framework import status
from .models import ExampleModel

User = get_user_model()

class ExampleModelTestCase(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123'
        )
        self.client.force_authenticate(user=self.user)
    
    def test_create_example(self):
        data = {'name': 'Test Example'}
        response = self.client.post('/api/v1/examples/', data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(ExampleModel.objects.count(), 1)
```

### 前端测试

```typescript
// src/components/__tests__/ExampleComponent.spec.ts
import { describe, it, expect } from 'vitest'
import { mount } from '@vue/test-utils'
import ExampleComponent from '../ExampleComponent.vue'

describe('ExampleComponent', () => {
  it('renders properly', () => {
    const wrapper = mount(ExampleComponent, {
      props: { data: { id: '1', name: 'Test' } }
    })
    expect(wrapper.text()).toContain('Test')
  })
  
  it('emits update event', async () => {
    const wrapper = mount(ExampleComponent)
    await wrapper.find('button').trigger('click')
    expect(wrapper.emitted()).toHaveProperty('update')
  })
})
```

## 部署指南

### 开发环境
- 后端: `python manage.py runserver`
- 前端: `npm run dev`

### 生产环境
- 使用 Docker 容器化部署
- 配置 Nginx 反向代理
- 使用 PostgreSQL 数据库
- 配置 Redis 缓存

## 常见问题

### 1. CORS 问题
在 Django settings.py 中配置 CORS：
```python
CORS_ALLOWED_ORIGINS = [
    "http://localhost:5173",  # Vue开发服务器
]
```

### 2. 静态文件处理
```python
# settings.py
STATIC_URL = '/static/'
MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')
```

### 3. 环境变量配置
使用 python-decouple 管理环境变量：
```python
from decouple import config

SECRET_KEY = config('SECRET_KEY')
DEBUG = config('DEBUG', default=False, cast=bool)
```
