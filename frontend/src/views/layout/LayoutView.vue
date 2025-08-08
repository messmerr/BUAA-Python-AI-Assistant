<template>
  <div class="layout">
    <!-- 侧边导航栏 -->
    <aside class="sidebar">
      <div class="logo">
        <h2>AI助教系统</h2>
      </div>

      <el-menu
        :default-active="currentRoute"
        class="sidebar-menu"
        @select="handleMenuSelect"
      >
        <el-menu-item index="/dashboard">
          <el-icon><House /></el-icon>
          <span>首页</span>
        </el-menu-item>

        <el-menu-item index="/assignments">
          <el-icon><Document /></el-icon>
          <span>作业管理</span>
        </el-menu-item>

        <el-menu-item index="/qa">
          <el-icon><ChatDotRound /></el-icon>
          <span>智能答疑</span>
        </el-menu-item>

        <el-menu-item index="/chat">
          <el-icon><Message /></el-icon>
          <span class="menu-text">师生交流</span>
          <el-badge v-if="unreadCount > 0" :value="unreadCount" class="menu-badge" />
        </el-menu-item>

        <el-menu-item index="/reports">
          <el-icon><Document /></el-icon>
          <span>{{ authStore.user?.role === 'teacher' ? '班级报告' : '学习报告' }}</span>
        </el-menu-item>

        <el-menu-item index="/profile">
          <el-icon><User /></el-icon>
          <span>个人中心</span>
        </el-menu-item>
      </el-menu>
    </aside>

    <!-- 主内容区域 -->
    <div class="main-container">
      <!-- 顶部导航栏 -->
      <header class="header">
        <div class="header-content">
          <div class="breadcrumb">
            <span>{{ getPageTitle() }}</span>
          </div>

          <div class="user-info">
            <span class="user-name">
              {{ authStore.user?.real_name || authStore.user?.username }}
              <el-tag size="small" :type="authStore.user?.role === 'teacher' ? 'success' : 'primary'">
                {{ authStore.user?.role === 'teacher' ? '教师' : '学生' }}
              </el-tag>
            </span>
            <el-button @click="handleLogout" size="small" type="danger" plain>
              退出登录
            </el-button>
          </div>
        </div>
      </header>

      <!-- 页面内容 -->
      <main class="main">
        <RouterView />
      </main>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { useAuthStore, useChatStore } from '@/stores'
import { House, Document, ChatDotRound, Message, User } from '@element-plus/icons-vue'

const authStore = useAuthStore()
const chatStore = useChatStore()
const router = useRouter()
const route = useRoute()

// 未读消息数量
const unreadCount = computed(() => chatStore.totalUnreadCount)

onMounted(() => {
  // 获取未读消息数量
  chatStore.fetchUnreadCount()
})

// 当前路由
const currentRoute = computed(() => route.path)

// 处理菜单选择
const handleMenuSelect = (index: string) => {
  router.push(index)
}

// 获取页面标题
const getPageTitle = () => {
  const titleMap: Record<string, string> = {
    '/dashboard': '首页',
    '/assignments': '作业管理',
    '/qa': '智能答疑',
    '/chat': '师生交流',
    '/reports': authStore.user?.role === 'teacher' ? '班级报告' : '学习报告',
    '/profile': '个人中心'
  }
  return titleMap[route.path] || '首页'
}

// 退出登录
const handleLogout = async () => {
  await authStore.logout()
  router.push('/login')
}
</script>

<style scoped>
.layout {
  height: 100vh;
  display: flex;
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', 'Roboto', sans-serif;
}

/* 侧边栏 */
.sidebar {
  width: 220px;
  background: linear-gradient(180deg, #304156 0%, #283442 100%);
  color: white;
  display: flex;
  flex-direction: column;
  box-shadow: 2px 0 8px rgba(0, 0, 0, 0.1);
  position: relative;
  z-index: 10;
}

.sidebar::after {
  content: '';
  position: absolute;
  top: 0;
  right: 0;
  width: 1px;
  height: 100%;
  background: linear-gradient(180deg, transparent, rgba(255, 255, 255, 0.1), transparent);
}

.logo {
  padding: 24px 20px;
  text-align: center;
  border-bottom: 1px solid rgba(255, 255, 255, 0.1);
  position: relative;
  background: rgba(255, 255, 255, 0.05);
}

.logo::after {
  content: '';
  position: absolute;
  bottom: 0;
  left: 20%;
  right: 20%;
  height: 2px;
  background: linear-gradient(90deg, #409eff, #67c23a);
  border-radius: 1px;
}

.logo h2 {
  margin: 0;
  font-size: 18px;
  font-weight: 600;
  color: white;
  text-shadow: 0 1px 2px rgba(0, 0, 0, 0.3);
  letter-spacing: 0.5px;
}

.sidebar-menu {
  flex: 1;
  border: none;
  background: transparent;
  padding: 8px 0;
}

/* 菜单项样式调整 */
.sidebar-menu :deep(.el-menu-item) {
  color: rgba(191, 203, 217, 0.9);
  border-bottom: 1px solid rgba(255, 255, 255, 0.08);
  position: relative;
  display: flex;
  align-items: center;
  justify-content: flex-start;
  margin: 2px 12px;
  border-radius: 8px;
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
  padding: 16px 20px;
  font-size: 15px;
  font-weight: 500;
}

.sidebar-menu :deep(.el-menu-item)::before {
  content: '';
  position: absolute;
  left: 0;
  top: 50%;
  transform: translateY(-50%);
  width: 3px;
  height: 0;
  background: linear-gradient(180deg, #409eff, #67c23a);
  border-radius: 0 2px 2px 0;
  transition: height 0.3s ease;
}

.sidebar-menu :deep(.el-menu-item.is-active)::before,
.sidebar-menu :deep(.el-menu-item:hover)::before {
  height: 20px;
}

.menu-text {
  flex: 1;
  text-align: left;
  margin-left: 12px;
}

.menu-badge {
  position: absolute;
  right: 16px;
  top: 50%;
  transform: translateY(-50%);
  z-index: 2;
}

.menu-badge :deep(.el-badge__content) {
  position: static;
  transform: none;
  background: #f56c6c;
  border: 2px solid #304156;
  animation: pulse-badge 2s infinite;
}

@keyframes pulse-badge {
  0% {
    box-shadow: 0 0 0 0 rgba(245, 108, 108, 0.7);
  }
  70% {
    box-shadow: 0 0 0 6px rgba(245, 108, 108, 0);
  }
  100% {
    box-shadow: 0 0 0 0 rgba(245, 108, 108, 0);
  }
}

.sidebar-menu :deep(.el-menu-item .el-icon) {
  font-size: 18px;
  color: rgba(191, 203, 217, 0.8);
  transition: all 0.3s ease;
}

.sidebar-menu :deep(.el-menu-item:hover) {
  background: rgba(255, 255, 255, 0.1);
  color: white;
  transform: translateX(4px);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
}

.sidebar-menu :deep(.el-menu-item:hover .el-icon) {
  color: #409eff;
  transform: scale(1.1);
}

.sidebar-menu :deep(.el-menu-item.is-active) {
  background: linear-gradient(135deg, rgba(64, 158, 255, 0.2), rgba(103, 194, 58, 0.1));
  color: white;
  border-color: rgba(64, 158, 255, 0.3);
  box-shadow: 0 4px 12px rgba(64, 158, 255, 0.2);
}

.sidebar-menu :deep(.el-menu-item.is-active .el-icon) {
  color: #409eff;
}

/* 主内容区域 */
.main-container {
  flex: 1;
  display: flex;
  flex-direction: column;
  position: relative;
}

/* 顶部导航栏 */
.header {
  background: linear-gradient(135deg, #fff 0%, #f8fafc 100%);
  border-bottom: 1px solid rgba(228, 231, 237, 0.6);
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.06);
  position: relative;
  z-index: 5;
}

.header::after {
  content: '';
  position: absolute;
  bottom: 0;
  left: 0;
  right: 0;
  height: 1px;
  background: linear-gradient(90deg, transparent, rgba(64, 158, 255, 0.3), transparent);
}

.header-content {
  display: flex;
  justify-content: space-between;
  align-items: center;
  height: 64px;
  padding: 0 32px;
  max-width: 1400px;
  margin: 0 auto;
}

.breadcrumb {
  font-size: 18px;
  font-weight: 600;
  color: #303133;
  position: relative;
}

.breadcrumb::after {
  content: '';
  position: absolute;
  bottom: -4px;
  left: 0;
  width: 30px;
  height: 2px;
  background: linear-gradient(90deg, #409eff, #67c23a);
  border-radius: 1px;
}

.user-info {
  display: flex;
  align-items: center;
  gap: 16px;
}

.user-name {
  display: flex;
  align-items: center;
  gap: 10px;
  color: #606266;
  font-size: 15px;
  font-weight: 500;
  padding: 8px 16px;
  background: rgba(64, 158, 255, 0.05);
  border-radius: 20px;
  border: 1px solid rgba(64, 158, 255, 0.1);
  transition: all 0.3s ease;
}

.user-name:hover {
  background: rgba(64, 158, 255, 0.1);
  transform: translateY(-1px);
}

.user-info :deep(.el-button--danger.is-plain) {
  border-radius: 20px;
  font-weight: 500;
  transition: all 0.3s ease;
}

.user-info :deep(.el-button--danger.is-plain:hover) {
  transform: translateY(-1px);
  box-shadow: 0 4px 12px rgba(245, 108, 108, 0.3);
}

/* 主内容 */
.main {
  flex: 1;
  overflow: auto;
  background: linear-gradient(135deg, #f5f5f5 0%, #f0f2f5 100%);
  position: relative;
}

.main::before {
  content: '';
  position: fixed;
  top: 0;
  left: 220px;
  right: 0;
  bottom: 0;
  background: 
    radial-gradient(circle at 20% 50%, rgba(64, 158, 255, 0.03) 0%, transparent 50%),
    radial-gradient(circle at 80% 20%, rgba(103, 194, 58, 0.03) 0%, transparent 50%),
    radial-gradient(circle at 40% 80%, rgba(230, 162, 60, 0.03) 0%, transparent 50%);
  pointer-events: none;
  z-index: 0;
}

/* 响应式设计 */
@media (max-width: 768px) {
  .sidebar {
    width: 200px;
  }
  
  .logo h2 {
    font-size: 16px;
  }
  
  .sidebar-menu :deep(.el-menu-item) {
    padding: 14px 16px;
    font-size: 14px;
  }
  
  .header-content {
    padding: 0 20px;
  }
  
  .breadcrumb {
    font-size: 16px;
  }
  
  .user-name {
    font-size: 14px;
    padding: 6px 12px;
  }
}
</style>











