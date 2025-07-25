import { ref, computed } from 'vue'
import { defineStore } from 'pinia'
import { assignmentsApi } from '@/api'
import type { Assignment, CreateAssignmentRequest, SubmitAssignmentRequest, Submission } from '@/types'
import { ElMessage } from 'element-plus'

export const useAssignmentsStore = defineStore('assignments', () => {
  // 状态
  const assignments = ref<Assignment[]>([])
  const currentAssignment = ref<Assignment | null>(null)
  const submissions = ref<Submission[]>([])
  const currentSubmission = ref<Submission | null>(null)
  const loading = ref(false)
  const total = ref(0)
  const pagination = ref({
    page: 1,
    page_size: 10,
    total: 0,
    total_pages: 0
  })

  // 计算属性
  const assignmentCount = computed(() => assignments.value.length)

  // 获取作业列表
  const fetchAssignments = async (params?: {
    page?: number
    page_size?: number
    subject?: string
    status?: string
    completion_status?: string
  }) => {
    loading.value = true
    try {
      console.log('获取作业列表，参数:', params)
      const response = await assignmentsApi.getAssignments(params)
      console.log('作业列表响应:', response)

      // 根据后端实际返回的数据格式解析
      assignments.value = response.data.assignments || []
      total.value = response.data.pagination?.total || 0

      // 更新分页信息
      if (response.data.pagination) {
        pagination.value = {
          page: response.data.pagination.page || 1,
          page_size: response.data.pagination.page_size || 10,
          total: response.data.pagination.total || 0,
          total_pages: response.data.pagination.total_pages || 0
        }
      }
    } catch (error) {
      console.error('获取作业列表失败:', error)
      ElMessage.error('获取作业列表失败')
    } finally {
      loading.value = false
    }
  }

  // 获取作业详情
  const fetchAssignmentDetail = async (assignmentId: string) => {
    loading.value = true
    try {
      console.log('Store: 开始获取作业详情，ID:', assignmentId)
      const response = await assignmentsApi.getAssignmentDetail(assignmentId)
      console.log('Store: API响应:', response)

      // 根据后端实际返回的数据格式解析
      if (response.data) {
        currentAssignment.value = response.data
        console.log('Store: 作业详情设置成功:', currentAssignment.value)
        return response.data
      } else {
        console.error('Store: 响应数据为空')
        throw new Error('响应数据为空')
      }
    } catch (error) {
      console.error('获取作业详情失败:', error)
      ElMessage.error('获取作业详情失败')
      currentAssignment.value = null
      throw error
    } finally {
      loading.value = false
    }
  }

  // 创建作业（教师）
  const createAssignment = async (data: CreateAssignmentRequest) => {
    loading.value = true
    try {
      const response = await assignmentsApi.createAssignment(data)
      ElMessage.success('作业创建成功')
      // 重新获取作业列表
      await fetchAssignments()
      return response.data
    } catch (error) {
      console.error('创建作业失败:', error)
      throw error
    } finally {
      loading.value = false
    }
  }

  // 更新作业（教师）
  const updateAssignment = async (assignmentId: string, data: Partial<CreateAssignmentRequest>) => {
    loading.value = true
    try {
      const response = await assignmentsApi.updateAssignment(assignmentId, data)
      ElMessage.success('作业更新成功')
      
      // 更新本地状态
      const index = assignments.value.findIndex(a => a.id === assignmentId)
      if (index !== -1) {
        assignments.value[index] = response.data
      }
      if (currentAssignment.value?.id === assignmentId) {
        currentAssignment.value = response.data
      }
      
      return response.data
    } catch (error) {
      console.error('更新作业失败:', error)
      throw error
    } finally {
      loading.value = false
    }
  }

  // 删除作业（教师）
  const deleteAssignment = async (assignmentId: string) => {
    loading.value = true
    try {
      await assignmentsApi.deleteAssignment(assignmentId)
      ElMessage.success('作业删除成功')
      
      // 从本地状态中移除
      assignments.value = assignments.value.filter(a => a.id !== assignmentId)
      if (currentAssignment.value?.id === assignmentId) {
        currentAssignment.value = null
      }
      
      return true
    } catch (error) {
      console.error('删除作业失败:', error)
      throw error
    } finally {
      loading.value = false
    }
  }

  // 提交作业（学生）
  const submitAssignment = async (assignmentId: string, data: SubmitAssignmentRequest) => {
    loading.value = true
    try {
      console.log('Store: 开始提交作业')
      console.log('Store: 作业ID:', assignmentId)
      console.log('Store: 提交数据:', data)

      const response = await assignmentsApi.submitAssignment(assignmentId, data)
      console.log('Store: 提交响应:', response)

      ElMessage.success('作业提交成功')
      return response.data
    } catch (error: any) {
      console.error('提交作业失败:', error)
      console.error('错误详情:', error.response?.data)
      throw error
    } finally {
      loading.value = false
    }
  }

  // 获取作业提交列表
  const fetchSubmissions = async (assignmentId: string, params?: {
    page?: number
    page_size?: number
    student?: string
  }) => {
    loading.value = true
    try {
      const response = await assignmentsApi.getSubmissions(assignmentId, params)
      submissions.value = response.data.submissions
      return response.data
    } catch (error) {
      console.error('获取提交列表失败:', error)
      ElMessage.error('获取提交列表失败')
      throw error
    } finally {
      loading.value = false
    }
  }

  // 获取作业批改结果（新接口）
  const fetchAssignmentResult = async (assignmentId: string, studentId?: string) => {
    loading.value = true
    try {
      console.log('获取作业批改结果:', assignmentId, studentId)
      const response = await assignmentsApi.getAssignmentResult(assignmentId, studentId)
      console.log('批改结果响应:', response)
      currentSubmission.value = response.data
      return response.data
    } catch (error) {
      console.error('获取批改结果失败:', error)
      if ((error as any).response?.status === 404) {
        ElMessage.warning('作业尚未提交或不存在')
      } else {
        ElMessage.error('获取批改结果失败')
      }
      throw error
    } finally {
      loading.value = false
    }
  }

  // 获取作业批改结果（旧接口，保持兼容）
  const fetchSubmissionResult = async (assignmentId: string, submissionId: string) => {
    loading.value = true
    try {
      const response = await assignmentsApi.getSubmissionResult(assignmentId, submissionId)
      currentSubmission.value = response.data
      return response.data
    } catch (error) {
      console.error('获取批改结果失败:', error)
      ElMessage.error('获取批改结果失败')
      throw error
    } finally {
      loading.value = false
    }
  }

  // 重新批改作业（教师）
  const regradeSubmission = async (assignmentId: string, submissionId: string) => {
    loading.value = true
    try {
      const response = await assignmentsApi.regradeSubmission(assignmentId, submissionId)
      ElMessage.success('重新批改成功')
      
      // 重新获取批改结果
      await fetchSubmissionResult(assignmentId, submissionId)
      
      return response.data
    } catch (error) {
      console.error('重新批改失败:', error)
      throw error
    } finally {
      loading.value = false
    }
  }

  // 清除当前作业
  const clearCurrentAssignment = () => {
    currentAssignment.value = null
  }

  // 清除当前提交
  const clearCurrentSubmission = () => {
    currentSubmission.value = null
  }

  return {
    // 状态
    assignments,
    currentAssignment,
    submissions,
    currentSubmission,
    loading,
    total,
    pagination,

    // 计算属性
    assignmentCount,
    
    // 方法
    fetchAssignments,
    fetchAssignmentDetail,
    createAssignment,
    updateAssignment,
    deleteAssignment,
    submitAssignment,
    fetchSubmissions,
    fetchAssignmentResult,
    fetchSubmissionResult,
    regradeSubmission,
    clearCurrentAssignment,
    clearCurrentSubmission
  }
})
