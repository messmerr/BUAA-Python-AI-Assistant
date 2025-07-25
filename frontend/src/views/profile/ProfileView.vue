<template>
  <div class="profile-container">
    <!-- 页面头部 -->
    <div class="page-header">
      <div class="header-info">
        <h1>个人中心</h1>
        <p>管理您的个人信息和账户设置</p>
      </div>
    </div>

    <div v-if="profileStore.loading" class="loading-container">
      <el-icon class="is-loading"><Loading /></el-icon>
      <span>加载中...</span>
    </div>

    <div v-else-if="!profileStore.profile" class="error-container">
      <el-result
        icon="warning"
        title="无法获取个人信息"
        sub-title="请刷新页面重试"
      >
        <template #extra>
          <el-button type="primary" @click="fetchProfile">重新加载</el-button>
        </template>
      </el-result>
    </div>

    <div v-else class="profile-content">
      <!-- 个人信息卡片 -->
      <el-card class="profile-info-card">
        <template #header>
          <div class="card-header">
            <span>基本信息</span>
            <el-button
              type="primary"
              text
              @click="openEditDialog"
              :disabled="profileStore.updating"
            >
              <el-icon><Edit /></el-icon>
              编辑信息
            </el-button>
          </div>
        </template>

        <div class="profile-info">
          <div class="avatar-section">
            <el-avatar :size="80" class="user-avatar">
              <el-icon><User /></el-icon>
            </el-avatar>
            <div class="user-basic">
              <h2>{{ profileStore.profile.real_name }}</h2>
              <el-tag :type="getRoleType(profileStore.profile.role)" size="large">
                {{ profileStore.roleDisplay }}
              </el-tag>
            </div>
          </div>

          <div class="info-grid">
            <div class="info-item">
              <div class="info-label">
                <el-icon><User /></el-icon>
                用户名
              </div>
              <div class="info-value">{{ profileStore.profile.username }}</div>
            </div>

            <div class="info-item">
              <div class="info-label">
                <el-icon><Message /></el-icon>
                邮箱
              </div>
              <div class="info-value">{{ profileStore.profile.email || '未设置' }}</div>
            </div>

            <div v-if="profileStore.isStudent" class="info-item">
              <div class="info-label">
                <el-icon><Postcard /></el-icon>
                学号
              </div>
              <div class="info-value">{{ profileStore.profile.student_id || '未设置' }}</div>
            </div>

            <div class="info-item">
              <div class="info-label">
                <el-icon><Calendar /></el-icon>
                注册时间
              </div>
              <div class="info-value">{{ formatTime(profileStore.profile.created_at) }}</div>
            </div>
          </div>
        </div>
      </el-card>

      <!-- 账户安全卡片 -->
      <el-card class="security-card">
        <template #header>
          <div class="card-header">
            <span>账户安全</span>
            <el-button
              type="primary"
              text
              @click="showPasswordDialog = true"
              :disabled="profileStore.updating"
            >
              <el-icon><Lock /></el-icon>
              修改密码
            </el-button>
          </div>
        </template>

        <div class="security-info">
          <div class="security-item">
            <div class="security-icon">
              <el-icon><Lock /></el-icon>
            </div>
            <div class="security-content">
              <h4>登录密码</h4>
              <p>定期更换密码可以提高账户安全性</p>
            </div>
            <div class="security-action">
              <el-button @click="showPasswordDialog = true">修改</el-button>
            </div>
          </div>

          <div class="security-item">
            <div class="security-icon">
              <el-icon><Message /></el-icon>
            </div>
            <div class="security-content">
              <h4>邮箱验证</h4>
              <p>{{ profileStore.profile.email ? '已绑定邮箱' : '未绑定邮箱，建议绑定以便找回密码' }}</p>
            </div>
            <div class="security-action">
              <el-button @click="openEditDialog">
                {{ profileStore.profile.email ? '修改' : '绑定' }}
              </el-button>
            </div>
          </div>
        </div>
      </el-card>
    </div>

    <!-- 编辑信息对话框 -->
    <el-dialog
      v-model="showEditDialog"
      title="编辑个人信息"
      width="500px"
      :close-on-click-modal="false"
    >
      <el-form
        ref="editFormRef"
        :model="editForm"
        :rules="editRules"
        label-width="80px"
      >
        <el-form-item label="真实姓名" prop="real_name">
          <el-input v-model="editForm.real_name" placeholder="请输入真实姓名" />
        </el-form-item>

        <el-form-item label="邮箱" prop="email">
          <el-input v-model="editForm.email" placeholder="请输入邮箱地址" />
        </el-form-item>
      </el-form>

      <template #footer>
        <el-button @click="showEditDialog = false">取消</el-button>
        <el-button
          type="primary"
          @click="handleUpdateInfo"
          :loading="profileStore.updating"
        >
          保存
        </el-button>
      </template>
    </el-dialog>

    <!-- 修改密码对话框 -->
    <el-dialog
      v-model="showPasswordDialog"
      title="修改密码"
      width="500px"
      :close-on-click-modal="false"
    >
      <el-form
        ref="passwordFormRef"
        :model="passwordForm"
        :rules="passwordRules"
        label-width="100px"
      >
        <el-form-item label="当前密码" prop="current_password">
          <el-input
            v-model="passwordForm.current_password"
            type="password"
            placeholder="请输入当前密码"
            show-password
          />
        </el-form-item>

        <el-form-item label="新密码" prop="new_password">
          <el-input
            v-model="passwordForm.new_password"
            type="password"
            placeholder="请输入新密码"
            show-password
          />
        </el-form-item>

        <el-form-item label="确认密码" prop="confirm_password">
          <el-input
            v-model="passwordForm.confirm_password"
            type="password"
            placeholder="请再次输入新密码"
            show-password
          />
        </el-form-item>
      </el-form>

      <template #footer>
        <el-button @click="showPasswordDialog = false">取消</el-button>
        <el-button
          type="primary"
          @click="handleUpdatePassword"
          :loading="profileStore.updating"
        >
          修改密码
        </el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted } from 'vue'
import { useProfileStore } from '@/stores'
import {
  Loading, Edit, User, Message, Postcard, Calendar, Lock
} from '@element-plus/icons-vue'
import type { FormInstance, FormRules } from 'element-plus'

const profileStore = useProfileStore()

// 响应式数据
const showEditDialog = ref(false)
const showPasswordDialog = ref(false)

// 表单引用
const editFormRef = ref<FormInstance>()
const passwordFormRef = ref<FormInstance>()

// 编辑信息表单
const editForm = reactive({
  real_name: '',
  email: ''
})

// 修改密码表单
const passwordForm = reactive({
  current_password: '',
  new_password: '',
  confirm_password: ''
})

// 表单验证规则
const editRules: FormRules = {
  real_name: [
    { required: true, message: '请输入真实姓名', trigger: 'blur' },
    { min: 2, max: 20, message: '姓名长度在 2 到 20 个字符', trigger: 'blur' }
  ],
  email: [
    { type: 'email', message: '请输入正确的邮箱地址', trigger: 'blur' }
  ]
}

const passwordRules: FormRules = {
  current_password: [
    { required: true, message: '请输入当前密码', trigger: 'blur' }
  ],
  new_password: [
    { required: true, message: '请输入新密码', trigger: 'blur' },
    { min: 6, message: '密码长度不能少于6位', trigger: 'blur' }
  ],
  confirm_password: [
    { required: true, message: '请确认新密码', trigger: 'blur' },
    {
      validator: (rule, value, callback) => {
        if (value !== passwordForm.new_password) {
          callback(new Error('两次输入的密码不一致'))
        } else {
          callback()
        }
      },
      trigger: 'blur'
    }
  ]
}

// 方法
const getRoleType = (role: string) => {
  switch (role) {
    case 'student': return 'primary'
    case 'teacher': return 'success'
    default: return 'info'
  }
}

const formatTime = (dateString: string) => {
  const date = new Date(dateString)
  return date.toLocaleDateString('zh-CN', {
    year: 'numeric',
    month: 'long',
    day: 'numeric'
  })
}

const fetchProfile = async () => {
  try {
    await profileStore.fetchProfile()
  } catch (error) {
    console.error('获取个人信息失败:', error)
  }
}

const handleUpdateInfo = async () => {
  if (!editFormRef.value) return

  try {
    await editFormRef.value.validate()

    await profileStore.updateProfile({
      real_name: editForm.real_name,
      email: editForm.email
    })

    showEditDialog.value = false
  } catch (error) {
    console.error('更新信息失败:', error)
  }
}

const handleUpdatePassword = async () => {
  if (!passwordFormRef.value) return

  try {
    await passwordFormRef.value.validate()

    await profileStore.updateProfile({
      current_password: passwordForm.current_password,
      new_password: passwordForm.new_password,
      confirm_password: passwordForm.confirm_password
    })

    showPasswordDialog.value = false

    // 清空表单
    passwordForm.current_password = ''
    passwordForm.new_password = ''
    passwordForm.confirm_password = ''
  } catch (error) {
    console.error('修改密码失败:', error)
  }
}

// 监听编辑对话框打开，填充表单数据
const openEditDialog = () => {
  if (profileStore.profile) {
    editForm.real_name = profileStore.profile.real_name
    editForm.email = profileStore.profile.email || ''
  }
  showEditDialog.value = true
}

// 页面加载时获取个人信息
onMounted(() => {
  fetchProfile()
})

// 更新按钮点击事件
const handleEditClick = () => {
  openEditDialog()
}
</script>

<style scoped>
.profile-container {
  padding: 24px;
  background: #f5f7fa;
  min-height: 100vh;
}

.page-header {
  margin-bottom: 24px;
}

.header-info h1 {
  margin: 0 0 4px 0;
  color: #303133;
  font-size: 24px;
  font-weight: 500;
}

.header-info p {
  margin: 0;
  color: #909399;
  font-size: 14px;
}

.loading-container,
.error-container {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 60px 20px;
  color: #909399;
}

.loading-container .el-icon {
  font-size: 32px;
  margin-bottom: 16px;
}

.profile-content {
  max-width: 800px;
  margin: 0 auto;
  display: flex;
  flex-direction: column;
  gap: 24px;
}

.profile-info-card,
.security-card {
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.1);
  border: none;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  font-weight: 500;
  color: #303133;
}

.profile-info {
  padding: 0;
}

.avatar-section {
  display: flex;
  align-items: center;
  gap: 20px;
  margin-bottom: 32px;
  padding-bottom: 24px;
  border-bottom: 1px solid #f0f0f0;
}

.user-avatar {
  background: linear-gradient(135deg, #409eff, #67c23a);
  color: white;
  font-size: 32px;
}

.user-basic h2 {
  margin: 0 0 8px 0;
  color: #303133;
  font-size: 20px;
  font-weight: 500;
}

.info-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
  gap: 24px;
}

.info-item {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.info-label {
  display: flex;
  align-items: center;
  gap: 8px;
  color: #909399;
  font-size: 14px;
  font-weight: 500;
}

.info-label .el-icon {
  font-size: 16px;
}

.info-value {
  color: #303133;
  font-size: 15px;
  padding-left: 24px;
}

.security-info {
  padding: 0;
}

.security-item {
  display: flex;
  align-items: center;
  gap: 16px;
  padding: 20px 0;
  border-bottom: 1px solid #f0f0f0;
}

.security-item:last-child {
  border-bottom: none;
}

.security-icon {
  width: 40px;
  height: 40px;
  border-radius: 50%;
  background: #f0f9ff;
  display: flex;
  align-items: center;
  justify-content: center;
  color: #409eff;
  font-size: 18px;
  flex-shrink: 0;
}

.security-content {
  flex: 1;
}

.security-content h4 {
  margin: 0 0 4px 0;
  color: #303133;
  font-size: 15px;
  font-weight: 500;
}

.security-content p {
  margin: 0;
  color: #909399;
  font-size: 13px;
  line-height: 1.4;
}

.security-action {
  flex-shrink: 0;
}

/* 响应式设计 */
@media (max-width: 768px) {
  .profile-container {
    padding: 16px;
  }

  .avatar-section {
    flex-direction: column;
    text-align: center;
    gap: 16px;
  }

  .info-grid {
    grid-template-columns: 1fr;
    gap: 16px;
  }

  .security-item {
    flex-direction: column;
    text-align: center;
    gap: 12px;
  }

  .card-header {
    flex-direction: column;
    gap: 12px;
    align-items: flex-start;
  }
}
</style>
