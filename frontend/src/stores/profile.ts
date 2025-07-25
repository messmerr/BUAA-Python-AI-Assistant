import { ref, computed } from 'vue'
import { defineStore } from 'pinia'
import { profileApi, type UserProfile, type UpdateProfileRequest } from '@/api/profile'
import { ElMessage } from 'element-plus'

export const useProfileStore = defineStore('profile', () => {
  // 状态
  const profile = ref<UserProfile | null>(null)
  const loading = ref(false)
  const updating = ref(false)

  // 计算属性
  const isStudent = computed(() => profile.value?.role === 'student')
  const isTeacher = computed(() => profile.value?.role === 'teacher')
  
  const roleDisplay = computed(() => {
    switch (profile.value?.role) {
      case 'student': return '学生'
      case 'teacher': return '教师'
      default: return '未知'
    }
  })

  // 获取个人信息
  const fetchProfile = async () => {
    loading.value = true
    try {
      const response = await profileApi.getProfile()
      profile.value = response.data
      return response.data
    } catch (error) {
      console.error('获取个人信息失败:', error)
      ElMessage.error('获取个人信息失败')
      throw error
    } finally {
      loading.value = false
    }
  }

  // 更新个人信息
  const updateProfile = async (data: UpdateProfileRequest) => {
    updating.value = true
    try {
      const response = await profileApi.updateProfile(data)
      profile.value = response.data
      
      // 根据更新内容显示不同的成功消息
      if (data.new_password) {
        ElMessage.success('密码修改成功')
      } else {
        ElMessage.success('个人信息更新成功')
      }
      
      return response.data
    } catch (error: any) {
      console.error('更新个人信息失败:', error)
      
      // 处理不同类型的错误
      if (error.response?.data?.errors) {
        const errors = error.response.data.errors
        if (errors.current_password) {
          ElMessage.error('当前密码错误')
        } else if (errors.new_password) {
          ElMessage.error('新密码格式不正确')
        } else if (errors.confirm_password) {
          ElMessage.error('确认密码不匹配')
        } else if (errors.email) {
          ElMessage.error('邮箱格式不正确')
        } else {
          ElMessage.error('更新失败，请检查输入信息')
        }
      } else {
        ElMessage.error('更新个人信息失败')
      }
      throw error
    } finally {
      updating.value = false
    }
  }

  // 清除个人信息
  const clearProfile = () => {
    profile.value = null
  }

  return {
    // 状态
    profile,
    loading,
    updating,
    
    // 计算属性
    isStudent,
    isTeacher,
    roleDisplay,
    
    // 方法
    fetchProfile,
    updateProfile,
    clearProfile
  }
})
