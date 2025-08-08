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

        <div class="action-card" @click="$router.push('/chat')">
          <el-icon class="card-icon" size="32"><Message /></el-icon>
          <h4>师生交流</h4>
          <p>与{{ authStore.user?.role === 'teacher' ? '学生' : '老师' }}在线交流</p>
          <el-badge v-if="unreadCount > 0" :value="unreadCount" class="chat-badge" />
        </div>

        <div class="action-card" @click="$router.push('/reports')">
          <el-icon class="card-icon" size="32"><Document /></el-icon>
          <h4>{{ authStore.user?.role === 'teacher' ? '班级报告' : '学习报告' }}</h4>
          <p>{{ authStore.user?.role === 'teacher' ? '查看班级学习分析报告' : '查看个人学习分析报告' }}</p>
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
import { computed, onMounted } from 'vue'
import { useAuthStore, useChatStore } from '@/stores'
import { Document, ChatDotRound, Message, User } from '@element-plus/icons-vue'

const authStore = useAuthStore()
const chatStore = useChatStore()

// 未读消息数量
const unreadCount = computed(() => chatStore.totalUnreadCount)

onMounted(() => {
  chatStore.fetchUnreadCount()
})
</script>

<style scoped>
.dashboard {
  padding: 24px;
  max-width: 1200px;
  margin: 0 auto;
  animation: fadeIn 0.6s ease-out;
}

@keyframes fadeIn {
  from {
    opacity: 0;
    transform: translateY(20px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

.welcome-section {
  background: linear-gradient(135deg, #fff 0%, #f8fafc 100%);
  padding: 48px 40px;
  border-radius: 16px;
  box-shadow: 
    0 8px 32px rgba(0, 0, 0, 0.08),
    0 2px 8px rgba(0, 0, 0, 0.04);
  margin-bottom: 32px;
  text-align: center;
  position: relative;
  overflow: hidden;
  border: 1px solid rgba(255, 255, 255, 0.8);
}

.welcome-section::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  height: 4px;
  background: linear-gradient(90deg, #409eff, #67c23a, #e6a23c, #f56c6c);
  border-radius: 16px 16px 0 0;
}

.welcome-section::after {
  content: '';
  position: absolute;
  top: -50%;
  right: -20%;
  width: 200px;
  height: 200px;
  background: radial-gradient(circle, rgba(64, 158, 255, 0.1) 0%, transparent 70%);
  border-radius: 50%;
  animation: pulse 4s ease-in-out infinite;
}

@keyframes pulse {
  0%, 100% {
    transform: scale(1);
    opacity: 0.5;
  }
  50% {
    transform: scale(1.1);
    opacity: 0.8;
  }
}

.welcome-section h1 {
  margin: 0 0 16px 0;
  color: #303133;
  font-size: 32px;
  font-weight: 600;
  position: relative;
  z-index: 1;
}

.welcome-text {
  margin: 0;
  color: #606266;
  font-size: 18px;
  position: relative;
  z-index: 1;
}

.quick-actions h3 {
  margin: 0 0 24px 0;
  color: #303133;
  font-size: 24px;
  font-weight: 600;
  position: relative;
}

.quick-actions h3::after {
  content: '';
  position: absolute;
  bottom: -8px;
  left: 0;
  width: 40px;
  height: 3px;
  background: linear-gradient(90deg, #409eff, #67c23a);
  border-radius: 2px;
}

.action-cards {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
  gap: 24px;
}

.action-card {
  background: linear-gradient(135deg, #fff 0%, #f8fafc 100%);
  padding: 36px 28px;
  border-radius: 16px;
  box-shadow: 
    0 8px 32px rgba(0, 0, 0, 0.08),
    0 2px 8px rgba(0, 0, 0, 0.04);
  text-align: center;
  cursor: pointer;
  transition: all 0.4s cubic-bezier(0.4, 0, 0.2, 1);
  position: relative;
  overflow: hidden;
  border: 1px solid rgba(255, 255, 255, 0.8);
}

.action-card::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  height: 3px;
  background: linear-gradient(90deg, transparent, #409eff, transparent);
  transform: translateX(-100%);
  transition: transform 0.6s ease;
}

.action-card:hover::before {
  transform: translateX(100%);
}

.action-card::after {
  content: '';
  position: absolute;
  top: 50%;
  left: 50%;
  width: 0;
  height: 0;
  background: radial-gradient(circle, rgba(64, 158, 255, 0.1) 0%, transparent 70%);
  border-radius: 50%;
  transition: all 0.4s ease;
  transform: translate(-50%, -50%);
  z-index: 0;
}

.action-card:hover::after {
  width: 200px;
  height: 200px;
}

.action-card:hover {
  transform: translateY(-8px) scale(1.02);
  box-shadow: 
    0 20px 40px rgba(0, 0, 0, 0.12),
    0 8px 16px rgba(0, 0, 0, 0.08);
  border-color: rgba(64, 158, 255, 0.2);
}

.card-icon {
  color: #409eff;
  margin-bottom: 20px;
  position: relative;
  z-index: 1;
  transition: all 0.3s ease;
}

.action-card:hover .card-icon {
  transform: scale(1.1);
  filter: drop-shadow(0 4px 8px rgba(64, 158, 255, 0.3));
}

.action-card h4 {
  margin: 0 0 14px 0;
  color: #303133;
  font-size: 20px;
  font-weight: 600;
  position: relative;
  z-index: 1;
  transition: color 0.3s ease;
}

.action-card:hover h4 {
  color: #409eff;
}

.action-card p {
  margin: 0;
  color: #606266;
  font-size: 15px;
  line-height: 1.6;
  position: relative;
  z-index: 1;
}

.chat-badge {
  position: absolute;
  top: 20px;
  right: 20px;
  z-index: 2;
  animation: bounce 2s infinite;
}

@keyframes bounce {
  0%, 20%, 53%, 80%, 100% {
    transform: translate3d(0, 0, 0);
  }
  40%, 43% {
    transform: translate3d(0, -8px, 0);
  }
  70% {
    transform: translate3d(0, -4px, 0);
  }
  90% {
    transform: translate3d(0, -2px, 0);
  }
}

/* 响应式设计 */
@media (max-width: 768px) {
  .dashboard {
    padding: 16px;
  }
  
  .welcome-section {
    padding: 32px 24px;
    margin-bottom: 24px;
  }
  
  .welcome-section h1 {
    font-size: 24px;
  }
  
  .welcome-text {
    font-size: 16px;
  }
  
  .quick-actions h3 {
    font-size: 20px;
  }
  
  .action-cards {
    grid-template-columns: 1fr;
    gap: 16px;
  }
  
  .action-card {
    padding: 28px 20px;
  }
}
</style>




