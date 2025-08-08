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
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  position: relative;
  overflow: hidden;
  padding: 20px 0;
}

.register-container::before {
  content: '';
  position: absolute;
  top: -50%;
  left: -50%;
  width: 200%;
  height: 200%;
  background: url('data:image/svg+xml,<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 100 100"><defs><pattern id="grid" width="10" height="10" patternUnits="userSpaceOnUse"><path d="M 10 0 L 0 0 0 10" fill="none" stroke="rgba(255,255,255,0.05)" stroke-width="0.5"/></pattern></defs><rect width="100" height="100" fill="url(%23grid)"/></svg>');
  animation: float 20s ease-in-out infinite;
}

@keyframes float {
  0%, 100% { transform: translate(0, 0) rotate(0deg); }
  33% { transform: translate(1%, -1%) rotate(0.5deg); }
  66% { transform: translate(-1%, 1%) rotate(-0.5deg); }
}

.register-form {
  width: 440px;
  max-width: 90%;
  padding: 48px;
  background: rgba(255, 255, 255, 0.95);
  backdrop-filter: blur(10px);
  border-radius: 16px;
  box-shadow: 
    0 8px 32px rgba(0, 0, 0, 0.1),
    0 2px 8px rgba(0, 0, 0, 0.05),
    inset 0 1px 0 rgba(255, 255, 255, 0.8);
  border: 1px solid rgba(255, 255, 255, 0.2);
  position: relative;
  z-index: 1;
  animation: slideUp 0.6s ease-out;
  transform-style: preserve-3d;
}

@keyframes slideUp {
  from {
    opacity: 0;
    transform: translateY(30px) scale(0.95);
  }
  to {
    opacity: 1;
    transform: translateY(0) scale(1);
  }
}

.register-form::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  height: 4px;
  background: linear-gradient(90deg, #409eff, #67c23a, #e6a23c, #f56c6c);
  border-radius: 16px 16px 0 0;
}

.register-form h2 {
  text-align: center;
  margin-bottom: 36px;
  color: #303133;
  font-size: 28px;
  font-weight: 600;
  position: relative;
}

.register-form h2::after {
  content: '';
  position: absolute;
  bottom: -12px;
  left: 50%;
  transform: translateX(-50%);
  width: 60px;
  height: 3px;
  background: linear-gradient(90deg, #409eff, #67c23a);
  border-radius: 2px;
}

.register-form :deep(.el-form-item) {
  margin-bottom: 20px;
}

.register-form :deep(.el-input) {
  border-radius: 12px;
  overflow: hidden;
}

.register-form :deep(.el-input__wrapper) {
  border-radius: 12px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.08);
  border: 1px solid #e4e7ed;
  transition: all 0.3s ease;
}

.register-form :deep(.el-input__wrapper:hover) {
  border-color: #409eff;
  box-shadow: 0 4px 12px rgba(64, 158, 255, 0.15);
}

.register-form :deep(.el-input__wrapper.is-focus) {
  border-color: #409eff;
  box-shadow: 0 4px 12px rgba(64, 158, 255, 0.2);
  transform: translateY(-1px);
}

.register-form :deep(.el-input__inner) {
  padding: 14px 18px;
  font-size: 15px;
}

.register-form :deep(.el-select) {
  width: 100%;
}

.register-form :deep(.el-select .el-input__wrapper) {
  border-radius: 12px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.08);
  border: 1px solid #e4e7ed;
  transition: all 0.3s ease;
}

.register-form :deep(.el-select .el-input__wrapper:hover) {
  border-color: #409eff;
  box-shadow: 0 4px 12px rgba(64, 158, 255, 0.15);
}

.register-form :deep(.el-select.is-focus .el-input__wrapper) {
  border-color: #409eff;
  box-shadow: 0 4px 12px rgba(64, 158, 255, 0.2);
  transform: translateY(-1px);
}

.register-form :deep(.el-button--primary) {
  border-radius: 12px;
  font-size: 16px;
  font-weight: 500;
  padding: 16px 0;
  background: linear-gradient(135deg, #409eff, #5a67d8);
  border: none;
  box-shadow: 0 4px 16px rgba(64, 158, 255, 0.3);
  transition: all 0.3s ease;
  position: relative;
  overflow: hidden;
}

.register-form :deep(.el-button--primary::before) {
  content: '';
  position: absolute;
  top: 0;
  left: -100%;
  width: 100%;
  height: 100%;
  background: linear-gradient(90deg, transparent, rgba(255, 255, 255, 0.2), transparent);
  transition: left 0.6s;
}

.register-form :deep(.el-button--primary:hover) {
  transform: translateY(-2px);
  box-shadow: 0 8px 24px rgba(64, 158, 255, 0.4);
}

.register-form :deep(.el-button--primary:hover::before) {
  left: 100%;
}

.register-form :deep(.el-button--primary:active) {
  transform: translateY(0);
}

.register-footer {
  text-align: center;
  margin-top: 24px;
  padding-top: 24px;
  border-top: 1px solid rgba(228, 231, 237, 0.6);
}

.register-footer a {
  color: #409eff;
  text-decoration: none;
  font-size: 14px;
  font-weight: 500;
  padding: 8px 16px;
  border-radius: 8px;
  transition: all 0.3s ease;
  display: inline-block;
}

.register-footer a:hover {
  background: rgba(64, 158, 255, 0.1);
  transform: translateY(-1px);
  text-decoration: none;
}

/* 响应式设计 */
@media (max-width: 480px) {
  .register-form {
    width: 90%;
    padding: 32px 24px;
    margin: 20px;
  }
  
  .register-form h2 {
    font-size: 24px;
  }
}
</style>
