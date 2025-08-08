<template>
  <div 
    class="markdown-renderer" 
    :class="{
      'compact': compact,
      'no-padding': noPadding
    }"
    v-html="renderedContent"
  ></div>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import MarkdownIt from 'markdown-it'
import hljs from 'highlight.js'

interface Props {
  content: string
  compact?: boolean
  noPadding?: boolean
  enableHighlight?: boolean
}

const props = withDefaults(defineProps<Props>(), {
  compact: false,
  noPadding: false,
  enableHighlight: true
})

// 创建简化的markdown-it实例
const createMarkdownInstance = (): MarkdownIt => {
  const md: MarkdownIt = new MarkdownIt({
    html: true,
    linkify: true,
    typographer: true,
    breaks: false,
    highlight: props.enableHighlight ? (str, lang) => {
      if (lang && hljs.getLanguage(lang)) {
        try {
          return `<pre class="hljs"><code class="hljs language-${lang}">${hljs.highlight(str, { language: lang }).value}</code></pre>`
        } catch (error) {
          console.warn('Highlight error:', error)
        }
      }
      return `<pre class="hljs"><code class="hljs">${md.utils.escapeHtml(str)}</code></pre>`
    } : undefined
  })

  return md
}

// 渲染内容
const renderedContent = computed(() => {
  if (!props.content) return ''
  
  try {
    const md = createMarkdownInstance()
    return md.render(props.content)
  } catch (error) {
    console.error('Markdown rendering error:', error)
    return `<p style="color: #f56c6c;">Markdown渲染错误</p>`
  }
})
</script>

<style scoped>
/* 基础样式 */
.markdown-renderer {
  line-height: 1.7;
  color: #2c3e50;
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', 'PingFang SC', 'Hiragino Sans GB', 'Microsoft YaHei', 'Helvetica Neue', Helvetica, Arial, sans-serif;
  word-wrap: break-word;
  font-size: 16px;
  padding: 16px;
}

.markdown-renderer.compact {
  padding: 8px;
  font-size: 14px;
  line-height: 1.5;
}

.markdown-renderer.no-padding {
  padding: 0;
}

/* 标题样式 - Typora风格 */
.markdown-renderer :deep(h1) {
  font-size: 2em;
  font-weight: 600;
  margin: 1.2em 0 0.8em 0;
  padding-bottom: 0.3em;
  border-bottom: 2px solid #eaecef;
  color: #2c3e50;
}

.markdown-renderer :deep(h2) {
  font-size: 1.5em;
  font-weight: 600;
  margin: 1em 0 0.6em 0;
  padding-bottom: 0.2em;
  border-bottom: 1px solid #eaecef;
  color: #2c3e50;
}

.markdown-renderer :deep(h3) {
  font-size: 1.25em;
  font-weight: 600;
  margin: 0.8em 0 0.5em 0;
  color: #2c3e50;
}

.markdown-renderer :deep(h4) {
  font-size: 1.1em;
  font-weight: 600;
  margin: 0.6em 0 0.4em 0;
  color: #2c3e50;
}

.markdown-renderer :deep(h5),
.markdown-renderer :deep(h6) {
  font-size: 1em;
  font-weight: 600;
  margin: 0.5em 0 0.3em 0;
  color: #2c3e50;
}

/* 段落样式 */
.markdown-renderer :deep(p) {
  margin: 0.8em 0;
  line-height: inherit;
}

/* 列表样式 */
.markdown-renderer :deep(ul),
.markdown-renderer :deep(ol) {
  margin: 0.8em 0;
  padding-left: 2em;
}

.markdown-renderer :deep(li) {
  margin: 0.25em 0;
}

.markdown-renderer :deep(li > ul),
.markdown-renderer :deep(li > ol) {
  margin: 0.25em 0;
}

/* 文本装饰 */
.markdown-renderer :deep(strong),
.markdown-renderer :deep(b) {
  font-weight: 600;
  color: #2c3e50;
}

.markdown-renderer :deep(em),
.markdown-renderer :deep(i) {
  font-style: italic;
  color: #34495e;
}

.markdown-renderer :deep(del),
.markdown-renderer :deep(s) {
  text-decoration: line-through;
  color: #6c757d;
}

/* 链接样式 */
.markdown-renderer :deep(a) {
  color: #3498db;
  text-decoration: none;
  border-bottom: 1px solid transparent;
  transition: border-bottom-color 0.3s;
}

.markdown-renderer :deep(a:hover) {
  border-bottom-color: #3498db;
}

/* 代码样式 */
.markdown-renderer :deep(code) {
  background-color: #f8f9fa;
  color: #e83e8c;
  padding: 0.2em 0.4em;
  border-radius: 4px;
  font-family: 'SFMono-Regular', Consolas, 'Liberation Mono', Menlo, Courier, monospace;
  font-size: 0.85em;
}

.markdown-renderer :deep(pre) {
  background-color: #f8f9fa;
  border: 1px solid #e9ecef;
  border-radius: 6px;
  padding: 1em;
  margin: 1em 0;
  overflow-x: auto;
  font-family: 'SFMono-Regular', Consolas, 'Liberation Mono', Menlo, Courier, monospace;
  font-size: 0.85em;
  line-height: 1.45;
}

.markdown-renderer :deep(pre code) {
  background: none;
  color: inherit;
  padding: 0;
  border-radius: 0;
  font-size: inherit;
}

/* Highlight.js 代码高亮样式 */
.markdown-renderer :deep(.hljs) {
  background: #f8f9fa !important;
  color: #383a42;
}

/* 引用样式 */
.markdown-renderer :deep(blockquote) {
  border-left: 4px solid #ddd;
  margin: 1em 0;
  padding: 0.5em 1em;
  background-color: #f9f9f9;
  color: #6c757d;
  font-style: italic;
}

.markdown-renderer :deep(blockquote p) {
  margin: 0.5em 0;
}

/* 表格样式 */
.markdown-renderer :deep(table) {
  border-collapse: collapse;
  margin: 1em 0;
  width: 100%;
  max-width: 100%;
  overflow-x: auto;
}

.markdown-renderer :deep(table thead) {
  background-color: #f8f9fa;
}

.markdown-renderer :deep(table th),
.markdown-renderer :deep(table td) {
  border: 1px solid #dee2e6;
  padding: 0.5em 0.75em;
  text-align: left;
}

.markdown-renderer :deep(table th) {
  font-weight: 600;
  background-color: #f8f9fa;
}

.markdown-renderer :deep(table tr:nth-child(even)) {
  background-color: #fdfdfe;
}

.markdown-renderer :deep(table tr:hover) {
  background-color: #f5f5f5;
}

/* 分割线 */
.markdown-renderer :deep(hr) {
  border: none;
  border-top: 1px solid #eaecef;
  margin: 2em 0;
}

/* 图片样式 */
.markdown-renderer :deep(img) {
  max-width: 100%;
  height: auto;
  border-radius: 4px;
  margin: 0.5em 0;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
}

/* 紧凑模式调整 */
.markdown-renderer.compact :deep(h1) {
  font-size: 1.5em;
  margin: 0.8em 0 0.5em 0;
}

.markdown-renderer.compact :deep(h2) {
  font-size: 1.3em;
  margin: 0.6em 0 0.4em 0;
}

.markdown-renderer.compact :deep(h3) {
  font-size: 1.1em;
  margin: 0.5em 0 0.3em 0;
}

.markdown-renderer.compact :deep(p) {
  margin: 0.5em 0;
}

.markdown-renderer.compact :deep(ul),
.markdown-renderer.compact :deep(ol) {
  margin: 0.5em 0;
}

.markdown-renderer.compact :deep(blockquote) {
  margin: 0.5em 0;
  padding: 0.3em 0.8em;
}

.markdown-renderer.compact :deep(table) {
  margin: 0.5em 0;
}

.markdown-renderer.compact :deep(pre) {
  margin: 0.5em 0;
  padding: 0.5em;
}

/* 响应式设计 */
@media (max-width: 768px) {
  .markdown-renderer {
    font-size: 14px;
    padding: 12px;
  }
  
  .markdown-renderer.compact {
    font-size: 13px;
    padding: 6px;
  }
  
  .markdown-renderer :deep(table) {
    font-size: 0.9em;
  }
}
</style>