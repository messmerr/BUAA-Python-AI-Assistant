<template>
  <div class="chat-container">
    <!-- 左侧用户列表 -->
    <div class="chat-sidebar">
      <div class="sidebar-header">
        <h3>{{ userRole === 'teacher' ? '学生列表' : '教师列表' }}</h3>
        <el-button @click="fetchUsers" :loading="loading" size="small">
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
          <div>
            <div class="user-name">{{ currentChatUser.real_name || currentChatUser.username }}</div>
            <div class="user-status">{{ currentChatUser.role === 'teacher' ? '教师' : '学生' }}</div>
          </div>
        </div>
      </div>

      <!-- 消息列表 -->
      <div class="messages-container" ref="messagesContainer">
        <div v-if="!currentChatUser" class="no-chat-selected">
          <el-empty description="请选择一个用户开始聊天" />
        </div>
        
        <div v-else-if="messages.length === 0" class="no-messages">
          <el-empty description="暂无消息，开始聊天吧！" />
        </div>

        <div v-else class="messages-list">
          <div 
            v-for="message in messages" 
            :key="message.id"
            class="message-item"
            :class="{ 'own-message': message.sender === currentUserId }"
          >
            <div class="message-content">
              <div class="message-text">{{ message.content }}</div>
              <div class="message-time">
                {{ formatTime(message.created_at) }}
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- 输入区域 -->
      <div class="chat-input" v-if="currentChatUser">
        <div class="input-container">
          <el-input
            v-model="inputMessage"
            type="textarea"
            :rows="3"
            placeholder="输入消息..."
            @keydown.enter.prevent="handleKeyDown"
            :disabled="loading"
          />
          <el-button 
            type="primary" 
            @click="handleSendMessage"
            :loading="loading"
            :disabled="!inputMessage.trim()"
          >
            发送
          </el-button>
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
import { Refresh } from '@element-plus/icons-vue'

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
  height: calc(100vh - 120px);
  border: 1px solid #e4e7ed;
  border-radius: 8px;
  overflow: hidden;
}

.chat-sidebar {
  width: 300px;
  border-right: 1px solid #e4e7ed;
  background: #f8f9fa;
}

.sidebar-header {
  padding: 16px;
  border-bottom: 1px solid #e4e7ed;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.user-list {
  height: calc(100% - 60px);
  overflow-y: auto;
}

.user-item {
  padding: 12px 16px;
  display: flex;
  align-items: center;
  cursor: pointer;
  border-bottom: 1px solid #f0f0f0;
}

.user-item:hover {
  background: #e8f4fd;
}

.user-item.active {
  background: #409eff;
  color: white;
}

.user-avatar {
  width: 40px;
  height: 40px;
  border-radius: 50%;
  background: #409eff;
  color: white;
  display: flex;
  align-items: center;
  justify-content: center;
  margin-right: 12px;
  font-weight: bold;
}

.user-info {
  flex: 1;
}

.user-name {
  font-weight: 500;
  margin-bottom: 4px;
}

.user-role {
  font-size: 12px;
  opacity: 0.7;
}

.chat-main {
  flex: 1;
  display: flex;
  flex-direction: column;
}

.chat-header {
  padding: 16px;
  border-bottom: 1px solid #e4e7ed;
  background: white;
}

.chat-user-info {
  display: flex;
  align-items: center;
}

.messages-container {
  flex: 1;
  overflow-y: auto;
  padding: 16px;
}

.messages-list {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.message-item {
  display: flex;
}

.message-item.own-message {
  justify-content: flex-end;
}

.message-content {
  max-width: 70%;
  padding: 8px 12px;
  border-radius: 8px;
  background: #f0f0f0;
}

.own-message .message-content {
  background: #409eff;
  color: white;
}

.message-text {
  margin-bottom: 4px;
}

.message-time {
  font-size: 12px;
  opacity: 0.7;
}

.chat-input {
  padding: 16px;
  border-top: 1px solid #e4e7ed;
  background: white;
}

.input-container {
  display: flex;
  gap: 12px;
  align-items: flex-end;
}

.input-container .el-input {
  flex: 1;
}
</style>

