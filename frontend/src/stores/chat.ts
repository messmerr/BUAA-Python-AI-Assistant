import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { chatApi, type ChatUser, type ChatMessage } from '@/api/chat'
import { ElMessage } from 'element-plus'

export const useChatStore = defineStore('chat', () => {
  // 状态
  const chatUsers = ref<ChatUser[]>([])
  const currentChatUser = ref<ChatUser | null>(null)
  const messages = ref<ChatMessage[]>([])
  const loading = ref(false)
  const totalUnreadCount = ref(0)

  // 计算属性
  const unreadUsers = computed(() => 
    chatUsers.value.filter(user => user.unread_count > 0)
  )

  // 获取可聊天用户列表
  const fetchChatUsers = async () => {
    loading.value = true
    try {
      const response = await chatApi.getChatUsers()
      chatUsers.value = response.data
      // 计算总未读数
      totalUnreadCount.value = chatUsers.value.reduce((sum, user) => sum + user.unread_count, 0)
    } catch (error) {
      console.error('获取聊天用户失败:', error)
      ElMessage.error('获取聊天用户失败')
    } finally {
      loading.value = false
    }
  }

  // 获取聊天记录
  const fetchChatMessages = async (userId: string, page = 1) => {
    loading.value = true
    try {
      const response = await chatApi.getChatMessages(userId, { page, page_size: 50 })
      if (page === 1) {
        messages.value = response.data.messages.reverse()
      } else {
        messages.value = [...response.data.messages.reverse(), ...messages.value]
      }
      return response.data
    } catch (error) {
      console.error('获取聊天记录失败:', error)
      ElMessage.error('获取聊天记录失败')
      throw error
    } finally {
      loading.value = false
    }
  }

  // 发送消息
  const sendMessage = async (receiverId: string, content: string) => {
    console.log('=== 开始发送消息 ===')
    console.log('接收者ID:', receiverId)
    console.log('消息内容:', content)
    console.log('当前loading状态:', loading.value)
    
    if (loading.value) {
      console.log('已在加载中，跳过')
      return
    }
    
    try {
      loading.value = true
      console.log('设置loading为true')
      
      const response = await chatApi.sendMessage({ 
        receiver_id: receiverId, 
        content 
      })
      
      console.log('API响应:', response)
      
      if (response.data) {
        messages.value.push(response.data)
        console.log('消息已添加到列表')
      }
      
      return response.data
    } catch (error) {
      console.error('发送消息失败:', error)
      ElMessage.error('发送消息失败')
      throw error
    } finally {
      loading.value = false
      console.log('设置loading为false')
      console.log('=== 发送消息结束 ===')
    }
  }

  // 标记为已读
  const markAsRead = async (userId: string) => {
    try {
      await chatApi.markAsRead(userId)
      // 更新本地状态
      const user = chatUsers.value.find(u => u.id === userId)
      if (user) {
        totalUnreadCount.value -= user.unread_count
        user.unread_count = 0
      }
    } catch (error) {
      console.error('标记已读失败:', error)
    }
  }

  // 获取未读消息数量
  const fetchUnreadCount = async () => {
    try {
      const response = await chatApi.getUnreadCount()
      totalUnreadCount.value = response.data.total_unread
    } catch (error) {
      console.error('获取未读数量失败:', error)
    }
  }

  // 设置当前聊天用户
  const setCurrentChatUser = (user: ChatUser) => {
    currentChatUser.value = user
    messages.value = []
  }

  return {
    // 状态
    chatUsers,
    currentChatUser,
    messages,
    loading,
    totalUnreadCount,

    // 计算属性
    unreadUsers,

    // 方法
    fetchChatUsers,
    fetchChatMessages,
    sendMessage,
    markAsRead,
    fetchUnreadCount,
    setCurrentChatUser
  }
})
