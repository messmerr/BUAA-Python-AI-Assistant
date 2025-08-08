import axios, { type AxiosInstance, type InternalAxiosRequestConfig, type AxiosResponse } from 'axios'
import { ElMessage } from 'element-plus'

// API基础配置
const BASE_URL = 'http://localhost:8000/api/v1'

// 创建axios实例
const request: AxiosInstance = axios.create({
  baseURL: BASE_URL,
  timeout: 60000, // 增加到60秒，因为AI批改需要较长时间
  headers: {
    'Content-Type': 'application/json',
  },
})

// 请求拦截器
request.interceptors.request.use(
  (config: InternalAxiosRequestConfig) => {
    // 添加认证token
    const token = localStorage.getItem('access_token')
    if (token && config.headers) {
      config.headers.Authorization = `Bearer ${token}`
    }
    return config
  },
  (error) => {
    return Promise.reject(error)
  }
)

// 响应拦截器
request.interceptors.response.use(
  (response: AxiosResponse) => {
    console.log('[DEBUG] 响应拦截器 - 原始数据:', response.data)
    
    const { data } = response
    
    // 如果是标准的API响应格式
    if (data && typeof data === 'object' && data.code !== undefined) {
      console.log('[DEBUG] 响应拦截器 - 检测到标准API格式, code:', data.code)
      if (data.code === 200 || data.code === 201) {
        console.log('[DEBUG] 响应拦截器 - 返回成功数据:', data)
        return data
      } else {
        console.error('[DEBUG] 响应拦截器 - API返回错误:', data)
        ElMessage.error(data.message || '请求失败')
        return Promise.reject(new Error(data.message || '请求失败'))
      }
    }
    
    // 直接返回数据（可能是Django的原始响应）
    console.log('[DEBUG] 响应拦截器 - 非标准格式，包装返回')
    const wrappedData = {
      code: 200,
      data: data,
      message: 'success'
    }
    console.log('[DEBUG] 响应拦截器 - 包装后数据:', wrappedData)
    return wrappedData
  },
  (error) => {
    console.error('[DEBUG] 响应拦截器 - 收到错误响应')
    console.error('[DEBUG] 响应拦截器 - 错误对象:', error)
    console.error('[DEBUG] 响应拦截器 - 错误响应:', error.response)
    console.error('[DEBUG] 响应拦截器 - 错误状态:', error.response?.status)
    console.error('[DEBUG] 响应拦截器 - 错误数据:', error.response?.data)
    
    if (error.response) {
      const { status, data } = error.response
      
      switch (status) {
        case 401:
          ElMessage.error('未授权，请重新登录')
          localStorage.removeItem('access_token')
          localStorage.removeItem('refresh_token')
          window.location.href = '/login'
          break
        case 403:
          ElMessage.error('权限不足')
          break
        case 404:
          ElMessage.error('请求的资源不存在')
          break
        case 500:
          ElMessage.error('服务器内部错误')
          break
        default:
          ElMessage.error(data?.message || `请求失败 (${status})`)
      }
    } else if (error.request) {
      console.error('[DEBUG] 响应拦截器 - 网络错误，无响应')
      ElMessage.error('网络错误，请检查网络连接')
    } else {
      console.error('[DEBUG] 响应拦截器 - 请求配置错误')
      ElMessage.error('请求配置错误')
    }
    
    return Promise.reject(error)
  }
)

export default request


