<template>
  <div class="loading-spinner" :class="{ 'full-screen': fullScreen }">
    <el-icon class="is-loading" :size="size">
      <Loading />
    </el-icon>
    <p v-if="text" class="loading-text">{{ text }}</p>
  </div>
</template>

<script setup lang="ts">
import { Loading } from '@element-plus/icons-vue'

interface Props {
  size?: number
  text?: string
  fullScreen?: boolean
}

withDefaults(defineProps<Props>(), {
  size: 24,
  text: '',
  fullScreen: false
})
</script>

<style scoped>
.loading-spinner {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 40px;
}

.loading-spinner.full-screen {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(255, 255, 255, 0.8);
  z-index: 9999;
}

.loading-text {
  margin-top: 12px;
  color: #606266;
  font-size: 14px;
}
</style>
