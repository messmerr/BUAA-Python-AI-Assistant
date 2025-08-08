<template>
  <div class="chat-container">
    <!-- 左侧用户列表 -->
    <div class="chat-sidebar">
      <div class="sidebar-header">
        <div class="header-info">
          <el-icon class="chat-icon"><ChatDotRound /></el-icon>
          <div class="title-info">
            <h3>{{ userRole === 'teacher' ? '学生列表' : '教师列表' }}</h3>
            <p>选择用户开始对话</p>
          </div>
        </div>
        <el-button @click="fetchUsers" :loading="loading" size="small" circle>
          <el-icon><Refresh /></el-icon>
        </el-button>
      </div>
      
      <div class="user-list">
        <div 
          v-for="user in chatUsers" 
          :key="user.id"
          class="user-item"
          :class="{ active: currentChatUser?.id === user.id }"
          @click="selectUser(user)"
        >
          <div class="user-avatar">
            {{ user.real_name?.charAt(0) || user.username.charAt(0) }}
          </div>
          <div class="user-info">
            <div class="user-name">{{ user.real_name || user.username }}</div>
            <div class="user-role">{{ user.role === 'teacher' ? '教师' : '学生' }}</div>
          </div>
          <el-badge v-if="user.unread_count > 0" :value="user.unread_count" />
        </div>
      </div>
    </div>

    <!-- 右侧聊天区域 -->
    <div class="chat-main">
      <!-- 聊天头部 -->
      <div class="chat-header" v-if="currentChatUser">
        <div class="chat-user-info">
          <div class="user-avatar">
            {{ currentChatUser.real_name?.charAt(0) || currentChatUser.username.charAt(0) }}
          </div>
          <div class="user-details">
            <div class="user-name">{{ currentChatUser.real_name || currentChatUser.username }}</div>
            <div class="user-status">{{ currentChatUser.role === 'teacher' ? '教师' : '学生' }}</div>
          </div>
        </div>
      </div>

      <!-- 消息列表 -->
      <div class="messages-container" ref="messagesContainer">
        <div v-if="!currentChatUser" class="welcome-message">
          <div class="welcome-icon">
            <el-icon><ChatDotRound /></el-icon>
          </div>
          <div class="welcome-content">
            <h3>👋 欢迎使用师生交流</h3>
            <p>请从左侧选择一个用户开始聊天</p>
            <ul>
              <li>💬 实时沟通交流</li>
              <li>📚 学习问题讨论</li>
              <li>📝 作业指导答疑</li>
              <li>🎯 个性化学习建议</li>
            </ul>
          </div>
        </div>
        
        <div v-else-if="messages.length === 0" class="welcome-message">
          <div class="welcome-icon">
            <el-icon><ChatDotRound /></el-icon>
          </div>
          <div class="welcome-content">
            <h3>开始新的对话</h3>
            <p>与 {{ currentChatUser.real_name || currentChatUser.username }} 的聊天</p>
            <p>快来发送第一条消息吧！</p>
          </div>
        </div>

        <div v-else class="messages-list">
          <div 
            v-for="message in messages" 
            :key="message.id"
            class="message-wrapper"
          >
            <div 
              class="message-item"
              :class="{ 'own-message': message.sender === currentUserId }"
            >
              <!-- 对方消息的头像 -->
              <div 
                v-if="message.sender !== currentUserId"
                class="message-avatar"
              >
                {{ currentChatUser.real_name?.charAt(0) || currentChatUser.username.charAt(0) }}
              </div>
              
              <div class="message-content">
                <div class="message-bubble" :class="{
                  'user-bubble': message.sender === currentUserId,
                  'other-bubble': message.sender !== currentUserId
                }">
                  <div class="message-text">{{ message.content }}</div>
                  <div class="message-time">
                    {{ formatTime(message.created_at) }}
                  </div>
                </div>
              </div>

              <!-- 自己消息的头像 -->
              <div 
                v-if="message.sender === currentUserId"
                class="message-avatar user-avatar"
              >
                {{ authStore.user?.real_name?.charAt(0) || authStore.user?.username?.charAt(0) }}
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- 输入区域 -->
      <div class="chat-input" v-if="currentChatUser">
        <div class="input-container">
          <div class="input-wrapper">
            <el-input
              v-model="inputMessage"
              type="textarea"
              :rows="1"
              :autosize="{ minRows: 1, maxRows: 4 }"
              placeholder="输入消息..."
              @keydown.enter.exact.prevent="handleSendMessage"
              @keydown.enter.shift.exact="handleShiftEnter"
              :disabled="loading"
            />
          </div>
          <el-button 
            type="primary" 
            @click="handleSendMessage"
            :loading="loading"
            :disabled="!inputMessage.trim()"
            class="send-button"
          >
            <el-icon v-if="!loading"><Promotion /></el-icon>
            {{ loading ? '发送中...' : '发送' }}
          </el-button>
        </div>
        <div class="input-tips">
          <span>按 Enter 发送，Shift + Enter 换行</span>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, nextTick } from 'vue'
import { useChatStore } from '@/stores/chat'
import { useAuthStore } from '@/stores/auth'
import { ElMessage } from 'element-plus'
import { Refresh, ChatDotRound, Promotion } from '@element-plus/icons-vue'

const chatStore = useChatStore()
const authStore = useAuthStore()

// 响应式数据
const inputMessage = ref('')
const messagesContainer = ref<HTMLElement>()

// 计算属性
const chatUsers = computed(() => chatStore.chatUsers)
const currentChatUser = computed(() => chatStore.currentChatUser)
const messages = computed(() => chatStore.messages)
const loading = computed(() => chatStore.loading)
const currentUserId = computed(() => authStore.user?.id)
const userRole = computed(() => authStore.user?.role)

// 方法
const fetchUsers = async () => {
  await chatStore.fetchChatUsers()
  // 切换账号后，如果当前选中对象是自己或不在列表中，则清空
  const selected = chatStore.currentChatUser
  const meId = authStore.user?.id
  if (selected && (selected.id === meId || !chatStore.chatUsers.some(u => u.id === selected.id))) {
    chatStore.setCurrentChatUser(null)
  }
}

const selectUser = async (user: any) => {
  chatStore.setCurrentChatUser(user)
  await chatStore.fetchChatMessages(user.id)
  await chatStore.markAsRead(user.id)
  await nextTick()
  scrollToBottom()
}

const handleKeyDown = (event: KeyboardEvent) => {
  if (event.key === 'Enter' && !event.shiftKey && !event.ctrlKey) {
    event.preventDefault()
    handleSendMessage()
  }
}

const handleShiftEnter = () => {
  // 允许默认行为（换行）
}

const handleSendMessage = async () => {
  if (!inputMessage.value.trim() || !currentChatUser.value || loading.value) {
    return
  }

  const content = inputMessage.value.trim()
  inputMessage.value = ''

  try {
    await chatStore.sendMessage(currentChatUser.value.id, content)
    await nextTick()
    scrollToBottom()
  } catch (error) {
    inputMessage.value = content
  }
}

const scrollToBottom = () => {
  if (messagesContainer.value) {
    messagesContainer.value.scrollTop = messagesContainer.value.scrollHeight
  }
}

const formatTime = (time: string) => {
  return new Date(time).toLocaleTimeString('zh-CN', {
    hour: '2-digit',
    minute: '2-digit'
  })
}

// 生命周期
onMounted(() => {
  fetchUsers()
})
</script>

<style scoped>
.chat-container {
  display: flex;
  height: calc(100vh - 60px);
  background: #f5f7fa;
  overflow: hidden;
}

.chat-sidebar {
  width: 320px;
  background: white;
  border-right: 1px solid #e4e7ed;
  box-shadow: 2px 0 8px rgba(0, 0, 0, 0.1);
  display: flex;
  flex-direction: column;
}

.sidebar-header {
  padding: 20px 24px;
  border-bottom: 1px solid #e4e7ed;
  display: flex;
  justify-content: space-between;
  align-items: center;
  background: white;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.05);
}

.header-info {
  display: flex;
  align-items: center;
  gap: 12px;
}

.chat-icon {
  font-size: 28px;
  color: #409eff;
}

.title-info h3 {
  margin: 0 0 4px 0;
  color: #303133;
  font-size: 16px;
  font-weight: 500;
}

.title-info p {
  margin: 0;
  color: #909399;
  font-size: 12px;
}

.user-list {
  flex: 1;
  overflow-y: auto;
  padding: 8px 0;
}

.user-item {
  padding: 16px 20px;
  display: flex;
  align-items: center;
  cursor: pointer;
  transition: all 0.2s;
  position: relative;
}

.user-item:hover {
  background: #f0f9ff;
}

.user-item.active {
  background: linear-gradient(135deg, #409eff, #67c23a);
  color: white;
}

.user-item.active .user-role {
  color: rgba(255, 255, 255, 0.8);
}

.user-avatar {
  width: 44px;
  height: 44px;
  border-radius: 50%;
  background: linear-gradient(135deg, #e6a23c, #f56c6c);
  color: white;
  display: flex;
  align-items: center;
  justify-content: center;
  margin-right: 12px;
  font-weight: 500;
  font-size: 16px;
  flex-shrink: 0;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.15);
}

.user-item.active .user-avatar {
  background: rgba(255, 255, 255, 0.2);
  backdrop-filter: blur(10px);
}

.user-info {
  flex: 1;
  min-width: 0;
}

.user-name {
  font-weight: 500;
  margin-bottom: 4px;
  color: #303133;
  font-size: 14px;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.user-item.active .user-name {
  color: white;
}

.user-role {
  font-size: 12px;
  color: #909399;
  font-weight: 400;
}

.chat-main {
  flex: 1;
  display: flex;
  flex-direction: column;
  min-width: 0;
}

.chat-header {
  padding: 20px 24px;
  border-bottom: 1px solid #e4e7ed;
  background: white;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.05);
  flex-shrink: 0;
}

.chat-user-info {
  display: flex;
  align-items: center;
  gap: 12px;
}

.chat-user-info .user-avatar {
  margin-right: 0;
  background: linear-gradient(135deg, #409eff, #67c23a);
}

.user-details .user-name {
  color: #303133;
  font-size: 16px;
  font-weight: 500;
  margin-bottom: 4px;
}

.user-details .user-status {
  color: #909399;
  font-size: 12px;
}

.messages-container {
  flex: 1;
  overflow-y: auto;
  padding: 24px;
  display: flex;
  flex-direction: column;
  gap: 16px;
  min-height: 0;
}

.welcome-message {
  display: flex;
  align-items: flex-start;
  gap: 12px;
  max-width: 600px;
  margin: auto;
}

.welcome-icon {
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
  line-height: 1.5;
}

.messages-list {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.message-wrapper {
  display: flex;
  flex-direction: column;
}

.message-item {
  display: flex;
  align-items: flex-start;
  gap: 12px;
  max-width: 70%;
}

.message-item.own-message {
  align-self: flex-end;
  flex-direction: row-reverse;
}

.message-avatar {
  width: 36px;
  height: 36px;
  border-radius: 50%;
  background: linear-gradient(135deg, #409eff, #67c23a);
  color: white;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 14px;
  font-weight: 500;
  flex-shrink: 0;
  box-shadow: 0 2px 6px rgba(0, 0, 0, 0.1);
}

.message-avatar.user-avatar {
  background: linear-gradient(135deg, #e6a23c, #f56c6c);
}

.message-content {
  min-width: 0;
}

.message-bubble {
  padding: 12px 16px;
  border-radius: 12px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
  word-wrap: break-word;
  position: relative;
}

.user-bubble {
  background: linear-gradient(135deg, #409eff, #67c23a);
  color: white;
}

.other-bubble {
  background: white;
  color: #303133;
  border: 1px solid #e4e7ed;
}

.message-text {
  line-height: 1.6;
  margin-bottom: 6px;
}

.message-time {
  font-size: 11px;
  opacity: 0.7;
}

.user-bubble .message-time {
  color: rgba(255, 255, 255, 0.8);
}

.other-bubble .message-time {
  color: #909399;
}

.chat-input {
  background: white;
  padding: 16px 24px;
  border-top: 1px solid #e4e7ed;
  box-shadow: 0 -2px 8px rgba(0, 0, 0, 0.05);
  flex-shrink: 0;
}

.input-container {
  display: flex;
  align-items: flex-end;
  gap: 12px;
  margin-bottom: 8px;
}

.input-wrapper {
  flex: 1;
}

.send-button {
  flex-shrink: 0;
  height: 40px;
  min-width: 80px;
}

.input-tips {
  text-align: center;
  color: #909399;
  font-size: 12px;
  margin-top: 4px;
}

/* 滚动条样式 */
.user-list::-webkit-scrollbar,
.messages-container::-webkit-scrollbar {
  width: 6px;
}

.user-list::-webkit-scrollbar-track,
.messages-container::-webkit-scrollbar-track {
  background: #f1f1f1;
  border-radius: 3px;
}

.user-list::-webkit-scrollbar-thumb,
.messages-container::-webkit-scrollbar-thumb {
  background: #c1c1c1;
  border-radius: 3px;
}

.user-list::-webkit-scrollbar-thumb:hover,
.messages-container::-webkit-scrollbar-thumb:hover {
  background: #a8a8a8;
}

/* 响应式设计 */
@media (max-width: 768px) {
  .chat-container {
    height: calc(100vh - 50px);
  }

  .chat-sidebar {
    width: 280px;
  }

  .sidebar-header {
    padding: 16px;
    flex-direction: column;
    gap: 12px;
    align-items: flex-start;
  }

  .user-item {
    padding: 12px 16px;
  }

  .messages-container {
    padding: 16px;
  }

  .message-item {
    max-width: 85%;
  }

  .input-container {
    flex-direction: column;
    align-items: stretch;
    gap: 8px;
  }

  .chat-input {
    padding: 12px 16px;
  }
}

/* 确保在小屏幕上也能正常显示 */
@media (max-height: 600px) {
  .chat-container {
    height: calc(100vh - 40px);
  }

  .sidebar-header {
    padding: 12px 16px;
  }

  .messages-container {
    padding: 12px 16px;
  }

  .welcome-content {
    padding: 16px;
  }

  .message-bubble {
    padding: 10px 12px;
  }
}
</style>

