import request from '@/utils/request'
import type { 
  Assignment, 
  CreateAssignmentRequest, 
  SubmitAssignmentRequest,
  Submission,
  ApiResponse,
  PaginatedResponse 
} from '@/types'

/**
 * 作业管理相关API
 */
export const assignmentsApi = {
  /**
   * 创建作业（教师）
   */
  createAssignment(data: CreateAssignmentRequest): Promise<ApiResponse<{ assignment_id: string; title: string; created_at: string }>> {
    return request.post('/assignments/create/', data)
  },

  /**
   * 获取作业列表
   */
  getAssignments(params?: {
    page?: number
    page_size?: number
    subject?: string
    status?: string
    completion_status?: string
  }): Promise<ApiResponse<{
    assignments: Assignment[]
    pagination: {
      page: number
      page_size: number
      total: number
      total_pages: number
    }
  }>> {
    return request.get('/assignments/list/', { params })
  },

  /**
   * 获取作业详情
   */
  getAssignmentDetail(assignmentId: string): Promise<ApiResponse<Assignment & { questions: any[] }>> {
    return request.get(`/assignments/${assignmentId}/`)
  },

  /**
   * 更新作业（教师）
   */
  updateAssignment(assignmentId: string, data: Partial<CreateAssignmentRequest>): Promise<ApiResponse<Assignment>> {
    return request.put(`/assignments/${assignmentId}/`, data)
  },

  /**
   * 删除作业（教师）
   */
  deleteAssignment(assignmentId: string): Promise<ApiResponse<null>> {
    return request.delete(`/assignments/${assignmentId}/`)
  },

  /**
   * 提交作业（学生）
   */
  submitAssignment(assignmentId: string, data: SubmitAssignmentRequest): Promise<ApiResponse<{ submission_id: string; status: string; submitted_at: string }>> {
    return request.post(`/assignments/${assignmentId}/submissions/`, data)
  },

  /**
   * 获取作业提交列表（教师查看所有提交，学生查看自己的提交）
   */
  getSubmissions(assignmentId: string, params?: {
    page?: number
    page_size?: number
    student?: string
  }): Promise<ApiResponse<{
    submissions: Array<{
      id: string
      student_id: string
      student_name: string
      student_username: string
      status: string
      obtained_score: number
      total_score: number
      submitted_at: string
      graded_at?: string
    }>
    pagination: {
      page: number
      page_size: number
      total: number
      total_pages: number
    }
    assignment_info: {
      id: string
      title: string
      total_score: number
      deadline: string
      submission_count: number
    }
  }>> {
    return request.get(`/assignments/${assignmentId}/submissions/list/`, { params })
  },

  /**
   * 获取作业批改结果（新接口）
   */
  getAssignmentResult(assignmentId: string, studentId?: string): Promise<ApiResponse<Submission>> {
    const params = studentId ? { student_id: studentId } : {}
    return request.get(`/assignments/${assignmentId}/result/`, { params })
  },

  /**
   * 获取作业批改结果（旧接口，保持兼容）
   */
  getSubmissionResult(assignmentId: string, submissionId: string): Promise<ApiResponse<Submission>> {
    return request.get(`/assignments/${assignmentId}/submissions/${submissionId}/`)
  },

  /**
   * 重新批改作业（教师）
   */
  regradeSubmission(assignmentId: string, submissionId: string): Promise<ApiResponse<{ message: string }>> {
    return request.post(`/assignments/${assignmentId}/submissions/${submissionId}/regrade/`)
  }
}
