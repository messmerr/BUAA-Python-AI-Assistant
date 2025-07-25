<template>
  <div class="dashboard">
    <div class="welcome-section">
      <h1>欢迎回来，{{ authStore.user?.real_name }}！</h1>
      <p class="welcome-text">
        您好，{{ authStore.user?.role === 'teacher' ? '老师' : '同学' }}！
        今天也要加油哦～
      </p>
    </div>

    <div class="quick-actions">
      <h3>快速操作</h3>
      <div class="action-cards">
        <div class="action-card" @click="$router.push('/assignments')">
          <el-icon class="card-icon" size="32"><Document /></el-icon>
          <h4>作业管理</h4>
          <p>{{ authStore.user?.role === 'teacher' ? '创建和管理作业' : '查看和提交作业' }}</p>
        </div>

        <div class="action-card" @click="$router.push('/qa')">
          <el-icon class="card-icon" size="32"><ChatDotRound /></el-icon>
          <h4>智能答疑</h4>
          <p>AI助手为您答疑解惑</p>
        </div>

        <div class="action-card" @click="$router.push('/reports')">
          <el-icon class="card-icon" size="32"><Document /></el-icon>
          <h4>学习报告</h4>
          <p>查看个人学习分析报告</p>
        </div>

        <div class="action-card" @click="$router.push('/profile')">
          <el-icon class="card-icon" size="32"><User /></el-icon>
          <h4>个人中心</h4>
          <p>管理个人信息和设置</p>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { useAuthStore } from '@/stores'
import { Document, ChatDotRound, User } from '@element-plus/icons-vue'

const authStore = useAuthStore()
</script>

<style scoped>
.dashboard {
  padding: 24px;
  max-width: 1200px;
  margin: 0 auto;
}

.welcome-section {
  background: white;
  padding: 40px;
  border-radius: 8px;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.1);
  margin-bottom: 24px;
  text-align: center;
}

.welcome-section h1 {
  margin: 0 0 16px 0;
  color: #303133;
  font-size: 28px;
  font-weight: 500;
}

.welcome-text {
  margin: 0;
  color: #606266;
  font-size: 16px;
}

.quick-actions h3 {
  margin: 0 0 20px 0;
  color: #303133;
  font-size: 20px;
  font-weight: 500;
}

.action-cards {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
  gap: 20px;
}

.action-card {
  background: white;
  padding: 32px 24px;
  border-radius: 8px;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.1);
  text-align: center;
  cursor: pointer;
  transition: all 0.3s ease;
}

.action-card:hover {
  transform: translateY(-4px);
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.15);
}

.card-icon {
  color: #409eff;
  margin-bottom: 16px;
}

.action-card h4 {
  margin: 0 0 12px 0;
  color: #303133;
  font-size: 18px;
  font-weight: 500;
}

.action-card p {
  margin: 0;
  color: #606266;
  font-size: 14px;
  line-height: 1.5;
}
</style>
