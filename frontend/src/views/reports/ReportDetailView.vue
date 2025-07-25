<template>
  <div class="report-detail-container">
    <!-- 返回按钮 -->
    <div class="back-button">
      <el-button @click="goBack" type="text">
        <el-icon><ArrowLeft /></el-icon>
        返回报告列表
      </el-button>
    </div>

    <div v-if="reportsStore.loading" class="loading-container">
      <el-icon class="is-loading"><Loading /></el-icon>
      <span>加载中...</span>
    </div>

    <div v-else-if="!reportsStore.currentReport" class="error-container">
      <el-result
        icon="warning"
        title="报告不存在"
        sub-title="您访问的报告不存在或已被删除"
      >
        <template #extra>
          <el-button type="primary" @click="goBack">返回列表</el-button>
        </template>
      </el-result>
    </div>

    <div v-else class="report-content">
      <!-- 报告头部信息 -->
      <el-card class="report-header-card">
        <div class="report-header-info">
          <div class="student-info">
            <h1>{{ reportsStore.currentReport.student_name }} 的学习报告</h1>
            <div class="meta-info">
              <span class="meta-item">
                <el-icon><User /></el-icon>
                学号：{{ reportsStore.currentReport.student_id_number }}
              </span>
              <span class="meta-item">
                <el-icon><Calendar /></el-icon>
                时间段：{{ reportsStore.currentReport.period_display }}
              </span>
              <span class="meta-item">
                <el-icon><Document /></el-icon>
                科目：{{ reportsStore.currentReport.subjects.join(', ') || '所有科目' }}
              </span>
              <span class="meta-item">
                <el-icon><Clock /></el-icon>
                生成时间：{{ formatTime(reportsStore.currentReport.created_at) }}
              </span>
            </div>
          </div>
          
          <div class="report-actions">
            <el-button @click="printReport">
              <el-icon><Printer /></el-icon>
              打印报告
            </el-button>
            <el-button type="primary" @click="exportReport">
              <el-icon><Download /></el-icon>
              导出PDF
            </el-button>
          </div>
        </div>
      </el-card>

      <!-- 统计概览 -->
      <el-card class="stats-overview">
        <template #header>
          <span>学习数据概览</span>
        </template>
        
        <div class="stats-grid">
          <div class="stat-item">
            <div class="stat-icon assignments">
              <el-icon><Document /></el-icon>
            </div>
            <div class="stat-content">
              <div class="stat-number">{{ reportsStore.currentReport.completed_assignments }}</div>
              <div class="stat-label">已完成作业</div>
              <div class="stat-detail">共 {{ reportsStore.currentReport.total_assignments }} 份</div>
            </div>
          </div>
          
          <div class="stat-item">
            <div class="stat-icon score">
              <el-icon><TrophyBase /></el-icon>
            </div>
            <div class="stat-content">
              <div class="stat-number">{{ reportsStore.currentReport.average_score }}%</div>
              <div class="stat-label">平均得分</div>
              <div class="stat-detail">{{ getScoreLevel(reportsStore.currentReport.average_score) }}</div>
            </div>
          </div>
          
          <div class="stat-item">
            <div class="stat-icon questions">
              <el-icon><ChatDotRound /></el-icon>
            </div>
            <div class="stat-content">
              <div class="stat-number">{{ reportsStore.currentReport.total_questions }}</div>
              <div class="stat-label">提问次数</div>
              <div class="stat-detail">学习积极性体现</div>
            </div>
          </div>
          
          <div class="stat-item">
            <div class="stat-icon completion">
              <el-icon><CircleCheck /></el-icon>
            </div>
            <div class="stat-content">
              <div class="stat-number">{{ getCompletionRate() }}%</div>
              <div class="stat-label">作业完成率</div>
              <div class="stat-detail">{{ getCompletionLevel() }}</div>
            </div>
          </div>
        </div>
      </el-card>

      <!-- 报告正文 -->
      <el-card class="report-content-card">
        <template #header>
          <span>详细分析报告</span>
        </template>
        
        <div class="report-text">
          <MarkdownRenderer :content="reportsStore.currentReport.report_content" />
        </div>
      </el-card>

      <!-- 生成信息 -->
      <el-card class="report-footer">
        <div class="generation-info">
          <span>报告由 {{ reportsStore.currentReport.generated_by_name }} 于 {{ formatTime(reportsStore.currentReport.created_at) }} 生成</span>
          <el-tag :type="getStatusType(reportsStore.currentReport.status)" size="small">
            {{ reportsStore.currentReport.status_display }}
          </el-tag>
        </div>
      </el-card>
    </div>
  </div>
</template>

<script setup lang="ts">
import { onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useReportsStore } from '@/stores'
import {
  ArrowLeft, Loading, User, Calendar, Document, Clock,
  Printer, Download, TrophyBase, ChatDotRound, CircleCheck
} from '@element-plus/icons-vue'
import { ElMessage } from 'element-plus'
import MarkdownRenderer from '@/components/common/MarkdownRenderer.vue'

const route = useRoute()
const router = useRouter()
const reportsStore = useReportsStore()

const reportId = route.params.id as string

// 方法
const goBack = () => {
  router.push('/reports')
}

const formatTime = (dateString: string) => {
  const date = new Date(dateString)
  return date.toLocaleString('zh-CN', {
    year: 'numeric',
    month: 'long',
    day: 'numeric',
    hour: '2-digit',
    minute: '2-digit'
  })
}

const getStatusType = (status: string) => {
  switch (status) {
    case 'completed': return 'success'
    case 'generating': return 'warning'
    case 'failed': return 'danger'
    default: return 'info'
  }
}

const getScoreLevel = (score: number) => {
  if (score >= 90) return '优秀'
  if (score >= 80) return '良好'
  if (score >= 70) return '中等'
  if (score >= 60) return '及格'
  return '需要努力'
}

const getCompletionRate = () => {
  const report = reportsStore.currentReport
  if (!report || report.total_assignments === 0) return 0
  return Math.round((report.completed_assignments / report.total_assignments) * 100)
}

const getCompletionLevel = () => {
  const rate = getCompletionRate()
  if (rate >= 90) return '非常积极'
  if (rate >= 70) return '比较积极'
  if (rate >= 50) return '一般'
  return '需要提高'
}



const printReport = () => {
  window.print()
}

const exportReport = () => {
  ElMessage.info('PDF导出功能开发中...')
}

// 页面加载时获取报告详情
onMounted(async () => {
  if (reportId) {
    try {
      await reportsStore.fetchReportDetail(reportId)
    } catch (error) {
      console.error('获取报告详情失败:', error)
      ElMessage.error('获取报告详情失败')
    }
  }
})
</script>

<style scoped>
.report-detail-container {
  padding: 24px;
  background: #f5f7fa;
  min-height: 100vh;
}

.back-button {
  margin-bottom: 16px;
}

.loading-container,
.error-container {
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

.report-content {
  max-width: 1200px;
  margin: 0 auto;
}

.report-header-card {
  margin-bottom: 24px;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.1);
  border: none;
}

.report-header-info {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
}

.student-info h1 {
  margin: 0 0 16px 0;
  color: #303133;
  font-size: 24px;
  font-weight: 500;
}

.meta-info {
  display: flex;
  flex-wrap: wrap;
  gap: 16px;
}

.meta-item {
  display: flex;
  align-items: center;
  color: #606266;
  font-size: 14px;
}

.meta-item .el-icon {
  margin-right: 4px;
  color: #909399;
}

.report-actions {
  display: flex;
  gap: 12px;
}

.stats-overview {
  margin-bottom: 24px;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.1);
  border: none;
}

.stats-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 24px;
}

.stat-item {
  display: flex;
  align-items: center;
  gap: 16px;
  padding: 16px;
  background: #f8f9fa;
  border-radius: 8px;
}

.stat-icon {
  width: 48px;
  height: 48px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 20px;
  color: white;
}

.stat-icon.assignments {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
}

.stat-icon.score {
  background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
}

.stat-icon.questions {
  background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%);
}

.stat-icon.completion {
  background: linear-gradient(135deg, #43e97b 0%, #38f9d7 100%);
}

.stat-content {
  flex: 1;
}

.stat-number {
  font-size: 24px;
  font-weight: bold;
  color: #303133;
  line-height: 1;
  margin-bottom: 4px;
}

.stat-label {
  color: #606266;
  font-size: 14px;
  margin-bottom: 2px;
}

.stat-detail {
  color: #909399;
  font-size: 12px;
}

.report-content-card {
  margin-bottom: 24px;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.1);
  border: none;
}

.report-text {
  line-height: 1.8;
  color: #303133;
  font-size: 15px;
}

.report-text :deep(.markdown-content) {
  margin: 0;
}

.report-text :deep(.markdown-content strong) {
  color: #409eff;
  font-weight: 600;
}

.report-text :deep(.markdown-content em) {
  color: #e6a23c;
  font-style: normal;
  background: #fdf6ec;
  padding: 2px 4px;
  border-radius: 3px;
}

.report-footer {
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.1);
  border: none;
}

.generation-info {
  display: flex;
  justify-content: space-between;
  align-items: center;
  color: #909399;
  font-size: 14px;
}

/* 打印样式 */
@media print {
  .report-detail-container {
    padding: 0;
    background: white;
  }

  .back-button,
  .report-actions {
    display: none;
  }

  .report-content {
    max-width: none;
  }

  .el-card {
    box-shadow: none !important;
    border: 1px solid #ddd !important;
  }
}

/* 响应式设计 */
@media (max-width: 768px) {
  .report-detail-container {
    padding: 16px;
  }

  .report-header-info {
    flex-direction: column;
    gap: 16px;
  }

  .meta-info {
    flex-direction: column;
    gap: 8px;
  }

  .stats-grid {
    grid-template-columns: 1fr;
  }

  .stat-item {
    flex-direction: column;
    text-align: center;
    gap: 8px;
  }

  .report-actions {
    flex-direction: column;
    width: 100%;
  }
}
</style>
