<template>
  <div class="dashboard">
    <h2>欢迎使用AI助教系统</h2>
    <p>当前用户：{{ authStore.user?.real_name }} ({{ authStore.user?.role === 'teacher' ? '教师' : '学生' }})</p>
    
    <div class="quick-actions">
      <el-button type="primary" @click="$router.push('/assignments')">
        查看作业
      </el-button>
      <el-button type="success" @click="$router.push('/qa')">
        智能答疑
      </el-button>
    </div>
  </div>
</template>

<script setup lang="ts">
import { useAuthStore } from '@/stores'

const authStore = useAuthStore()
</script>

<style scoped>
.dashboard {
  padding: 40px;
  text-align: center;
}

.dashboard h2 {
  margin-bottom: 20px;
  color: #303133;
}

.dashboard p {
  margin-bottom: 40px;
  color: #606266;
}

.quick-actions {
  display: flex;
  justify-content: center;
  gap: 20px;
}
</style>
