import request from '@/utils/request'
import type {
  QAQuestion,
  CreateQuestionRequest,
  ApiResponse
} from '@/types'

// 新的类型定义
export interface ChatSession {
  id: string
  subject: string
  created_at: string
  updated_at: string
  last_message?: {
    role: 'user' | 'ai'
    content: string
    created_at: string
  }
  message_count: number
}

export interface ChatMessage {
  id: string
  role: 'user' | 'ai'
  content: string
  created_at: string
}

export interface ChatSessionDetail {
  id: string
  subject: string
  created_at: string
  updated_at: string
  messages: ChatMessage[]
}

export interface ChatMessageRequest {
  session_id?: string
  message: string
  subject?: string
}

/**
 * 智能答疑相关API
 */
export const qaApi = {
  /**
   * 发送聊天消息（新接口）
   */
  sendChatMessage(data: ChatMessageRequest): Promise<ApiResponse<{
    session_id: string
    ai_response: string
    created_at: string
  }>> {
    return request.post('/qa/chat/', data)
  },

  /**
   * 获取会话列表（新接口）
   */
  getSessions(params?: {
    page?: number
    page_size?: number
    subject?: string
  }): Promise<ApiResponse<{
    sessions: ChatSession[]
    pagination: {
      page: number
      page_size: number
      total: number
      total_pages: number
    }
  }>> {
    return request.get('/qa/sessions/', { params })
  },

  /**
   * 获取会话详情（新接口）
   */
  getSessionDetail(sessionId: string): Promise<ApiResponse<ChatSessionDetail>> {
    return request.get(`/qa/sessions/${sessionId}/`)
  },

  // 保留旧接口以兼容
  /**
   * 提交问题（学生）
   */
  submitQuestion(data: CreateQuestionRequest): Promise<ApiResponse<{ question_id: string; ai_answer: string; created_at: string }>> {
    return request.post('/qa/questions/', data)
  },

  /**
   * 获取问题详情
   */
  getQuestionDetail(questionId: string): Promise<ApiResponse<QAQuestion>> {
    return request.get(`/qa/questions/${questionId}/`)
  },

  /**
   * 获取问题列表
   */
  getQuestions(params?: {
    page?: number
    page_size?: number
    subject?: string
  }): Promise<ApiResponse<{
    questions: QAQuestion[]
    pagination: {
      page: number
      page_size: number
      total: number
      total_pages: number
    }
  }>> {
    return request.get('/qa/questions/list/', { params })
  },

  /**
   * 删除问题（学生删除自己的问题）
   */
  deleteQuestion(questionId: string): Promise<ApiResponse<null>> {
    return request.delete(`/qa/questions/${questionId}/`)
  }
}
