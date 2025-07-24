<template>
  <div class="page-container">
    <!-- 页面头部 -->
    <div v-if="title || $slots.header" class="page-header">
      <div class="page-title">
        <h1 v-if="title">{{ title }}</h1>
        <slot name="header" />
      </div>
      <div v-if="$slots.actions" class="page-actions">
        <slot name="actions" />
      </div>
    </div>

    <!-- 页面内容 -->
    <div class="page-content" :class="{ 'no-padding': noPadding }">
      <slot />
    </div>
  </div>
</template>

<script setup lang="ts">
interface Props {
  title?: string
  noPadding?: boolean
}

withDefaults(defineProps<Props>(), {
  title: '',
  noPadding: false
})
</script>

<style scoped>
.page-container {
  height: 100%;
  display: flex;
  flex-direction: column;
}

.page-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 16px 24px;
  border-bottom: 1px solid #e4e7ed;
  background: #fff;
}

.page-title h1 {
  margin: 0;
  font-size: 20px;
  font-weight: 500;
  color: #303133;
}

.page-actions {
  display: flex;
  gap: 12px;
}

.page-content {
  flex: 1;
  padding: 24px;
  overflow: auto;
}

.page-content.no-padding {
  padding: 0;
}
</style>
