import request from '@/utils/request'
import type { 
  QAQuestion, 
  CreateQuestionRequest, 
  ApiResponse,
  PaginatedResponse 
} from '@/types'

/**
 * 智能答疑相关API
 */
export const qaApi = {
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
  }): Promise<ApiResponse<PaginatedResponse<QAQuestion>>> {
    return request.get('/qa/questions/', { params })
  },

  /**
   * 删除问题（学生删除自己的问题）
   */
  deleteQuestion(questionId: string): Promise<ApiResponse<null>> {
    return request.delete(`/qa/questions/${questionId}/`)
  }
}
