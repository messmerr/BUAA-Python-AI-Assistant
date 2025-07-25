import request from '@/utils/request'
import type { ApiResponse } from '@/types'

// 学习报告相关类型定义
export interface LearningReport {
  id: string
  student_name: string
  student_id_number: string
  generated_by_name: string
  period: 'week' | 'month' | 'semester' | 'all'
  period_display: string
  subjects: string[]
  status: 'generating' | 'completed' | 'failed'
  status_display: string
  total_assignments: number
  completed_assignments: number
  average_score: number
  total_questions: number
  report_content: string
  created_at: string
  updated_at: string
}

export interface LearningReportListItem {
  id: string
  student_name: string
  generated_by_name: string
  period: string
  period_display: string
  subjects: string[]
  status: string
  status_display: string
  total_assignments: number
  completed_assignments: number
  average_score: number
  total_questions: number
  created_at: string
  updated_at: string
}

export interface GenerateReportRequest {
  student_id?: string  // 教师生成报告时必填
  period: 'week' | 'month' | 'semester' | 'all'
  subjects?: string[]  // 可选，为空则包含所有科目
}

export interface GenerateReportResponse {
  report_id: string
  status: string
  created_at: string
}

/**
 * 学习报告相关API
 */
export const reportsApi = {
  /**
   * 生成学习报告
   */
  generateReport(data: GenerateReportRequest): Promise<ApiResponse<GenerateReportResponse>> {
    return request.post('/reports/generate/', data)
  },

  /**
   * 获取报告列表
   */
  getReports(params?: {
    page?: number
    page_size?: number
    status?: string
    period?: string
  }): Promise<ApiResponse<{
    reports: LearningReportListItem[]
    pagination: {
      page: number
      page_size: number
      total: number
      total_pages: number
    }
  }>> {
    return request.get('/reports/list/', { params })
  },

  /**
   * 获取报告详情
   */
  getReportDetail(reportId: string): Promise<ApiResponse<LearningReport>> {
    return request.get(`/reports/${reportId}/`)
  }
}
