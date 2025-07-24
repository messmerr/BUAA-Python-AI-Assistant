import { ref, computed } from 'vue'
import { defineStore } from 'pinia'
import { authApi } from '@/api'
import type { User, LoginRequest, RegisterRequest } from '@/types'
import { ElMessage } from 'element-plus'

export const useAuthStore = defineStore('auth', () => {
  // 状态
  const user = ref<User | null>(null)
  const accessToken = ref<string | null>(localStorage.getItem('access_token'))
  const refreshToken = ref<string | null>(localStorage.getItem('refresh_token'))
  const loading = ref(false)

  // 计算属性
  const isAuthenticated = computed(() => !!accessToken.value && !!user.value)
  const isTeacher = computed(() => user.value?.role === 'teacher')
  const isStudent = computed(() => user.value?.role === 'student')

  // 初始化用户信息
  const initUser = async () => {
    if (accessToken.value && !user.value) {
      try {
        await getUserProfile()
      } catch (error) {
        console.error('获取用户信息失败:', error)
        logout()
      }
    }
  }

  // 登录
  const login = async (loginData: LoginRequest) => {
    loading.value = true
    try {
      const response = await authApi.login(loginData)
      const { access_token, refresh_token, user: userInfo } = response.data
      
      // 保存token和用户信息
      accessToken.value = access_token
      refreshToken.value = refresh_token
      user.value = userInfo
      
      localStorage.setItem('access_token', access_token)
      localStorage.setItem('refresh_token', refresh_token)
      localStorage.setItem('user_info', JSON.stringify(userInfo))
      
      ElMessage.success('登录成功')
      return true
    } catch (error) {
      console.error('登录失败:', error)
      return false
    } finally {
      loading.value = false
    }
  }

  // 注册
  const register = async (registerData: RegisterRequest) => {
    loading.value = true
    try {
      await authApi.register(registerData)
      ElMessage.success('注册成功，请登录')
      return true
    } catch (error) {
      console.error('注册失败:', error)
      return false
    } finally {
      loading.value = false
    }
  }

  // 获取用户信息
  const getUserProfile = async () => {
    try {
      const response = await authApi.getProfile()
      user.value = response.data
      localStorage.setItem('user_info', JSON.stringify(response.data))
    } catch (error) {
      console.error('获取用户信息失败:', error)
      throw error
    }
  }

  // 更新用户信息
  const updateProfile = async (userData: Partial<User>) => {
    loading.value = true
    try {
      const response = await authApi.updateProfile(userData)
      user.value = response.data
      localStorage.setItem('user_info', JSON.stringify(response.data))
      ElMessage.success('更新成功')
      return true
    } catch (error) {
      console.error('更新用户信息失败:', error)
      return false
    } finally {
      loading.value = false
    }
  }

  // 退出登录
  const logout = async () => {
    try {
      await authApi.logout()
    } catch (error) {
      console.error('退出登录失败:', error)
    } finally {
      // 清除状态
      user.value = null
      accessToken.value = null
      refreshToken.value = null
      
      // 清除本地存储
      localStorage.removeItem('access_token')
      localStorage.removeItem('refresh_token')
      localStorage.removeItem('user_info')
      
      ElMessage.success('已退出登录')
    }
  }

  // 刷新token
  const refreshAccessToken = async () => {
    if (!refreshToken.value) {
      logout()
      return false
    }

    try {
      const response = await authApi.refreshToken(refreshToken.value)
      accessToken.value = response.data.access
      localStorage.setItem('access_token', response.data.access)
      return true
    } catch (error) {
      console.error('刷新token失败:', error)
      logout()
      return false
    }
  }

  return {
    // 状态
    user,
    accessToken,
    refreshToken,
    loading,
    
    // 计算属性
    isAuthenticated,
    isTeacher,
    isStudent,
    
    // 方法
    initUser,
    login,
    register,
    getUserProfile,
    updateProfile,
    logout,
    refreshAccessToken
  }
})
