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
import { computed } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { useAuthStore } from '@/stores'
import { House, Document, ChatDotRound, User } from '@element-plus/icons-vue'

const router = useRouter()
const route = useRoute()
const authStore = useAuthStore()

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
}

/* 侧边栏 */
.sidebar {
  width: 200px;
  background: #304156;
  color: white;
  display: flex;
  flex-direction: column;
}

.logo {
  padding: 20px;
  text-align: center;
  border-bottom: 1px solid #434a5a;
}

.logo h2 {
  margin: 0;
  font-size: 16px;
  font-weight: 500;
  color: white;
}

.sidebar-menu {
  flex: 1;
  border: none;
  background: transparent;
}

.sidebar-menu :deep(.el-menu-item) {
  color: #bfcbd9;
  border-bottom: 1px solid #434a5a;
}

.sidebar-menu :deep(.el-menu-item:hover) {
  background-color: #434a5a;
  color: white;
}

.sidebar-menu :deep(.el-menu-item.is-active) {
  background-color: #409eff;
  color: white;
}

/* 主内容区域 */
.main-container {
  flex: 1;
  display: flex;
  flex-direction: column;
}

/* 顶部导航栏 */
.header {
  background: white;
  border-bottom: 1px solid #e4e7ed;
  box-shadow: 0 1px 4px rgba(0, 0, 0, 0.08);
}

.header-content {
  display: flex;
  justify-content: space-between;
  align-items: center;
  height: 60px;
  padding: 0 24px;
}

.breadcrumb {
  font-size: 16px;
  font-weight: 500;
  color: #303133;
}

.user-info {
  display: flex;
  align-items: center;
  gap: 12px;
}

.user-name {
  display: flex;
  align-items: center;
  gap: 8px;
  color: #606266;
  font-size: 14px;
}

/* 主内容 */
.main {
  flex: 1;
  overflow: auto;
  background: #f5f5f5;
}
</style>
