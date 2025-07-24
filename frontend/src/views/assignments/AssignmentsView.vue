<template>
  <div class="assignments">
    <!-- 页面头部 -->
    <div class="page-header">
      <h1>作业管理</h1>
      <div class="header-actions">
        <!-- 教师可以创建作业 -->
        <el-button
          v-if="authStore.isTeacher"
          type="primary"
          @click="handleCreateAssignment"
        >
          <el-icon><Plus /></el-icon>
          创建作业
        </el-button>

        <!-- 刷新按钮 -->
        <el-button @click="fetchAssignments">
          <el-icon><Refresh /></el-icon>
          刷新
        </el-button>
      </div>
    </div>

    <!-- 筛选条件 -->
    <div class="filters">
      <el-form :model="filters" inline>
        <el-form-item label="科目">
          <el-input
            v-model="filters.subject"
            placeholder="输入科目名称"
            clearable
            @change="handleFilterChange"
          />
        </el-form-item>

        <el-form-item v-if="authStore.isStudent" label="完成状态">
          <el-select
            v-model="filters.completion_status"
            placeholder="选择状态"
            clearable
            @change="handleFilterChange"
          >
            <el-option label="未完成" value="pending" />
            <el-option label="已完成" value="completed" />
          </el-select>
        </el-form-item>
      </el-form>
    </div>

    <!-- 作业列表 -->
    <div class="assignments-content">
      <div v-if="assignmentsStore.loading" class="loading">
        <el-icon class="is-loading" size="32"><Loading /></el-icon>
        <p>加载中...</p>
      </div>

      <div v-else-if="assignmentsStore.assignments.length === 0" class="empty">
        <el-empty description="暂无作业" />
      </div>

      <div v-else class="assignments-grid">
        <div
          v-for="assignment in assignmentsStore.assignments"
          :key="assignment.id"
          class="assignment-card"
          @click="handleViewAssignment(assignment.id)"
        >
          <div class="card-header">
            <h3>{{ assignment.title }}</h3>
            <div class="header-tags">
              <el-tag
                v-if="authStore.isStudent && assignment.is_completed !== null"
                :type="assignment.is_completed ? 'success' : 'info'"
                size="small"
              >
                {{ assignment.is_completed ? '已完成' : '未完成' }}
              </el-tag>
              <el-tag :type="getDeadlineType(assignment.deadline)">
                {{ formatDeadline(assignment.deadline) }}
              </el-tag>
            </div>
          </div>

          <div class="card-content">
            <p class="description">{{ assignment.description }}</p>
            <div class="meta-info">
              <span class="subject">{{ assignment.subject }}</span>
              <span class="score">总分：{{ assignment.total_score }}分</span>
            </div>
          </div>

          <div class="card-footer">
            <span class="created-time">
              {{ formatDateTime(assignment.created_at) }}
            </span>
            <div class="actions">
              <el-button size="small" type="primary">
                {{ authStore.isTeacher ? '查看详情' : '进入作业' }}
              </el-button>
            </div>
          </div>
        </div>
      </div>

      <!-- 分页组件 -->
      <div v-if="paginationData && paginationData.total > 0" class="pagination-wrapper">
        <el-pagination
          v-model:current-page="currentPage"
          v-model:page-size="pageSize"
          :page-sizes="[10, 20, 50]"
          :total="paginationData.total"
          layout="total, sizes, prev, pager, next, jumper"
          @size-change="handleSizeChange"
          @current-change="handleCurrentChange"
        />
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { reactive, ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore, useAssignmentsStore } from '@/stores'
import { formatDateTime } from '@/utils'
import { Plus, Refresh, Loading } from '@element-plus/icons-vue'

const router = useRouter()
const authStore = useAuthStore()
const assignmentsStore = useAssignmentsStore()

// 分页参数
const currentPage = ref(1)
const pageSize = ref(10)

// 筛选条件
const filters = reactive({
  subject: '',
  completion_status: ''
})

// 分页数据
const paginationData = computed(() => assignmentsStore.pagination)

// 获取作业列表
const fetchAssignments = async () => {
  const params: any = {
    page: currentPage.value,
    page_size: pageSize.value
  }
  if (filters.subject) params.subject = filters.subject
  if (filters.completion_status) params.completion_status = filters.completion_status

  await assignmentsStore.fetchAssignments(params)
}

// 分页大小改变
const handleSizeChange = (size: number) => {
  pageSize.value = size
  currentPage.value = 1
  fetchAssignments()
}

// 当前页改变
const handleCurrentChange = (page: number) => {
  currentPage.value = page
  fetchAssignments()
}

// 筛选条件改变
const handleFilterChange = () => {
  currentPage.value = 1
  fetchAssignments()
}

// 创建作业（教师）
const handleCreateAssignment = () => {
  // 暂时跳转到一个提示页面，后续会实现创建页面
  router.push('/assignments/create')
}

// 查看作业详情
const handleViewAssignment = (assignmentId: string) => {
  router.push(`/assignments/${assignmentId}`)
}

// 格式化截止时间
const formatDeadline = (deadline: string) => {
  const now = new Date()
  const deadlineDate = new Date(deadline)
  const diff = deadlineDate.getTime() - now.getTime()
  const days = Math.floor(diff / (1000 * 60 * 60 * 24))
  const hours = Math.floor(diff / (1000 * 60 * 60))

  if (diff < 0) return '已过期'
  if (hours < 24) return `${hours}小时后截止`
  return `${days}天后截止`
}

// 获取截止时间标签类型
const getDeadlineType = (deadline: string) => {
  const now = new Date()
  const deadlineDate = new Date(deadline)
  const diff = deadlineDate.getTime() - now.getTime()
  const hours = Math.floor(diff / (1000 * 60 * 60))

  if (diff < 0) return 'danger'
  if (hours < 24) return 'warning'
  return 'success'
}

// 页面加载时获取作业列表
onMounted(() => {
  fetchAssignments()
})
</script>

<style scoped>
.assignments {
  padding: 24px;
  max-width: 1200px;
  margin: 0 auto;
}

.page-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 24px;
}

.page-header h1 {
  margin: 0;
  color: #303133;
  font-size: 24px;
  font-weight: 500;
}

.header-actions {
  display: flex;
  gap: 12px;
}

.filters {
  background: white;
  padding: 20px;
  border-radius: 8px;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.1);
  margin-bottom: 24px;
}

.assignments-content {
  min-height: 400px;
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

.empty {
  background: white;
  border-radius: 8px;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.1);
  padding: 40px;
}

.assignments-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(350px, 1fr));
  gap: 20px;
}

.assignment-card {
  background: white;
  border-radius: 8px;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.1);
  padding: 20px;
  cursor: pointer;
  transition: all 0.3s ease;
}

.assignment-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.15);
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 16px;
}

.card-header h3 {
  margin: 0;
  color: #303133;
  font-size: 18px;
  font-weight: 500;
  flex: 1;
  margin-right: 12px;
}

.header-tags {
  display: flex;
  flex-direction: column;
  gap: 6px;
  align-items: flex-end;
}

.card-content {
  margin-bottom: 16px;
}

.description {
  color: #606266;
  font-size: 14px;
  line-height: 1.5;
  margin: 0 0 12px 0;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
}

.meta-info {
  display: flex;
  justify-content: space-between;
  align-items: center;
  font-size: 12px;
  color: #909399;
}

.card-footer {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding-top: 16px;
  border-top: 1px solid #ebeef5;
}

.created-time {
  font-size: 12px;
  color: #909399;
}

.pagination-wrapper {
  display: flex;
  justify-content: center;
  margin-top: 32px;
  padding: 24px;
  background: white;
  border-radius: 8px;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.1);
}

@media (max-width: 768px) {
  .assignments-grid {
    grid-template-columns: 1fr;
  }

  .pagination-wrapper {
    padding: 16px;
  }
}
</style>
