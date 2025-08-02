<template>
  <div class="reports-container">
    <!-- 页面头部 -->
    <div class="page-header">
      <div class="header-info">
        <h1>{{ authStore.user?.role === 'teacher' ? '班级报告' : '学习报告' }}</h1>
        <p v-if="authStore.user?.role === 'teacher'">查看班级整体分析和学生个人报告</p>
        <p v-else>查看和生成个人学习分析报告</p>
      </div>
      <div class="header-actions">
        <el-button 
          v-if="authStore.user?.role === 'teacher'"
          type="success" 
          @click="showClassReportDialog = true"
          :loading="reportsStore.generatingClass"
        >
          <el-icon><TrendCharts /></el-icon>
          生成班级报告
        </el-button>
        <el-button 
          type="primary" 
          @click="showGenerateDialog = true"
          :loading="reportsStore.generating"
        >
          <el-icon><DocumentAdd /></el-icon>
          生成{{ authStore.user?.role === 'teacher' ? '学生' : '' }}报告
        </el-button>
      </div>
    </div>

    <!-- 班级报告区域 (仅教师可见) -->
    <div v-if="authStore.user?.role === 'teacher'" class="class-report-section">
      <el-card class="class-report-card">
        <template #header>
          <div class="card-header">
            <span>班级统计分析</span>
            <el-button 
              v-if="reportsStore.classReport" 
              text 
              @click="reportsStore.clearClassReport()"
            >
              清除报告
            </el-button>
          </div>
        </template>

        <div v-if="!reportsStore.classReport" class="empty-state">
          <el-empty description="暂无班级报告，点击上方按钮生成">
            <el-button type="primary" @click="showClassReportDialog = true">
              生成班级报告
            </el-button>
          </el-empty>
        </div>

        <div v-else class="class-report-content">
          <!-- 统计卡片 -->
          <div class="class-stats-cards">
            <el-card class="stat-card">
              <div class="stat-content">
                <div class="stat-number">{{ reportsStore.classReport.statistics.total_students }}</div>
                <div class="stat-label">班级人数</div>
              </div>
              <el-icon class="stat-icon"><User /></el-icon>
            </el-card>
            
            <el-card class="stat-card">
              <div class="stat-content">
                <div class="stat-number">{{ reportsStore.classReport.statistics.completion_rate }}%</div>
                <div class="stat-label">完成率</div>
              </div>
              <el-icon class="stat-icon"><CircleCheck /></el-icon>
            </el-card>
            
            <el-card class="stat-card">
              <div class="stat-content">
                <div class="stat-number">{{ reportsStore.classReport.statistics.average_score }}%</div>
                <div class="stat-label">得分率</div>
              </div>
              <el-icon class="stat-icon"><TrophyBase /></el-icon>
            </el-card>

            <el-card class="stat-card">
              <div class="stat-content">
                <div class="stat-number">{{ reportsStore.classReport.statistics.total_questions }}</div>
                <div class="stat-label">总提问数</div>
              </div>
              <el-icon class="stat-icon"><ChatDotRound /></el-icon>
            </el-card>
          </div>

          <!-- 图表区域 -->
          <div class="charts-section">
            <el-row :gutter="20">
              <el-col :span="12">
                <el-card>
                  <template #header>成绩分布</template>
                  <div ref="scoreChartRef" style="height: 300px;"></div>
                </el-card>
              </el-col>
              <el-col :span="12">
                <el-card>
                  <template #header>学生排名</template>
                  <div class="student-ranking">
                    <el-table 
                      :data="reportsStore.classReport.statistics.student_performance.slice(0, 10)" 
                      size="small"
                      max-height="350"
                      style="width: 100%"
                    >
                      <el-table-column prop="student_name" label="姓名" min-width="80" />
                      <el-table-column prop="completed_assignments" label="完成数" min-width="70" />
                      <el-table-column prop="average_score" label="平均得分率" min-width="90">
                        <template #default="{ row }">
                          {{ row.average_score }}%
                        </template>
                      </el-table-column>
                      <el-table-column prop="qa_count" label="提问数" min-width="70" />
                    </el-table>
                  </div>
                </el-card>
              </el-col>
            </el-row>
          </div>

          <!-- AI分析报告 -->
          <el-card class="ai-analysis">
            <template #header>班级分析报告</template>
            <div class="report-text">
              <MarkdownRenderer :content="reportsStore.classReport.report_content" />
            </div>
          </el-card>
        </div>
      </el-card>
    </div>

    <!-- 学生报告区域 -->
    <div class="student-reports-section">
      <el-card>
        <template #header>
          <span>{{ authStore.user?.role === 'teacher' ? '学生报告' : '我的报告' }}</span>
        </template>

        <!-- 统计卡片 (学生视角) -->
        <div v-if="authStore.user?.role === 'student'" class="stats-cards">
          <el-card class="stat-card">
            <div class="stat-content">
              <div class="stat-number">{{ reportsStore.reportCount }}</div>
              <div class="stat-label">总报告数</div>
            </div>
            <el-icon class="stat-icon"><Document /></el-icon>
          </el-card>
          
          <el-card class="stat-card">
            <div class="stat-content">
              <div class="stat-number">{{ completedReports }}</div>
              <div class="stat-label">已完成</div>
            </div>
            <el-icon class="stat-icon"><CircleCheck /></el-icon>
          </el-card>
          
          <el-card class="stat-card">
            <div class="stat-content">
              <div class="stat-number">{{ generatingReports }}</div>
              <div class="stat-label">生成中</div>
            </div>
            <el-icon class="stat-icon"><Loading /></el-icon>
          </el-card>
        </div>

        <!-- 筛选器 -->
        <div class="filters">
          <el-row :gutter="16">
            <el-col :span="6">
              <el-select v-model="statusFilter" placeholder="状态筛选" clearable>
                <el-option label="已完成" value="completed" />
                <el-option label="生成中" value="generating" />
                <el-option label="失败" value="failed" />
              </el-select>
            </el-col>
            <el-col :span="6">
              <el-select v-model="periodFilter" placeholder="时间段筛选" clearable>
                <el-option label="最近一周" value="week" />
                <el-option label="最近一个月" value="month" />
                <el-option label="最近一学期" value="semester" />
                <el-option label="全部时间" value="all" />
              </el-select>
            </el-col>
            <el-col :span="6">
              <el-button @click="fetchReports">刷新</el-button>
            </el-col>
          </el-row>
        </div>

        <!-- 报告列表 -->
        <div v-if="reportsStore.loading" class="loading-state">
          <el-skeleton :rows="3" animated />
        </div>

        <div v-else-if="reportsStore.reports.length === 0" class="empty-state">
          <el-empty description="暂无报告数据">
            <el-button type="primary" @click="showGenerateDialog = true">
              生成第一份报告
            </el-button>
          </el-empty>
        </div>

        <div v-else class="reports-grid">
          <div 
            v-for="report in reportsStore.reports" 
            :key="report.id"
            class="report-card"
            :class="getReportCardClass(report)"
            @click="viewReport(report)"
          >
            <div class="report-header">
              <div class="report-title">
                <!-- 学生信息更显眼 -->
                <div class="student-info-prominent">
                  <span class="student-name">{{ report.student_name }}</span>
                  <span class="period-badge">{{ report.period_display }}</span>
                </div>
                <span class="subjects">{{ report.subjects.join(', ') || '所有科目' }}</span>
              </div>
              <el-tag 
                :type="getStatusType(report.status)"
                size="small"
              >
                {{ report.status_display }}
              </el-tag>
            </div>

            <div class="report-content">
              <div class="report-stats">
                <div class="stat-item">
                  <span class="label">作业数:</span>
                  <span class="value">{{ report.completed_assignments }}/{{ report.total_assignments }}</span>
                </div>
                <div class="stat-item">
                  <span class="label">完成率:</span>
                  <span class="value">{{ getCompletionRate(report) }}%</span>
                </div>
                <div class="stat-item">
                  <span class="label">平均分:</span>
                  <span class="value">{{ report.average_score }}%</span>
                </div>
                <div class="stat-item">
                  <span class="label">提问数:</span>
                  <span class="value">{{ report.total_questions }}</span>
                </div>
              </div>
            </div>

            <div class="report-footer">
              <div class="footer-left">
                <span class="time">{{ formatTime(report.created_at) }}</span>
              </div>
              <div class="footer-right">
                <!-- 生成者信息更明显 -->
                <span class="generator-info">
                  <el-icon><User /></el-icon>
                  {{ report.generated_by_name }}
                  {{ report.generated_by_name === authStore.user?.real_name ? '(我)' : '' }}
                </span>
              </div>
            </div>
          </div>
        </div>

        <!-- 分页 -->
        <div v-if="pagination.total > 0" class="pagination">
          <el-pagination
            v-model:current-page="currentPage"
            v-model:page-size="pageSize"
            :page-sizes="[10, 20, 50]"
            :total="pagination.total"
            layout="total, sizes, prev, pager, next, jumper"
            @size-change="fetchReports"
            @current-change="fetchReports"
          />
        </div>
      </el-card>
    </div>

    <!-- 生成学生报告对话框 -->
    <el-dialog
      v-model="showGenerateDialog"
      title="生成学习报告"
      width="500px"
      :close-on-click-modal="false"
    >
      <el-form 
        ref="generateFormRef"
        :model="generateForm"
        :rules="generateRules"
        label-width="100px"
      >
        <el-form-item v-if="authStore.user?.role === 'teacher'" label="学生" prop="student_id">
          <el-select v-model="generateForm.student_id" placeholder="选择学生" style="width: 100%">
            <el-option 
              v-for="student in students" 
              :key="student.id" 
              :label="student.real_name" 
              :value="student.id" 
            />
          </el-select>
        </el-form-item>
        
        <el-form-item label="时间段" prop="period">
          <el-select v-model="generateForm.period" placeholder="选择时间段" style="width: 100%">
            <el-option label="最近一周" value="week" />
            <el-option label="最近一个月" value="month" />
            <el-option label="最近一学期" value="semester" />
            <el-option label="全部时间" value="all" />
          </el-select>
        </el-form-item>
        
        <el-form-item label="科目筛选">
          <el-select 
            v-model="generateForm.subjects" 
            multiple 
            placeholder="选择科目（为空则包含所有科目）"
            style="width: 100%"
          >
            <el-option label="Python编程" value="Python编程" />
            <el-option label="数据结构" value="数据结构" />
            <el-option label="算法设计" value="算法设计" />
            <el-option label="数学" value="数学" />
            <el-option label="其他" value="其他" />
          </el-select>
        </el-form-item>
      </el-form>
      
      <template #footer>
        <el-button @click="showGenerateDialog = false">取消</el-button>
        <el-button 
          type="primary" 
          @click="handleGenerateReport"
          :loading="reportsStore.generating"
        >
          生成报告
        </el-button>
      </template>
    </el-dialog>

    <!-- 生成班级报告对话框 -->
    <el-dialog
      v-model="showClassReportDialog"
      title="生成班级报告"
      width="500px"
      :close-on-click-modal="false"
    >
      <el-form 
        ref="classReportFormRef"
        :model="classReportForm"
        :rules="classReportRules"
        label-width="100px"
      >
        <el-form-item label="时间段" prop="period">
          <el-select v-model="classReportForm.period" placeholder="选择时间段" style="width: 100%">
            <el-option label="最近一周" value="week" />
            <el-option label="最近一个月" value="month" />
            <el-option label="最近一学期" value="semester" />
            <el-option label="全部时间" value="all" />
          </el-select>
        </el-form-item>
        
        <el-form-item label="科目筛选">
          <el-select 
            v-model="classReportForm.subjects" 
            multiple 
            placeholder="选择科目（为空则包含所有科目）"
            style="width: 100%"
          >
            <el-option label="Python编程" value="Python编程" />
            <el-option label="数据结构" value="数据结构" />
            <el-option label="算法设计" value="算法设计" />
            <el-option label="数学" value="数学" />
            <el-option label="其他" value="其他" />
          </el-select>
        </el-form-item>
      </el-form>
      
      <template #footer>
        <el-button @click="showClassReportDialog = false">取消</el-button>
        <el-button 
          type="primary" 
          @click="handleGenerateClassReport"
          :loading="reportsStore.generatingClass"
        >
          生成班级报告
        </el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, nextTick, watch } from 'vue'
import { useRouter } from 'vue-router'
import { useReportsStore, useAuthStore } from '@/stores'
import { DocumentAdd, Document, CircleCheck, Loading, TrendCharts, User, TrophyBase, ChatDotRound } from '@element-plus/icons-vue'
import { ElMessage, type FormInstance, type FormRules } from 'element-plus'
import * as echarts from 'echarts'
import MarkdownRenderer from '@/components/common/MarkdownRenderer.vue'
import request from '@/utils/request'  // 默认导入，不用花括号
import { chatApi } from '@/api/chat'  // 导入聊天API

const router = useRouter()
const reportsStore = useReportsStore()
const authStore = useAuthStore()

// 响应式数据
const showGenerateDialog = ref(false)
const showClassReportDialog = ref(false)
const statusFilter = ref('')
const periodFilter = ref('')
const currentPage = ref(1)
const pageSize = ref(10)
const students = ref([])
const scoreChartRef = ref<HTMLElement>()

// 分页数据
const pagination = ref({
  page: 1,
  page_size: 10,
  total: 0,
  total_pages: 0
})

// 生成学生报告表单
const generateFormRef = ref<FormInstance>()
const generateForm = ref({
  student_id: '',
  period: 'month',
  subjects: [] as string[]
})

const generateRules: FormRules = {
  student_id: [
    { required: true, message: '请选择学生', trigger: 'change' }
  ],
  period: [
    { required: true, message: '请选择时间段', trigger: 'change' }
  ]
}

// 生成班级报告表单
const classReportFormRef = ref<FormInstance>()
const classReportForm = ref({
  period: 'month',
  subjects: [] as string[]
})

const classReportRules: FormRules = {
  period: [
    { required: true, message: '请选择时间段', trigger: 'change' }
  ]
}

// 计算属性
const completedReports = computed(() => {
  return reportsStore.reports.filter(report => report.status === 'completed').length
})

const generatingReports = computed(() => {
  return reportsStore.reports.filter(report => report.status === 'generating').length
})

// 方法
const getStatusType = (status: string) => {
  switch (status) {
    case 'completed': return 'success'
    case 'generating': return 'warning'
    case 'failed': return 'danger'
    default: return 'info'
  }
}

const getCompletionRate = (report: any) => {
  if (report.total_assignments === 0) return 0
  return Math.round((report.completed_assignments / report.total_assignments) * 100)
}

const formatTime = (time: string) => {
  return new Date(time).toLocaleString('zh-CN')
}

const fetchReports = async () => {
  try {
    const params = {
      page: currentPage.value,
      page_size: pageSize.value,
      status: statusFilter.value || undefined,
      period: periodFilter.value || undefined
    }
    const response = await reportsStore.fetchReports(params)
    pagination.value = response.pagination
  } catch (error) {
    console.error('获取报告列表失败:', error)
  }
}

const handleGenerateReport = async () => {
  if (!generateFormRef.value) return

  try {
    await generateFormRef.value.validate()

    const data: any = {
      period: generateForm.value.period as any,
      subjects: generateForm.value.subjects.length > 0 ? generateForm.value.subjects : undefined
    }

    // 教师生成学生报告时必须传递学生ID
    if (authStore.user?.role === 'teacher') {
      if (!generateForm.value.student_id) {
        ElMessage.error('请选择要生成报告的学生')
        return
      }
      data.student_id = generateForm.value.student_id
      console.log('[DEBUG] 教师生成报告，学生ID:', data.student_id)
    } else {
      console.log('[DEBUG] 学生自己生成报告')
    }

    console.log('[DEBUG] 发送报告生成请求:', data)

    await reportsStore.generateReport(data)

    showGenerateDialog.value = false
    generateForm.value = {
      student_id: '',
      period: 'month',
      subjects: []
    }

    // 刷新列表
    await fetchReports()

  } catch (error) {
    console.error('生成报告失败:', error)
  }
}

const handleGenerateClassReport = async () => {
  if (!classReportFormRef.value) return

  try {
    await classReportFormRef.value.validate()

    const requestData = {
      period: classReportForm.value.period,
      subjects: classReportForm.value.subjects.length > 0 ? classReportForm.value.subjects : []
    }

    console.log('[DEBUG] 发送班级报告请求:', requestData)

    await reportsStore.generateClassReport(requestData)

    showClassReportDialog.value = false
    classReportForm.value = {
      period: 'month',
      subjects: []
    }

    // 渲染图表
    nextTick(() => {
      renderScoreChart()
    })

  } catch (error) {
    console.error('生成班级报告失败:', error)
    
    // 显示详细错误信息
    if (error.response?.data?.errors) {
      const errors = error.response.data.errors
      const errorMessages = Object.entries(errors).map(([field, messages]) => 
        `${field}: ${Array.isArray(messages) ? messages.join(', ') : messages}`
      ).join('\n')
      ElMessage.error(`参数错误:\n${errorMessages}`)
    } else {
      ElMessage.error(error.response?.data?.message || '生成班级报告失败')
    }
  }
}

const renderScoreChart = () => {
  if (!scoreChartRef.value || !reportsStore.classReport) return

  console.log('[DEBUG] 开始渲染成绩分布图表')
  console.log('[DEBUG] classReport数据:', reportsStore.classReport)
  console.log('[DEBUG] statistics数据:', reportsStore.classReport.statistics)
  
  const chart = echarts.init(scoreChartRef.value)
  const distribution = reportsStore.classReport.statistics?.score_distribution

  if (!distribution) {
    console.log('[DEBUG] score_distribution数据为空')
    return
  }

  console.log('[DEBUG] score_distribution数据:', distribution)

  const option = {
    title: {
      text: '成绩分布',
      left: 'center'
    },
    tooltip: {
      trigger: 'item',
      formatter: '{a} <br/>{b}: {c} ({d}%)'
    },
    series: [
      {
        name: '成绩分布',
        type: 'pie',
        radius: '50%',
        data: [
          { value: distribution['0-60'] || 0, name: '0-60分' },
          { value: distribution['60-70'] || 0, name: '60-70分' },
          { value: distribution['70-80'] || 0, name: '70-80分' },
          { value: distribution['80-90'] || 0, name: '80-90分' },
          { value: distribution['90-100'] || 0, name: '90-100分' }
        ],
        emphasis: {
          itemStyle: {
            shadowBlur: 10,
            shadowOffsetX: 0,
            shadowColor: 'rgba(0, 0, 0, 0.5)'
          }
        }
      }
    ]
  }

  chart.setOption(option)
  console.log('[DEBUG] 图表渲染完成')
}

const viewReport = (report: any) => {
  if (report.status === 'completed') {
    router.push(`/reports/${report.id}`)
  } else if (report.status === 'generating') {
    ElMessage.info('报告正在生成中，请稍后查看')
  } else {
    ElMessage.error('报告生成失败，请重新生成')
  }
}

// 获取学生列表（仅教师需要）
const fetchStudents = async () => {
  if (authStore.user?.role !== 'teacher') return
  
  try {
    console.log('[DEBUG] 获取学生列表...')
    // 使用聊天API获取可聊天用户（教师获取学生列表）
    const response = await chatApi.getChatUsers()
    students.value = response.data.map(user => ({
      id: user.id,
      real_name: user.real_name,
      username: user.username
    }))
    console.log('[DEBUG] 获取到学生列表:', students.value.length, '个学生')
  } catch (error) {
    console.error('[DEBUG] 获取学生列表失败:', error)
    ElMessage.error('获取学生列表失败')
  }
}

// 监听班级报告变化，渲染图表
watch(() => reportsStore.classReport, (newReport) => {
  if (newReport) {
    nextTick(() => {
      renderScoreChart()
    })
  }
})

// 页面加载时获取数据
onMounted(async () => {
  // 先加载本地存储的班级报告
  reportsStore.loadClassReportFromStorage()
  
  await fetchReports()
  await fetchStudents()
})

// 根据生成者添加样式类
const getReportCardClass = (report: any) => {
  const classes = []
  
  // 如果是自己生成的
  if (report.generated_by_name === authStore.user?.real_name) {
    classes.push('self-generated')
  }
  
  // 如果是学生自己生成的
  if (report.student_name === report.generated_by_name) {
    classes.push('student-self-generated')
  }
  
  return classes.join(' ')
}
</script>

<style scoped>
.reports-container {
  padding: 20px;
}

.page-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
}

.header-info h1 {
  margin: 0 0 8px 0;
  font-size: 24px;
  color: #303133;
}

.header-info p {
  margin: 0;
  color: #606266;
}

.header-actions {
  display: flex;
  gap: 12px;
}

.class-report-section {
  margin-bottom: 30px;
}

.class-report-card {
  margin-bottom: 20px;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.class-stats-cards {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 16px;
  margin-bottom: 20px;
}

.stat-card {
  border: none;
  box-shadow: 0 2px 12px 0 rgba(0, 0, 0, 0.1);
}

.stat-card .el-card__body {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 20px;
}

.stat-content {
  flex: 1;
}

.stat-number {
  font-size: 28px;
  font-weight: bold;
  color: #303133;
  margin-bottom: 4px;
}

.stat-label {
  font-size: 14px;
  color: #909399;
}

.stat-icon {
  font-size: 32px;
  color: #409eff;
  opacity: 0.8;
}

.charts-section {
  margin-bottom: 20px;
}

.student-ranking {
  height: 300px;
  overflow-y: auto;
}

.ai-analysis .report-text {
  max-height: 400px;
  overflow-y: auto;
}

.student-reports-section .stats-cards {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 16px;
  margin-bottom: 20px;
}

.filters {
  margin-bottom: 20px;
}

.reports-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(350px, 1fr));
  gap: 16px;
  margin-bottom: 20px;
}

.report-card {
  border: 1px solid #ebeef5;
  border-radius: 8px;
  padding: 16px;
  cursor: pointer;
  transition: all 0.3s;
  background: white;
}

.report-card:hover {
  border-color: #409eff;
  box-shadow: 0 2px 12px 0 rgba(64, 158, 255, 0.2);
}

.report-card.self-generated {
  border-left: 4px solid #67c23a;
}

.report-card.student-self-generated {
  border-left: 4px solid #e6a23c;
}

.report-card.self-generated .generator-info {
  background: #f0f9ff;
  color: #0369a1;
}

.report-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 12px;
}

.report-title {
  flex: 1;
}

.student-info-prominent {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-bottom: 4px;
}

.student-name {
  font-size: 16px;
  font-weight: 600;
  color: #409eff;
  background: linear-gradient(135deg, #409eff, #67c23a);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
}

.period-badge {
  background: #f0f9ff;
  color: #0369a1;
  padding: 2px 8px;
  border-radius: 12px;
  font-size: 12px;
  font-weight: 500;
  border: 1px solid #bae6fd;
}

.report-footer {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-top: 12px;
  padding-top: 12px;
  border-top: 1px solid #f0f0f0;
}

.footer-left .time {
  color: #909399;
  font-size: 12px;
}

.footer-right .generator-info {
  display: flex;
  align-items: center;
  gap: 4px;
  color: #606266;
  font-size: 12px;
  font-weight: 500;
  background: #f8f9fa;
  padding: 4px 8px;
  border-radius: 8px;
  border: 1px solid #e9ecef;
}

.generator-info .el-icon {
  font-size: 14px;
  color: #909399;
}

/* 教师视角的报告卡片特殊样式 */
.reports-grid .report-card:hover .student-name {
  transform: scale(1.05);
  transition: transform 0.2s ease;
}

.reports-grid .report-card:hover .generator-info {
  background: #e3f2fd;
  border-color: #90caf9;
}

.subjects {
  color: #606266;
  font-size: 14px;
}

.report-stats {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 8px;
  margin-bottom: 12px;
}

.stat-item {
  display: flex;
  justify-content: space-between;
  font-size: 14px;
}

.stat-item .label {
  color: #909399;
}

.stat-item .value {
  color: #303133;
  font-weight: 500;
}

.report-footer {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-top: 12px;
  padding-top: 12px;
  border-top: 1px solid #f0f0f0;
}

.footer-left .time {
  color: #909399;
  font-size: 12px;
}

.footer-right .generator-info {
  display: flex;
  align-items: center;
  gap: 4px;
  color: #606266;
  font-size: 12px;
  font-weight: 500;
  background: #f8f9fa;
  padding: 4px 8px;
  border-radius: 8px;
  border: 1px solid #e9ecef;
}

.generator-info .el-icon {
  font-size: 14px;
  color: #909399;
}

/* 教师视角的报告卡片特殊样式 */
.reports-grid .report-card:hover .student-name {
  transform: scale(1.05);
  transition: transform 0.2s ease;
}

.reports-grid .report-card:hover .generator-info {
  background: #e3f2fd;
  border-color: #90caf9;
}

.pagination {
  display: flex;
  justify-content: center;
  margin-top: 20px;
}

.empty-state, .loading-state {
  padding: 40px 0;
}
</style>























