<template>
  <div class="reports-container">
    <!-- 页面头部 -->
    <div class="page-header">
      <div class="header-info">
        <h1>学习报告</h1>
        <p>查看和生成个人学习分析报告</p>
      </div>
      <div class="header-actions">
        <el-button 
          type="primary" 
          @click="showGenerateDialog = true"
          :loading="reportsStore.generating"
        >
          <el-icon><DocumentAdd /></el-icon>
          生成报告
        </el-button>
      </div>
    </div>

    <!-- 统计卡片 -->
    <div class="stats-cards">
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

    <!-- 报告列表 -->
    <el-card class="reports-list">
      <template #header>
        <div class="card-header">
          <span>我的学习报告</span>
          <div class="header-filters">
            <el-select 
              v-model="statusFilter" 
              placeholder="状态筛选"
              clearable
              size="small"
              style="width: 120px"
              @change="handleFilterChange"
            >
              <el-option label="已完成" value="completed" />
              <el-option label="生成中" value="generating" />
              <el-option label="生成失败" value="failed" />
            </el-select>
            
            <el-select 
              v-model="periodFilter" 
              placeholder="时间段筛选"
              clearable
              size="small"
              style="width: 120px; margin-left: 8px"
              @change="handleFilterChange"
            >
              <el-option label="一周" value="week" />
              <el-option label="一个月" value="month" />
              <el-option label="一学期" value="semester" />
              <el-option label="全部时间" value="all" />
            </el-select>
          </div>
        </div>
      </template>

      <div v-if="reportsStore.loading" class="loading-container">
        <el-icon class="is-loading"><Loading /></el-icon>
        <span>加载中...</span>
      </div>

      <div v-else-if="reportsStore.reports.length === 0" class="empty-container">
        <el-empty description="暂无学习报告">
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
          @click="viewReport(report)"
        >
          <div class="report-header">
            <div class="report-title">
              <span class="period-badge">{{ report.period_display }}</span>
              <span class="subjects">{{ report.subjects.join(', ') || '所有科目' }}</span>
            </div>
            <el-tag 
              :type="getStatusType(report.status)"
              size="small"
            >
              {{ report.status_display }}
            </el-tag>
          </div>
          
          <div class="report-stats">
            <div class="stat-item">
              <span class="label">作业完成率</span>
              <span class="value">{{ getCompletionRate(report) }}%</span>
            </div>
            <div class="stat-item">
              <span class="label">平均得分</span>
              <span class="value">{{ report.average_score }}%</span>
            </div>
            <div class="stat-item">
              <span class="label">提问次数</span>
              <span class="value">{{ report.total_questions }}</span>
            </div>
          </div>
          
          <div class="report-footer">
            <span class="generated-by">由 {{ report.generated_by_name }} 生成</span>
            <span class="created-time">{{ formatTime(report.created_at) }}</span>
          </div>
        </div>
      </div>

      <!-- 分页 -->
      <div v-if="pagination.total > 0" class="pagination-container">
        <el-pagination
          v-model:current-page="currentPage"
          :page-size="pageSize"
          :total="pagination.total"
          layout="prev, pager, next, total"
          @current-change="handlePageChange"
        />
      </div>
    </el-card>

    <!-- 生成报告对话框 -->
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
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useReportsStore } from '@/stores'
import { DocumentAdd, Document, CircleCheck, Loading } from '@element-plus/icons-vue'
import { ElMessage, type FormInstance, type FormRules } from 'element-plus'

const router = useRouter()
const reportsStore = useReportsStore()

// 响应式数据
const showGenerateDialog = ref(false)
const statusFilter = ref('')
const periodFilter = ref('')
const currentPage = ref(1)
const pageSize = ref(10)

// 生成报告表单
const generateFormRef = ref<FormInstance>()
const generateForm = ref({
  period: 'month',
  subjects: [] as string[]
})

const generateRules: FormRules = {
  period: [
    { required: true, message: '请选择时间段', trigger: 'change' }
  ]
}

// 分页信息
const pagination = ref({
  page: 1,
  page_size: 10,
  total: 0,
  total_pages: 0
})

// 计算属性
const completedReports = computed(() => {
  return reportsStore.reports.filter(r => r.status === 'completed').length
})

const generatingReports = computed(() => {
  return reportsStore.reports.filter(r => r.status === 'generating').length
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

const formatTime = (dateString: string) => {
  const date = new Date(dateString)
  return date.toLocaleDateString('zh-CN', {
    year: 'numeric',
    month: 'short',
    day: 'numeric',
    hour: '2-digit',
    minute: '2-digit'
  })
}

const handleFilterChange = () => {
  currentPage.value = 1
  fetchReports()
}

const handlePageChange = (page: number) => {
  currentPage.value = page
  fetchReports()
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

    await reportsStore.generateReport({
      period: generateForm.value.period as any,
      subjects: generateForm.value.subjects.length > 0 ? generateForm.value.subjects : undefined
    })

    showGenerateDialog.value = false
    generateForm.value = {
      period: 'month',
      subjects: []
    }

    // 刷新列表
    await fetchReports()

  } catch (error) {
    console.error('生成报告失败:', error)
  }
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

// 页面加载时获取数据
onMounted(() => {
  fetchReports()
})
</script>

<style scoped>
.reports-container {
  padding: 24px;
  background: #f5f7fa;
  min-height: 100vh;
}

.page-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 24px;
}

.header-info h1 {
  margin: 0 0 4px 0;
  color: #303133;
  font-size: 24px;
  font-weight: 500;
}

.header-info p {
  margin: 0;
  color: #909399;
  font-size: 14px;
}

.stats-cards {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 16px;
  margin-bottom: 24px;
}

.stat-card {
  border: none;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.1);
}

.stat-card :deep(.el-card__body) {
  padding: 20px;
  display: flex;
  align-items: center;
  justify-content: space-between;
}

.stat-content {
  flex: 1;
}

.stat-number {
  font-size: 28px;
  font-weight: bold;
  color: #303133;
  line-height: 1;
  margin-bottom: 4px;
}

.stat-label {
  color: #909399;
  font-size: 14px;
}

.stat-icon {
  font-size: 32px;
  color: #409eff;
  opacity: 0.8;
}

.reports-list {
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.1);
  border: none;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.header-filters {
  display: flex;
  align-items: center;
}

.loading-container,
.empty-container {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 60px 20px;
  color: #909399;
}

.loading-container .el-icon {
  font-size: 32px;
  margin-bottom: 16px;
}

.reports-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(320px, 1fr));
  gap: 16px;
  margin-bottom: 24px;
}

.report-card {
  background: white;
  border: 1px solid #e4e7ed;
  border-radius: 8px;
  padding: 20px;
  cursor: pointer;
  transition: all 0.3s;
}

.report-card:hover {
  border-color: #409eff;
  box-shadow: 0 4px 12px rgba(64, 158, 255, 0.15);
  transform: translateY(-2px);
}

.report-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 16px;
}

.report-title {
  flex: 1;
}

.period-badge {
  display: inline-block;
  background: #e1f3ff;
  color: #409eff;
  padding: 2px 8px;
  border-radius: 12px;
  font-size: 12px;
  font-weight: 500;
  margin-bottom: 4px;
}

.subjects {
  display: block;
  color: #303133;
  font-weight: 500;
  font-size: 14px;
}

.report-stats {
  margin-bottom: 16px;
}

.stat-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 8px;
}

.stat-item:last-child {
  margin-bottom: 0;
}

.stat-item .label {
  color: #606266;
  font-size: 13px;
}

.stat-item .value {
  color: #303133;
  font-weight: 500;
  font-size: 14px;
}

.report-footer {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding-top: 12px;
  border-top: 1px solid #f0f0f0;
  font-size: 12px;
  color: #909399;
}

.pagination-container {
  display: flex;
  justify-content: center;
  margin-top: 24px;
}

/* 响应式设计 */
@media (max-width: 768px) {
  .reports-container {
    padding: 16px;
  }

  .page-header {
    flex-direction: column;
    gap: 16px;
    align-items: flex-start;
  }

  .stats-cards {
    grid-template-columns: 1fr;
  }

  .reports-grid {
    grid-template-columns: 1fr;
  }

  .header-filters {
    flex-direction: column;
    gap: 8px;
    align-items: stretch;
  }

  .header-filters .el-select {
    width: 100% !important;
    margin-left: 0 !important;
  }
}
</style>
