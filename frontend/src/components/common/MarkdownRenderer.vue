<template>
  <div 
    class="markdown-content" 
    v-html="renderedContent"
    :class="{ 'compact': compact }"
  ></div>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import MarkdownIt from 'markdown-it'

interface Props {
  content: string
  compact?: boolean  // 紧凑模式，用于评语等简短内容
}

const props = withDefaults(defineProps<Props>(), {
  content: '',
  compact: false
})

// 配置Markdown解析器
const md = new MarkdownIt({
  html: true,        // 允许HTML标签
  breaks: true,      // 将换行符转换为<br>
  linkify: true,     // 自动识别链接
  typographer: true  // 启用一些语言中性的替换和引号美化
})

// 渲染Markdown内容
const renderedContent = computed(() => {
  if (!props.content) return ''
  
  try {
    return md.render(props.content)
  } catch (error) {
    console.error('Markdown渲染失败:', error)
    // 如果渲染失败，返回原始内容（转义HTML）
    return props.content.replace(/</g, '&lt;').replace(/>/g, '&gt;').replace(/\n/g, '<br>')
  }
})
</script>

<style scoped>
.markdown-content {
  line-height: 1.6;
  color: #333;
  word-wrap: break-word;
}

/* 标题样式 */
.markdown-content :deep(h1) {
  font-size: 1.8em;
  font-weight: 600;
  margin: 1.2em 0 0.8em 0;
  padding-bottom: 0.3em;
  border-bottom: 2px solid #eaecef;
  color: #2c3e50;
}

.markdown-content :deep(h2) {
  font-size: 1.5em;
  font-weight: 600;
  margin: 1em 0 0.6em 0;
  padding-bottom: 0.2em;
  border-bottom: 1px solid #eaecef;
  color: #2c3e50;
}

.markdown-content :deep(h3) {
  font-size: 1.3em;
  font-weight: 600;
  margin: 0.8em 0 0.5em 0;
  color: #2c3e50;
}

.markdown-content :deep(h4),
.markdown-content :deep(h5),
.markdown-content :deep(h6) {
  font-size: 1.1em;
  font-weight: 600;
  margin: 0.6em 0 0.4em 0;
  color: #2c3e50;
}

/* 段落样式 */
.markdown-content :deep(p) {
  margin: 0.8em 0;
  line-height: 1.7;
}

/* 列表样式 */
.markdown-content :deep(ul),
.markdown-content :deep(ol) {
  margin: 0.8em 0;
  padding-left: 2em;
}

.markdown-content :deep(li) {
  margin: 0.3em 0;
  line-height: 1.6;
}

.markdown-content :deep(ul li) {
  list-style-type: disc;
}

.markdown-content :deep(ol li) {
  list-style-type: decimal;
}

/* 代码样式 */
.markdown-content :deep(code) {
  background: #f1f3f4;
  padding: 0.2em 0.4em;
  border-radius: 3px;
  font-family: 'Monaco', 'Menlo', 'Ubuntu Mono', monospace;
  font-size: 0.9em;
  color: #e83e8c;
}

.markdown-content :deep(pre) {
  background: #f8f9fa;
  border: 1px solid #e9ecef;
  border-radius: 6px;
  padding: 1em;
  margin: 1em 0;
  overflow-x: auto;
  line-height: 1.4;
}

.markdown-content :deep(pre code) {
  background: none;
  padding: 0;
  color: #333;
  font-size: 0.9em;
}

/* 引用样式 */
.markdown-content :deep(blockquote) {
  border-left: 4px solid #409eff;
  background: #f8f9fa;
  margin: 1em 0;
  padding: 0.8em 1.2em;
  color: #666;
  font-style: italic;
}

.markdown-content :deep(blockquote p) {
  margin: 0.5em 0;
}

/* 链接样式 */
.markdown-content :deep(a) {
  color: #409eff;
  text-decoration: none;
  border-bottom: 1px solid transparent;
  transition: border-color 0.2s;
}

.markdown-content :deep(a:hover) {
  border-bottom-color: #409eff;
}

/* 表格样式 */
.markdown-content :deep(table) {
  border-collapse: collapse;
  width: 100%;
  margin: 1em 0;
  border: 1px solid #ddd;
}

.markdown-content :deep(th),
.markdown-content :deep(td) {
  border: 1px solid #ddd;
  padding: 0.6em 1em;
  text-align: left;
}

.markdown-content :deep(th) {
  background: #f8f9fa;
  font-weight: 600;
}

/* 分隔线样式 */
.markdown-content :deep(hr) {
  border: none;
  border-top: 2px solid #eaecef;
  margin: 2em 0;
}

/* 强调样式 */
.markdown-content :deep(strong) {
  font-weight: 600;
  color: #2c3e50;
}

.markdown-content :deep(em) {
  font-style: italic;
  color: #666;
}

/* 紧凑模式样式 */
.markdown-content.compact :deep(h1),
.markdown-content.compact :deep(h2),
.markdown-content.compact :deep(h3),
.markdown-content.compact :deep(h4),
.markdown-content.compact :deep(h5),
.markdown-content.compact :deep(h6) {
  margin: 0.5em 0 0.3em 0;
  font-size: 1.1em;
}

.markdown-content.compact :deep(p) {
  margin: 0.5em 0;
}

.markdown-content.compact :deep(ul),
.markdown-content.compact :deep(ol) {
  margin: 0.5em 0;
  padding-left: 1.5em;
}

.markdown-content.compact :deep(li) {
  margin: 0.2em 0;
}

.markdown-content.compact :deep(pre) {
  margin: 0.5em 0;
  padding: 0.8em;
}

.markdown-content.compact :deep(blockquote) {
  margin: 0.5em 0;
  padding: 0.5em 1em;
}

/* 响应式设计 */
@media (max-width: 768px) {
  .markdown-content {
    font-size: 14px;
  }
  
  .markdown-content :deep(pre) {
    padding: 0.8em;
    font-size: 0.85em;
  }
  
  .markdown-content :deep(table) {
    font-size: 0.9em;
  }
  
  .markdown-content :deep(th),
  .markdown-content :deep(td) {
    padding: 0.4em 0.6em;
  }
}
</style>
