<template>
  <div class="layout">
    <header class="header">
      <div class="header-content">
        <h1>AI助教系统</h1>
        <div class="user-info">
          <span>{{ authStore.user?.real_name || authStore.user?.username }}</span>
          <el-button @click="handleLogout" size="small">退出</el-button>
        </div>
      </div>
    </header>
    
    <main class="main">
      <RouterView />
    </main>
  </div>
</template>

<script setup lang="ts">
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores'

const router = useRouter()
const authStore = useAuthStore()

const handleLogout = async () => {
  await authStore.logout()
  router.push('/login')
}
</script>

<style scoped>
.layout {
  height: 100vh;
  display: flex;
  flex-direction: column;
}

.header {
  background: #409eff;
  color: white;
  padding: 0 20px;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
}

.header-content {
  display: flex;
  justify-content: space-between;
  align-items: center;
  height: 60px;
}

.header h1 {
  margin: 0;
  font-size: 20px;
  font-weight: 500;
}

.user-info {
  display: flex;
  align-items: center;
  gap: 12px;
}

.main {
  flex: 1;
  overflow: auto;
  background: #f5f5f5;
}
</style>
