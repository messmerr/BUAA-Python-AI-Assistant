import request from '@/utils/request'
import type { ApiResponse } from '@/types'

export interface ChatUser {
  id: string
  username: string
  real_name: string
  role: 'teacher' | 'student'
  avatar?: string
  last_message?: {
    content: string
    created_at: string
    is_read: boolean
  }
  unread_count: number
}

export interface ChatMessage {
  id: string
  sender_id: string
  receiver_id: string
  content: string
  is_read: boolean
  created_at: string
}

export interface SendMessageRequest {
  receiver_id: string
  content: string
}

export const chatApi = {
  // 获取可聊天的用户列表
  getChatUsers(): Promise<ApiResponse<ChatUser[]>> {
    return request.get('/chat/users/')
  },

  // 获取与某用户的聊天记录
  getChatMessages(userId: string, params?: {
    page?: number
    page_size?: number
  }): Promise<ApiResponse<{
    messages: ChatMessage[]
    pagination: {
      page: number
      page_size: number
      total: number
      total_pages: number
    }
  }>> {
    return request.get(`/chat/messages/${userId}/`, { params })
  },

  // 发送消息
  sendMessage(data: SendMessageRequest): Promise<ApiResponse<ChatMessage>> {
    return request.post('/chat/messages/', data)
  },

  // 标记消息为已读
  markAsRead(userId: string): Promise<ApiResponse<void>> {
    return request.post(`/chat/messages/${userId}/read/`)
  },

  // 获取未读消息数量
  getUnreadCount(): Promise<ApiResponse<{ total_unread: number }>> {
    return request.get('/chat/unread-count/')
  }
}