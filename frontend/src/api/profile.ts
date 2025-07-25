import request from '@/utils/request'
import type { ApiResponse } from '@/types'

// 用户信息类型定义
export interface UserProfile {
  id: string
  username: string
  email: string
  role: 'student' | 'teacher'
  real_name: string
  student_id?: string
  created_at: string
}

export interface UpdateProfileRequest {
  email?: string
  real_name?: string
  current_password?: string
  new_password?: string
  confirm_password?: string
}

/**
 * 个人中心相关API
 */
export const profileApi = {
  /**
   * 获取个人信息
   */
  getProfile(): Promise<ApiResponse<UserProfile>> {
    return request.get('/auth/profile/')
  },

  /**
   * 更新个人信息
   */
  updateProfile(data: UpdateProfileRequest): Promise<ApiResponse<UserProfile>> {
    return request.put('/auth/profile/', data)
  }
}
