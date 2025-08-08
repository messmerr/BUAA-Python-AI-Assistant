<template>
  <div class="assignment-submissions">
    <!-- 加载状态 -->
    <div v-if="assignmentsStore.loading" class="loading">
      <el-icon class="is-loading" size="32"><Loading /></el-icon>
      <p>加载中...</p>
    </div>

    <!-- 提交情况展示 -->
    <div v-else-if="submissionsData" class="submissions-content">
      <!-- 页面头部 -->
      <div class="page-header">
        <div class="header-info">
          <h1>{{ submissionsData.assignment_info.title }} - 提交情况</h1>
          <div class="stats-info">
            <el-tag type="info" size="large">
              总分：{{ submissionsData.assignment_info.total_score }}分
            </el-tag>
            <el-tag type="success" size="large">
              已提交：{{ submissionsData.assignment_info.submission_count }}人
            </el-tag>
            <el-tag type="warning" size="large">
              截止时间：{{ formatDateTime(submissionsData.assignment_info.deadline) }}
            </el-tag>
          </div>
        </div>
        
        <div class="header-actions">
          <el-button @click="$router.back()">返回</el-button>
          <el-button type="primary" @click="refreshData">
            <el-icon><Refresh /></el-icon>
            刷新
          </el-button>
        </div>
      </div>

      <!-- 筛选和搜索 -->
      <div class="filters">
        <el-input
          v-model="searchStudent"
          placeholder="搜索学生姓名或用户名"
          style="width: 300px"
          clearable
          @input="handleSearch"
        >
          <template #prefix>
            <el-icon><Search /></el-icon>
          </template>
        </el-input>
      </div>

      <!-- 提交列表 -->
      <div class="submissions-table">
        <el-table 
          :data="submissionsData.submissions" 
          stripe
          style="width: 100%"
          empty-text="暂无提交记录"
        >
          <el-table-column prop="student_name" label="学生姓名">
            <template #default="{ row }">
              <div class="student-info">
                <div class="name">{{ row.student_name }}</div>
                <div class="username">@{{ row.student_username }}</div>
              </div>
            </template>
          </el-table-column>
          
          <el-table-column prop="status" label="状态">
            <template #default="{ row }">
              <el-tag :type="getStatusType(row.status)">
                {{ getStatusText(row.status) }}
              </el-tag>
            </template>
          </el-table-column>
          
          <el-table-column prop="obtained_score" label="得分">
            <template #default="{ row }">
              <div class="score-info">
                <span class="score">{{ row.obtained_score }}/{{ row.total_score }}</span>
                <el-tag 
                  size="small" 
                  :type="getScoreType(row.obtained_score, row.total_score)"
                >
                  {{ getScorePercentage(row.obtained_score, row.total_score) }}%
                </el-tag>
              </div>
            </template>
          </el-table-column>
          
          <el-table-column prop="submitted_at" label="提交时间">
            <template #default="{ row }">
              {{ formatDateTime(row.submitted_at) }}
            </template>
          </el-table-column>
          
          <el-table-column prop="graded_at" label="批改时间">
            <template #default="{ row }">
              {{ row.graded_at ? formatDateTime(row.graded_at) : '-' }}
            </template>
          </el-table-column>
          

        </el-table>

        <!-- 分页 -->
        <div class="pagination">
          <el-pagination
            v-model:current-page="currentPage"
            v-model:page-size="pageSize"
            :page-sizes="[10, 20, 50]"
            :total="submissionsData.pagination.total"
            layout="total, sizes, prev, pager, next, jumper"
            @size-change="handleSizeChange"
            @current-change="handleCurrentChange"
          />
        </div>
      </div>
    </div>

    <!-- 错误状态 -->
    <div v-else class="error-state">
      <el-result
        icon="warning"
        title="无法获取提交情况"
        sub-title="请检查作业是否存在或您是否有权限查看"
      >
        <template #extra>
          <el-button type="primary" @click="$router.push('/assignments')">
            返回作业列表
          </el-button>
        </template>
      </el-result>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useRoute } from 'vue-router'
import { useAssignmentsStore } from '@/stores'
import { formatDateTime } from '@/utils'
import { Loading, Refresh, Search } from '@element-plus/icons-vue'

const route = useRoute()
const assignmentsStore = useAssignmentsStore()

// 分页参数
const currentPage = ref(1)
const pageSize = ref(10)
const searchStudent = ref('')

// 提交数据
const submissionsData = ref<any>(null)

// 获取提交列表
const fetchSubmissions = async () => {
  const assignmentId = route.params.id as string
  try {
    const params = {
      page: currentPage.value,
      page_size: pageSize.value,
      student: searchStudent.value || undefined
    }
    const response = await assignmentsStore.fetchSubmissions(assignmentId, params)
    submissionsData.value = response
  } catch (error) {
    console.error('获取提交列表失败:', error)
  }
}

// 刷新数据
const refreshData = () => {
  fetchSubmissions()
}

// 搜索处理
const handleSearch = () => {
  currentPage.value = 1
  fetchSubmissions()
}

// 分页处理
const handleSizeChange = (size: number) => {
  pageSize.value = size
  currentPage.value = 1
  fetchSubmissions()
}

const handleCurrentChange = (page: number) => {
  currentPage.value = page
  fetchSubmissions()
}



// 获取状态类型
const getStatusType = (status: string) => {
  switch (status) {
    case 'submitted': return 'info'
    case 'grading': return 'warning'
    case 'graded': return 'success'
    default: return 'info'
  }
}

// 获取状态文本
const getStatusText = (status: string) => {
  switch (status) {
    case 'submitted': return '已提交'
    case 'grading': return '批改中'
    case 'graded': return '已批改'
    default: return '未知'
  }
}

// 计算分数百分比
const getScorePercentage = (obtained: number, total: number): number => {
  if (total === 0) return 0
  return Math.round((obtained / total) * 100)
}

// 获取分数标签类型
const getScoreType = (obtained: number, total: number): string => {
  const percentage = getScorePercentage(obtained, total)
  if (percentage >= 90) return 'success'
  if (percentage >= 70) return 'warning'
  return 'danger'
}

// 页面加载时获取数据
onMounted(() => {
  fetchSubmissions()
})
</script>

<style scoped>
.assignment-submissions {
  padding: 24px;
  max-width: 100%;
  margin: 0 auto;
}

.loading {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 60px;
  color: #606266;
}

.loading p {
  margin-top: 12px;
}

.submissions-content {
  background: white;
  border-radius: 8px;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.1);
  overflow: hidden;
}

.page-header {
  padding: 32px;
  border-bottom: 1px solid #ebeef5;
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
}

.header-info {
  flex: 1;
  margin-right: 24px;
}

.header-info h1 {
  margin: 0 0 16px 0;
  color: #303133;
  font-size: 24px;
  font-weight: 500;
}

.stats-info {
  display: flex;
  gap: 12px;
  flex-wrap: wrap;
}

.header-actions {
  display: flex;
  gap: 12px;
}

.filters {
  padding: 24px 32px;
  border-bottom: 1px solid #ebeef5;
  background: #fafafa;
}

.submissions-table {
  padding: 32px;
}

.student-info .name {
  font-weight: 500;
  color: #303133;
}

.student-info .username {
  font-size: 12px;
  color: #909399;
  margin-top: 2px;
}

.score-info {
  display: flex;
  align-items: center;
  gap: 8px;
}

.score-info .score {
  font-weight: 500;
  color: #303133;
}

.pagination {
  display: flex;
  justify-content: center;
  margin-top: 24px;
  padding-top: 24px;
  border-top: 1px solid #ebeef5;
}

.error-state {
  background: white;
  border-radius: 8px;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.1);
  padding: 40px;
}

/* 表格样式调整 */
.el-table {
  border-radius: 8px;
  overflow: hidden;
}

.el-table th {
  background: #f8f9fa;
  color: #303133;
  font-weight: 500;
}

.el-table td {
  border-bottom: 1px solid #f0f0f0;
}

.el-table tr:hover td {
  background: #f8f9fa;
}

@media (max-width: 768px) {
  .page-header {
    flex-direction: column;
    gap: 20px;
  }

  .header-info {
    margin-right: 0;
  }

  .stats-info {
    flex-direction: column;
    align-items: flex-start;
  }

  .filters {
    padding: 16px;
  }

  .submissions-table {
    padding: 16px;
    overflow-x: auto;
  }
}
</style>
