import { ref, computed } from 'vue'
import { defineStore } from 'pinia'
import { reportsApi, type LearningReport, type LearningReportListItem, type GenerateReportRequest } from '@/api/reports'
import { ElMessage } from 'element-plus'

export const useReportsStore = defineStore('reports', () => {
  // 状态
  const reports = ref<LearningReportListItem[]>([])
  const currentReport = ref<LearningReport | null>(null)
  const loading = ref(false)
  const generating = ref(false)
  const total = ref(0)

  // 计算属性
  const reportCount = computed(() => reports.value.length)
  
  // 按状态分组报告
  const getReportsByStatus = computed(() => {
    const grouped: Record<string, LearningReportListItem[]> = {}
    reports.value.forEach(report => {
      if (!grouped[report.status]) {
        grouped[report.status] = []
      }
      grouped[report.status].push(report)
    })
    return grouped
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

  // 获取报告列表
  const fetchReports = async (params?: {
    page?: number
    page_size?: number
    status?: string
    period?: string
  }) => {
    loading.value = true
    try {
      const response = await reportsApi.getReports(params)
      reports.value = response.data.reports
      total.value = response.data.pagination.total
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

  // 清除当前报告
  const clearCurrentReport = () => {
    currentReport.value = null
  }

  // 检查报告生成状态
  const checkReportStatus = async (reportId: string) => {
    try {
      const report = await fetchReportDetail(reportId)
      return report.status
    } catch (error) {
      console.error('检查报告状态失败:', error)
      return 'failed'
    }
  }

  return {
    // 状态
    reports,
    currentReport,
    loading,
    generating,
    total,
    
    // 计算属性
    reportCount,
    getReportsByStatus,
    getRecentReports,
    
    // 方法
    generateReport,
    fetchReports,
    fetchReportDetail,
    clearCurrentReport,
    checkReportStatus
  }
})
