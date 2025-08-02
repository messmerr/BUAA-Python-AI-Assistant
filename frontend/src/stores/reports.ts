import { ref, computed } from 'vue'
import { defineStore } from 'pinia'
import { reportsApi, type LearningReportListItem, type LearningReport, type GenerateReportRequest, type ClassReportRequest, type ClassReportResponse } from '@/api/reports'
import { ElMessage } from 'element-plus'

export const useReportsStore = defineStore('reports', () => {
  // 状态
  const reports = ref<LearningReportListItem[]>([])
  const currentReport = ref<LearningReport | null>(null)
  const classReport = ref<ClassReportResponse | null>(null)
  const loading = ref(false)
  const generating = ref(false)
  const generatingClass = ref(false)

  // 计算属性
  const reportCount = computed(() => reports.value.length)
  
  const completedReports = computed(() => {
    return reports.value.filter(report => report.status === 'completed').length
  })
  
  const generatingReports = computed(() => {
    return reports.value.filter(report => report.status === 'generating').length
  })

  // 获取最近的报告
  const getRecentReports = computed(() => {
    return reports.value
      .slice()
      .sort((a, b) => new Date(b.created_at).getTime() - new Date(a.created_at).getTime())
      .slice(0, 5)
  })

  // 生成学习报告
  const generateReport = async (data: GenerateReportRequest) => {
    generating.value = true
    try {
      const response = await reportsApi.generateReport(data)
      ElMessage.success('报告生成请求已提交，请稍后查看结果')
      
      // 重新获取报告列表
      await fetchReports()
      
      return response.data
    } catch (error) {
      console.error('生成报告失败:', error)
      ElMessage.error('生成报告失败')
      throw error
    } finally {
      generating.value = false
    }
  }

  // 生成班级报告
  const generateClassReport = async (data: ClassReportRequest) => {
    generatingClass.value = true
    try {
      const response = await reportsApi.generateClassReport(data)
      classReport.value = response.data
      ElMessage.success('班级报告生成成功')
      return response.data
    } catch (error) {
      console.error('生成班级报告失败:', error)
      ElMessage.error('生成班级报告失败')
      throw error
    } finally {
      generatingClass.value = false
    }
  }

  // 获取报告列表
  const fetchReports = async (params?: any) => {
    loading.value = true
    try {
      const response = await reportsApi.getReports(params)
      reports.value = response.data.reports
      return response.data
    } catch (error) {
      console.error('获取报告列表失败:', error)
      ElMessage.error('获取报告列表失败')
      throw error
    } finally {
      loading.value = false
    }
  }

  // 获取报告详情
  const fetchReportDetail = async (reportId: string) => {
    loading.value = true
    try {
      const response = await reportsApi.getReportDetail(reportId)
      currentReport.value = response.data
      return response.data
    } catch (error) {
      console.error('获取报告详情失败:', error)
      ElMessage.error('获取报告详情失败')
      throw error
    } finally {
      loading.value = false
    }
  }

  // 清空当前报告
  const clearCurrentReport = () => {
    currentReport.value = null
  }

  // 清空班级报告
  const clearClassReport = () => {
    classReport.value = null
  }

  return {
    // 状态
    reports,
    currentReport,
    classReport,
    loading,
    generating,
    generatingClass,
    
    // 计算属性
    reportCount,
    completedReports,
    generatingReports,
    getRecentReports,
    
    // 方法
    generateReport,
    generateClassReport,
    fetchReports,
    fetchReportDetail,
    clearCurrentReport,
    clearClassReport
  }
})

