<template>
  <div class="qa-chat">
    <!-- 聊天头部 -->
    <div class="chat-header">
      <div class="header-info">
        <el-icon class="ai-icon"><ChatDotRound /></el-icon>
        <div class="title-info">
          <h1>AI智能答疑</h1>
          <p>有任何学习问题都可以问我哦～</p>
        </div>
      </div>
      <div class="header-actions">
        <el-button @click="toggleHistory" :type="showHistory ? 'primary' : 'default'">
          <el-icon><Clock /></el-icon>
          历史记录
        </el-button>
        <el-button @click="clearChat" :disabled="messages.length === 0">
          <el-icon><Delete /></el-icon>
          清空对话
        </el-button>
      </div>
    </div>

    <!-- 历史记录面板 -->
    <div v-if="showHistory" class="history-panel">
      <div class="history-header">
        <h3>历史对话记录</h3>
        <div class="history-filters">
          <el-select
            v-model="historySubjectFilter"
            placeholder="筛选学科"
            size="small"
            style="width: 120px"
            clearable
            @change="fetchHistoryQuestions"
          >
            <el-option label="Python" value="Python" />
            <el-option label="数学" value="数学" />
            <el-option label="算法" value="算法" />
            <el-option label="数据结构" value="数据结构" />
            <el-option label="其他" value="其他" />
          </el-select>
        </div>
      </div>

      <div class="history-content">
        <div v-if="qaStore.loading" class="history-loading">
          <el-icon class="is-loading"><Loading /></el-icon>
          <span>加载中...</span>
        </div>

        <div v-else-if="historyQuestions.length === 0" class="history-empty">
          <el-empty description="暂无历史记录" />
        </div>

        <div v-else class="history-list">
          <div
            v-for="question in historyQuestions"
            :key="question.id"
            class="history-item"
            @click="loadHistoryQuestion(question)"
          >
            <div class="history-item-header">
              <span class="history-subject">{{ question.subject }}</span>
              <span class="history-time">{{ formatHistoryTime(question.created_at) }}</span>
            </div>
            <div class="history-question">
              {{ question.question_text }}
            </div>
            <div class="history-answer">
              {{ question.ai_answer.substring(0, 100) }}{{ question.ai_answer.length > 100 ? '...' : '' }}
            </div>
          </div>
        </div>

        <!-- 分页 -->
        <div v-if="historyPagination.total > 0" class="history-pagination">
          <el-pagination
            v-model:current-page="historyPage"
            :page-size="historyPageSize"
            :total="historyPagination.total"
            layout="prev, pager, next"
            small
            @current-change="handleHistoryPageChange"
          />
        </div>
      </div>
    </div>

    <!-- 聊天消息区域 -->
    <div class="chat-messages" ref="messagesContainer">
      <!-- 欢迎消息 -->
      <div v-if="messages.length === 0" class="welcome-message">
        <div class="ai-avatar">
          <el-icon><ChatDotRound /></el-icon>
        </div>
        <div class="welcome-content">
          <h3>👋 你好！我是AI助教</h3>
          <p>我可以帮你解答各种学习问题，包括：</p>
          <ul>
            <li>📚 课程知识点解释</li>
            <li>💻 编程问题解答</li>
            <li>🧮 数学公式推导</li>
            <li>📝 作业题目讲解</li>
          </ul>
          <p>快来问我问题吧！</p>
        </div>
      </div>

      <!-- 聊天消息列表 -->
      <div v-for="message in messages" :key="message.id" class="message-item">
        <!-- 用户消息 -->
        <div v-if="message.type === 'user'" class="message user-message">
          <div class="message-content">
            <div class="message-bubble user-bubble">
              <p>{{ message.content }}</p>
              <div class="message-meta">
                <span class="subject-tag" v-if="message.subject">{{ message.subject }}</span>
                <span class="time">{{ formatTime(message.timestamp) }}</span>
              </div>
            </div>
          </div>
          <div class="user-avatar">
            <el-icon><User /></el-icon>
          </div>
        </div>

        <!-- AI回答 -->
        <div v-if="message.type === 'ai'" class="message ai-message">
          <div class="ai-avatar">
            <el-icon><ChatDotRound /></el-icon>
          </div>
          <div class="message-content">
            <div class="message-bubble ai-bubble">
              <div v-if="message.loading" class="loading-dots">
                <span></span>
                <span></span>
                <span></span>
              </div>
              <div v-else class="ai-answer">
                <MarkdownRenderer :content="message.content" />
              </div>
              <div v-if="!message.loading" class="message-meta">
                <span class="time">{{ formatTime(message.timestamp) }}</span>
                <el-button
                  type="primary"
                  text
                  size="small"
                  @click="copyAnswer(message.content)"
                >
                  <el-icon><CopyDocument /></el-icon>
                  复制
                </el-button>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- 输入区域 -->
    <div class="chat-input">
      <div class="input-container">
        <!-- 学科选择 -->
        <div class="subject-selector">
          <el-select
            v-model="currentSubject"
            placeholder="选择学科"
            size="small"
            style="width: 120px"
          >
            <el-option label="Python" value="Python" />
            <el-option label="数学" value="数学" />
            <el-option label="算法" value="算法" />
            <el-option label="数据结构" value="数据结构" />
            <el-option label="其他" value="其他" />
          </el-select>
        </div>

        <!-- 消息输入框 -->
        <div class="input-wrapper">
          <el-input
            v-model="inputMessage"
            type="textarea"
            :rows="1"
            :autosize="{ minRows: 1, maxRows: 4 }"
            placeholder="输入你的问题..."
            @keydown.enter.exact.prevent="sendMessage"
            @keydown.enter.shift.exact="handleShiftEnter"
            :disabled="isLoading"
          />
        </div>

        <!-- 发送按钮 -->
        <el-button
          type="primary"
          :loading="isLoading"
          :disabled="!inputMessage.trim()"
          @click="sendMessage"
          class="send-button"
        >
          <el-icon v-if="!isLoading"><Promotion /></el-icon>
          {{ isLoading ? '思考中...' : '发送' }}
        </el-button>
      </div>

      <!-- 输入提示 -->
      <div class="input-tips">
        <span>按 Enter 发送，Shift + Enter 换行</span>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, nextTick, onMounted, onUnmounted } from 'vue'
import { useQAStore } from '@/stores'
import { ChatDotRound, User, Delete, CopyDocument, Promotion, Clock, Loading } from '@element-plus/icons-vue'
import { ElMessage } from 'element-plus'
import MarkdownRenderer from '@/components/common/MarkdownRenderer.vue'

const qaStore = useQAStore()

// 当前会话ID
const currentSessionId = ref<string | null>(null)

// 消息列表
const messages = ref<Array<{
  id: string
  type: 'user' | 'ai'
  content: string
  timestamp: Date
  loading?: boolean
  subject?: string
}>>([])

// 输入相关
const inputMessage = ref('')
const currentSubject = ref('Python')
const isLoading = ref(false)

// 历史记录相关
const showHistory = ref(false)
const historyQuestions = ref<any[]>([])
const historySubjectFilter = ref('')
const historyPage = ref(1)
const historyPageSize = ref(10)
const historyPagination = ref({
  page: 1,
  page_size: 10,
  total: 0,
  total_pages: 0
})

// DOM引用
const messagesContainer = ref<HTMLElement>()

// 发送消息
const sendMessage = async () => {
  if (!inputMessage.value.trim() || isLoading.value) return

  const userMessage = inputMessage.value.trim()
  const messageId = Date.now().toString()

  // 添加用户消息
  messages.value.push({
    id: messageId + '_user',
    type: 'user',
    content: userMessage,
    timestamp: new Date(),
    subject: currentSubject.value
  })

  // 添加AI加载消息
  const aiMessageId = messageId + '_ai'
  messages.value.push({
    id: aiMessageId,
    type: 'ai',
    content: '',
    timestamp: new Date(),
    loading: true
  })

  // 清空输入框
  inputMessage.value = ''
  isLoading.value = true

  // 滚动到底部
  await nextTick()
  scrollToBottom()

  try {
    // 调用新的聊天API
    const response = await qaStore.sendChatMessage({
      session_id: currentSessionId.value || undefined,
      message: userMessage,
      subject: currentSubject.value
    })

    // 更新会话ID
    if (!currentSessionId.value) {
      currentSessionId.value = response.session_id
    }

    // 更新AI消息
    const aiMessageIndex = messages.value.findIndex(m => m.id === aiMessageId)
    if (aiMessageIndex !== -1) {
      messages.value[aiMessageIndex] = {
        id: aiMessageId,
        type: 'ai',
        content: response.ai_response,
        timestamp: new Date(response.created_at),
        loading: false
      }
    }

    // 滚动到底部
    await nextTick()
    scrollToBottom()

  } catch (error) {
    console.error('发送消息失败:', error)

    // 更新AI消息为错误信息
    const aiMessageIndex = messages.value.findIndex(m => m.id === aiMessageId)
    if (aiMessageIndex !== -1) {
      messages.value[aiMessageIndex] = {
        id: aiMessageId,
        type: 'ai',
        content: '抱歉，我暂时无法回答您的问题，请稍后重试。',
        timestamp: new Date(),
        loading: false
      }
    }
  } finally {
    isLoading.value = false
  }
}

// 处理Shift+Enter换行
const handleShiftEnter = () => {
  // 允许默认行为（换行）
}

// 清空对话
const clearChat = () => {
  messages.value = []
  currentSessionId.value = null
}

// 切换历史记录面板
const toggleHistory = async () => {
  showHistory.value = !showHistory.value
  if (showHistory.value && historyQuestions.value.length === 0) {
    await fetchHistoryQuestions()
  }
}

// 获取历史会话列表
const fetchHistoryQuestions = async () => {
  try {
    const params = {
      page: historyPage.value,
      page_size: historyPageSize.value,
      subject: historySubjectFilter.value || undefined
    }
    const response = await qaStore.fetchSessions(params)
    // 转换会话数据为历史问题格式以兼容现有UI
    historyQuestions.value = response.sessions.map(session => ({
      id: session.id,
      subject: session.subject,
      created_at: session.updated_at,
      question_text: session.last_message?.content || '新对话',
      ai_answer: session.last_message?.role === 'ai' ? session.last_message.content : '等待回复...'
    }))
    historyPagination.value = response.pagination
  } catch (error) {
    console.error('获取历史记录失败:', error)
  }
}

// 加载历史会话到当前对话
const loadHistoryQuestion = async (session: any) => {
  try {
    // 获取会话详情
    const sessionDetail = await qaStore.fetchSessionDetail(session.id)

    // 设置当前会话ID
    currentSessionId.value = session.id

    // 清空当前对话
    messages.value = []

    // 加载会话中的所有消息
    sessionDetail.messages.forEach((message, index) => {
      messages.value.push({
        id: message.id,
        type: message.role,
        content: message.content,
        timestamp: new Date(message.created_at),
        loading: false
      })
    })

    // 关闭历史记录面板
    showHistory.value = false

    // 滚动到底部
    await nextTick()
    scrollToBottom()

  } catch (error) {
    console.error('加载历史会话失败:', error)
  }
}

// 历史记录分页处理
const handleHistoryPageChange = (page: number) => {
  historyPage.value = page
  fetchHistoryQuestions()
}

// 格式化历史记录时间
const formatHistoryTime = (dateString: string) => {
  const date = new Date(dateString)
  const now = new Date()
  const diff = now.getTime() - date.getTime()
  const days = Math.floor(diff / (1000 * 60 * 60 * 24))

  if (days === 0) {
    return date.toLocaleTimeString('zh-CN', {
      hour: '2-digit',
      minute: '2-digit'
    })
  } else if (days === 1) {
    return '昨天'
  } else if (days < 7) {
    return `${days}天前`
  } else {
    return date.toLocaleDateString('zh-CN', {
      month: 'short',
      day: 'numeric'
    })
  }
}

// 复制答案
const copyAnswer = async (content: string) => {
  try {
    await navigator.clipboard.writeText(content)
    ElMessage.success('已复制到剪贴板')
  } catch (error) {
    ElMessage.error('复制失败')
  }
}

// 滚动到底部
const scrollToBottom = () => {
  if (messagesContainer.value) {
    messagesContainer.value.scrollTop = messagesContainer.value.scrollHeight
  }
}

// 格式化时间
const formatTime = (date: Date) => {
  return date.toLocaleTimeString('zh-CN', {
    hour: '2-digit',
    minute: '2-digit'
  })
}

// 调整页面高度以适应视口
const adjustHeight = () => {
  const chatElement = document.querySelector('.qa-chat') as HTMLElement
  if (chatElement) {
    // 计算实际可用高度
    const viewportHeight = window.innerHeight
    const navHeight = 60 // 导航栏高度
    const availableHeight = viewportHeight - navHeight
    chatElement.style.height = `${availableHeight}px`
  }
}

// 页面加载时调整高度并滚动到底部
onMounted(() => {
  adjustHeight()
  scrollToBottom()

  // 监听窗口大小变化
  window.addEventListener('resize', adjustHeight)
})

// 组件卸载时清理事件监听器
onUnmounted(() => {
  window.removeEventListener('resize', adjustHeight)
})
</script>

<style scoped>
.qa-chat {
  display: flex;
  flex-direction: column;
  height: calc(100vh - 60px); /* 减去顶部导航栏高度 */
  background: #f5f7fa;
  position: relative;
}

.chat-header {
  background: white;
  padding: 20px 24px;
  border-bottom: 1px solid #e4e7ed;
  display: flex;
  justify-content: space-between;
  align-items: center;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
  flex-shrink: 0;
}

.history-panel {
  background: white;
  border-bottom: 1px solid #e4e7ed;
  max-height: 300px;
  overflow: hidden;
  display: flex;
  flex-direction: column;
  flex-shrink: 0;
}

.history-header {
  padding: 16px 24px;
  border-bottom: 1px solid #f0f0f0;
  display: flex;
  justify-content: space-between;
  align-items: center;
  background: #fafafa;
}

.history-header h3 {
  margin: 0;
  color: #303133;
  font-size: 16px;
  font-weight: 500;
}

.history-content {
  flex: 1;
  overflow-y: auto;
  min-height: 0;
}

.history-loading {
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 40px;
  color: #606266;
  gap: 8px;
}

.history-empty {
  padding: 20px;
}

.history-list {
  padding: 0;
}

.history-item {
  padding: 16px 24px;
  border-bottom: 1px solid #f0f0f0;
  cursor: pointer;
  transition: background-color 0.2s;
}

.history-item:hover {
  background: #f8f9fa;
}

.history-item:last-child {
  border-bottom: none;
}

.history-item-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 8px;
}

.history-subject {
  background: #e1f3ff;
  color: #409eff;
  padding: 2px 8px;
  border-radius: 12px;
  font-size: 12px;
  font-weight: 500;
}

.history-time {
  color: #909399;
  font-size: 12px;
}

.history-question {
  color: #303133;
  font-weight: 500;
  margin-bottom: 6px;
  line-height: 1.4;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
}

.history-answer {
  color: #606266;
  font-size: 13px;
  line-height: 1.4;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
}

.history-pagination {
  padding: 16px;
  display: flex;
  justify-content: center;
  border-top: 1px solid #f0f0f0;
  background: #fafafa;
}

.header-info {
  display: flex;
  align-items: center;
  gap: 16px;
}

.ai-icon {
  font-size: 32px;
  color: #409eff;
}

.title-info h1 {
  margin: 0 0 4px 0;
  color: #303133;
  font-size: 20px;
  font-weight: 500;
}

.title-info p {
  margin: 0;
  color: #909399;
  font-size: 14px;
}

.chat-messages {
  flex: 1;
  overflow-y: auto;
  padding: 24px;
  padding-bottom: 0; /* 移除底部padding，避免与输入框重叠 */
  display: flex;
  flex-direction: column;
  gap: 16px;
  min-height: 0; /* 确保flex子元素可以收缩 */
}

.welcome-message {
  display: flex;
  align-items: flex-start;
  gap: 12px;
  max-width: 600px;
}

.ai-avatar {
  width: 40px;
  height: 40px;
  border-radius: 50%;
  background: linear-gradient(135deg, #409eff, #67c23a);
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
  font-size: 20px;
  flex-shrink: 0;
}

.user-avatar {
  width: 40px;
  height: 40px;
  border-radius: 50%;
  background: linear-gradient(135deg, #e6a23c, #f56c6c);
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
  font-size: 20px;
  flex-shrink: 0;
}

.welcome-content {
  background: white;
  padding: 20px;
  border-radius: 12px;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.1);
}

.welcome-content h3 {
  margin: 0 0 12px 0;
  color: #303133;
  font-size: 16px;
}

.welcome-content p {
  margin: 8px 0;
  color: #606266;
  line-height: 1.6;
}

.welcome-content ul {
  margin: 12px 0;
  padding-left: 20px;
  color: #606266;
}

.welcome-content li {
  margin: 4px 0;
}

.message-item {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.message {
  display: flex;
  align-items: flex-start;
  gap: 12px;
  max-width: 70%;
}

.user-message {
  align-self: flex-end;
  flex-direction: row-reverse;
}

.ai-message {
  align-self: flex-start;
}

.message-content {
  flex: 1;
}

.message-bubble {
  padding: 16px;
  border-radius: 12px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
  word-wrap: break-word;
}

.user-bubble {
  background: linear-gradient(135deg, #409eff, #67c23a);
  color: white;
}

.ai-bubble {
  background: white;
  color: #303133;
  border: 1px solid #e4e7ed;
}

.message-bubble p {
  margin: 0 0 8px 0;
  line-height: 1.6;
}

.message-bubble p:last-child {
  margin-bottom: 0;
}

.ai-answer {
  line-height: 1.6;
}

.ai-answer :deep(.markdown-content) {
  margin: 0;
}

.message-meta {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-top: 8px;
  font-size: 12px;
}

.user-bubble .message-meta {
  color: rgba(255, 255, 255, 0.8);
}

.ai-bubble .message-meta {
  color: #909399;
}

.subject-tag {
  background: rgba(255, 255, 255, 0.2);
  padding: 2px 8px;
  border-radius: 12px;
  font-size: 11px;
}

.time {
  opacity: 0.8;
}

.loading-dots {
  display: flex;
  gap: 4px;
  padding: 8px 0;
}

.loading-dots span {
  width: 8px;
  height: 8px;
  border-radius: 50%;
  background: #409eff;
  animation: loading 1.4s infinite ease-in-out;
}

.loading-dots span:nth-child(1) {
  animation-delay: -0.32s;
}

.loading-dots span:nth-child(2) {
  animation-delay: -0.16s;
}

@keyframes loading {
  0%, 80%, 100% {
    transform: scale(0);
    opacity: 0.5;
  }
  40% {
    transform: scale(1);
    opacity: 1;
  }
}

.chat-input {
  background: white;
  padding: 16px 24px;
  border-top: 1px solid #e4e7ed;
  box-shadow: 0 -2px 8px rgba(0, 0, 0, 0.1);
  flex-shrink: 0; /* 防止输入框被压缩 */
  position: relative;
  z-index: 10;
}

.input-container {
  display: flex;
  align-items: flex-end;
  gap: 12px;
  margin-bottom: 8px;
}

.subject-selector {
  flex-shrink: 0;
}

.input-wrapper {
  flex: 1;
}

.send-button {
  flex-shrink: 0;
  height: 40px;
}

.input-tips {
  text-align: center;
  color: #909399;
  font-size: 12px;
}

/* 滚动条样式 */
.chat-messages::-webkit-scrollbar {
  width: 6px;
}

.chat-messages::-webkit-scrollbar-track {
  background: #f1f1f1;
  border-radius: 3px;
}

.chat-messages::-webkit-scrollbar-thumb {
  background: #c1c1c1;
  border-radius: 3px;
}

.chat-messages::-webkit-scrollbar-thumb:hover {
  background: #a8a8a8;
}

/* 响应式设计 */
@media (max-width: 768px) {
  .qa-chat {
    height: calc(100vh - 50px); /* 移动端导航栏可能更小 */
  }

  .chat-header {
    padding: 16px;
    flex-direction: column;
    gap: 12px;
    align-items: flex-start;
  }

  .history-panel {
    max-height: 250px;
  }

  .history-header {
    padding: 12px 16px;
    flex-direction: column;
    gap: 8px;
    align-items: flex-start;
  }

  .history-item {
    padding: 12px 16px;
  }

  .chat-messages {
    padding: 16px;
    padding-bottom: 0;
  }

  .message {
    max-width: 85%;
  }

  .input-container {
    flex-direction: column;
    align-items: stretch;
    gap: 8px;
  }

  .subject-selector {
    align-self: flex-start;
  }

  .chat-input {
    padding: 12px 16px;
  }
}

/* 确保在小屏幕上也能正常显示 */
@media (max-height: 600px) {
  .qa-chat {
    height: calc(100vh - 40px);
  }

  .chat-header {
    padding: 12px 16px;
  }

  .chat-messages {
    padding: 12px 16px;
    padding-bottom: 0;
  }

  .welcome-content {
    padding: 16px;
  }

  .message-bubble {
    padding: 12px;
  }
}

/* 修复可能的滚动问题 */
.qa-chat {
  overflow: hidden;
}

.chat-messages {
  overflow-x: hidden;
  overflow-y: auto;
}
</style>
