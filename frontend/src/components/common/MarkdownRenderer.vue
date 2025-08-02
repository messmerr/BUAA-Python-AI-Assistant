<template>
  <div class="markdown-content" v-html="renderedContent"></div>
</template>

<script setup lang="ts">
import { computed } from 'vue'

interface Props {
  content: string
}

const props = defineProps<Props>()

// 简单的Markdown渲染（可以后续替换为更完整的库）
const renderedContent = computed(() => {
  if (!props.content) return ''
  
  let html = props.content
  
  // 标题
  html = html.replace(/^### (.*$)/gim, '<h3>$1</h3>')
  html = html.replace(/^## (.*$)/gim, '<h2>$1</h2>')
  html = html.replace(/^# (.*$)/gim, '<h1>$1</h1>')
  
  // 粗体
  html = html.replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
  
  // 列表
  html = html.replace(/^\- (.*$)/gim, '<li>$1</li>')
  html = html.replace(/(<li>.*<\/li>)/s, '<ul>$1</ul>')
  
  // 换行
  html = html.replace(/\n/g, '<br>')
  
  return html
})
</script>

<style scoped>
.markdown-content {
  line-height: 1.6;
}

.markdown-content h1 {
  font-size: 24px;
  margin: 20px 0 16px 0;
  color: #303133;
}

.markdown-content h2 {
  font-size: 20px;
  margin: 16px 0 12px 0;
  color: #303133;
}

.markdown-content h3 {
  font-size: 16px;
  margin: 12px 0 8px 0;
  color: #303133;
}

.markdown-content ul {
  margin: 8px 0;
  padding-left: 20px;
}

.markdown-content li {
  margin: 4px 0;
}

.markdown-content strong {
  font-weight: 600;
  color: #303133;
}
</style>

