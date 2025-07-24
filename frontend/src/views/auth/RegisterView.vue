<template>
  <div class="register-container">
    <div class="register-form">
      <h2>注册</h2>
      
      <el-form 
        ref="formRef" 
        :model="registerForm" 
        :rules="rules"
        @submit.prevent="handleRegister"
      >
        <el-form-item prop="username">
          <el-input
            v-model="registerForm.username"
            placeholder="用户名"
            size="large"
          />
        </el-form-item>
        
        <el-form-item prop="password">
          <el-input
            v-model="registerForm.password"
            type="password"
            placeholder="密码"
            size="large"
          />
        </el-form-item>
        
        <el-form-item prop="email">
          <el-input
            v-model="registerForm.email"
            placeholder="邮箱"
            size="large"
          />
        </el-form-item>
        
        <el-form-item prop="role">
          <el-select 
            v-model="registerForm.role" 
            placeholder="选择角色"
            size="large"
            style="width: 100%"
          >
            <el-option label="学生" value="student" />
            <el-option label="教师" value="teacher" />
          </el-select>
        </el-form-item>
        
        <el-form-item prop="real_name">
          <el-input
            v-model="registerForm.real_name"
            placeholder="真实姓名"
            size="large"
          />
        </el-form-item>
        
        <el-form-item v-if="registerForm.role === 'student'" prop="student_id">
          <el-input
            v-model="registerForm.student_id"
            placeholder="学号"
            size="large"
          />
        </el-form-item>
        
        <el-form-item>
          <el-button 
            type="primary" 
            size="large" 
            style="width: 100%"
            :loading="authStore.loading"
            @click="handleRegister"
          >
            注册
          </el-button>
        </el-form-item>
      </el-form>
      
      <div class="register-footer">
        <router-link to="/login">已有账号？去登录</router-link>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores'
import type { FormInstance, FormRules } from 'element-plus'

const router = useRouter()
const authStore = useAuthStore()

// 表单引用
const formRef = ref<FormInstance>()

// 表单数据
const registerForm = reactive({
  username: '',
  password: '',
  email: '',
  role: 'student' as 'teacher' | 'student',
  real_name: '',
  student_id: ''
})

// 表单验证规则
const rules: FormRules = {
  username: [
    { required: true, message: '请输入用户名', trigger: 'blur' }
  ],
  password: [
    { required: true, message: '请输入密码', trigger: 'blur' },
    { min: 6, message: '密码长度至少6位', trigger: 'blur' }
  ],
  email: [
    { required: true, message: '请输入邮箱', trigger: 'blur' },
    { type: 'email', message: '请输入正确的邮箱格式', trigger: 'blur' }
  ],
  role: [
    { required: true, message: '请选择角色', trigger: 'change' }
  ],
  real_name: [
    { required: true, message: '请输入真实姓名', trigger: 'blur' }
  ],
  student_id: [
    {
      validator: (_rule: any, value: string, callback: Function) => {
        if (registerForm.role === 'student' && !value) {
          callback(new Error('学生必须输入学号'))
        } else {
          callback()
        }
      },
      trigger: 'blur'
    }
  ]
}

// 处理注册
const handleRegister = async () => {
  if (!formRef.value) return

  const valid = await formRef.value.validate().catch(() => false)
  if (!valid) return

  // 准备注册数据，如果不是学生则不包含student_id
  const registrationData = {
    username: registerForm.username,
    password: registerForm.password,
    email: registerForm.email,
    role: registerForm.role,
    real_name: registerForm.real_name,
    ...(registerForm.role === 'student' && { student_id: registerForm.student_id })
  }

  console.log('注册数据:', registrationData)

  try {
    const success = await authStore.register(registrationData)
    if (success) {
      router.push('/login')
    }
  } catch (error) {
    console.error('注册错误:', error)
  }
}
</script>

<style scoped>
.register-container {
  display: flex;
  justify-content: center;
  align-items: center;
  min-height: 100vh;
  background: #f5f5f5;
}

.register-form {
  width: 400px;
  padding: 40px;
  background: white;
  border-radius: 8px;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.1);
}

.register-form h2 {
  text-align: center;
  margin-bottom: 30px;
  color: #303133;
}

.register-footer {
  text-align: center;
  margin-top: 20px;
}

.register-footer a {
  color: #409eff;
  text-decoration: none;
}

.register-footer a:hover {
  text-decoration: underline;
}
</style>
