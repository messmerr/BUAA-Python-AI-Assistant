<template>
  <div class="assignment-detail">
    <!-- 加载状态 -->
    <div v-if="assignmentsStore.loading" class="loading">
      <el-icon class="is-loading" size="32"><Loading /></el-icon>
      <p>加载中...</p>
    </div>

    <!-- 作业详情 -->
    <div v-else-if="assignment" class="assignment-content">
      <!-- 作业头部信息 -->
      <div class="assignment-header">
        <div class="header-info">
          <h1>{{ assignment.title }}</h1>
          <div class="meta-info">
            <el-tag :type="getDeadlineType(assignment.deadline)">
              {{ formatDeadline(assignment.deadline) }}
            </el-tag>
            <span class="subject">{{ assignment.subject }}</span>
            <span class="score">总分：{{ assignment.total_score }}分</span>
          </div>
          <p class="description">{{ assignment.description }}</p>
        </div>

        <!-- 操作按钮 -->
        <div class="header-actions">
          <!-- 学生视角 -->
          <template v-if="authStore.isStudent">
            <el-button 
              v-if="!assignment.is_completed" 
              type="primary" 
              size="large"
              @click="startAssignment"
            >
              开始作业
            </el-button>
            <el-button 
              v-else 
              type="success" 
              size="large"
              @click="viewResult"
            >
              查看批改结果
            </el-button>
          </template>

          <!-- 教师视角 -->
          <template v-if="authStore.isTeacher">
            <el-button @click="viewSubmissions">
              查看提交情况
            </el-button>
            <el-button type="primary" @click="editAssignment">
              编辑作业
            </el-button>
          </template>
        </div>
      </div>

      <!-- 题目列表 -->
      <div class="questions-section">
        <h2>题目列表</h2>
        <div class="questions-list">
          <div 
            v-for="(question, index) in assignment.questions" 
            :key="question.id"
            class="question-card"
          >
            <div class="question-header">
              <span class="question-number">第{{ index + 1 }}题</span>
              <span class="question-score">{{ question.score }}分</span>
            </div>
            <div class="question-content">
              <p>{{ question.question_text }}</p>
            </div>
          </div>
        </div>
      </div>

      <!-- 学生完成状态 -->
      <div v-if="authStore.isStudent && assignment.is_completed" class="completion-info">
        <el-alert
          title="作业已完成"
          :description="`您的得分：${assignment.obtained_score || 0}/${assignment.total_score}分`"
          type="success"
          show-icon
          :closable="false"
        />
      </div>
    </div>

    <!-- 错误状态 -->
    <div v-else class="error-state">
      <el-result
        icon="warning"
        title="作业不存在"
        sub-title="请检查作业ID是否正确"
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
import { ref, computed, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useAuthStore, useAssignmentsStore } from '@/stores'
import { Loading } from '@element-plus/icons-vue'

const route = useRoute()
const router = useRouter()
const authStore = useAuthStore()
const assignmentsStore = useAssignmentsStore()

// 当前作业
const assignment = computed(() => assignmentsStore.currentAssignment)

// 获取作业详情
const fetchAssignmentDetail = async () => {
  const assignmentId = route.params.id as string
  try {
    await assignmentsStore.fetchAssignmentDetail(assignmentId)
  } catch (error) {
    console.error('获取作业详情失败:', error)
  }
}

// 开始作业（学生）
const startAssignment = () => {
  const assignmentId = route.params.id as string
  router.push(`/assignments/${assignmentId}/submit`)
}

// 查看批改结果（学生）
const viewResult = () => {
  const assignmentId = route.params.id as string
  // 这里需要获取学生的提交ID，暂时使用作业ID
  router.push(`/assignments/${assignmentId}/result`)
}

// 查看提交情况（教师）
const viewSubmissions = () => {
  const assignmentId = route.params.id as string
  router.push(`/assignments/${assignmentId}/submissions`)
}

// 编辑作业（教师）
const editAssignment = () => {
  const assignmentId = route.params.id as string
  router.push(`/assignments/${assignmentId}/edit`)
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

// 页面加载时获取作业详情
onMounted(() => {
  fetchAssignmentDetail()
})
</script>

<style scoped>
.assignment-detail {
  padding: 24px;
  max-width: 1000px;
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

.assignment-content {
  background: white;
  border-radius: 8px;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.1);
  overflow: hidden;
}

.assignment-header {
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

.meta-info {
  display: flex;
  align-items: center;
  gap: 16px;
  margin-bottom: 16px;
  font-size: 14px;
  color: #606266;
}

.description {
  margin: 0;
  color: #606266;
  line-height: 1.6;
}

.header-actions {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.questions-section {
  padding: 32px;
}

.questions-section h2 {
  margin: 0 0 24px 0;
  color: #303133;
  font-size: 20px;
  font-weight: 500;
}

.questions-list {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.question-card {
  border: 1px solid #ebeef5;
  border-radius: 8px;
  padding: 20px;
  background: #fafafa;
}

.question-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 12px;
}

.question-number {
  font-weight: 500;
  color: #409eff;
}

.question-score {
  color: #e6a23c;
  font-weight: 500;
}

.question-content p {
  margin: 0;
  color: #303133;
  line-height: 1.6;
}

.completion-info {
  padding: 32px;
  border-top: 1px solid #ebeef5;
}

.error-state {
  background: white;
  border-radius: 8px;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.1);
  padding: 40px;
}
</style>
