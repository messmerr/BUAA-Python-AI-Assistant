import request from '@/utils/request'
import type { 
  LoginRequest, 
  RegisterRequest, 
  LoginResponse, 
  User, 
  ApiResponse 
} from '@/types'

/**
 * 用户认证相关API
 */
export const authApi = {
  /**
   * 用户登录
   */
  login(data: LoginRequest): Promise<ApiResponse<LoginResponse>> {
    return request.post('/auth/login/', data)
  },

  /**
   * 用户注册
   */
  register(data: RegisterRequest): Promise<ApiResponse<{ user_id: string; username: string; role: string }>> {
    return request.post('/auth/register/', data)
  },

  /**
   * 刷新Token
   */
  refreshToken(refreshToken: string): Promise<ApiResponse<{ access: string }>> {
    return request.post('/auth/refresh/', { refresh: refreshToken })
  },

  /**
   * 获取当前用户信息
   */
  getProfile(): Promise<ApiResponse<User>> {
    return request.get('/auth/profile/')
  },

  /**
   * 更新用户信息
   */
  updateProfile(data: Partial<User>): Promise<ApiResponse<User>> {
    return request.put('/auth/profile/', data)
  },

  /**
   * 退出登录
   */
  logout(): Promise<void> {
    // 清除本地存储的token
    localStorage.removeItem('access_token')
    localStorage.removeItem('refresh_token')
    localStorage.removeItem('user_info')
    return Promise.resolve()
  }
}
