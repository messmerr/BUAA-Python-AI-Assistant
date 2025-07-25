<template>
  <div class="assignment-result">
    <!-- 加载状态 -->
    <div v-if="assignmentsStore.loading" class="loading">
      <el-icon class="is-loading" size="32"><Loading /></el-icon>
      <p>加载中...</p>
    </div>

    <!-- 批改结果展示 -->
    <div v-else-if="result" class="result-content">
      <!-- 结果头部 -->
      <div class="result-header">
        <div class="header-info">
          <h1>{{ result.assignment_title }}</h1>
          <div class="score-info">
            <div class="total-score">
              <span class="score-label">总分：</span>
              <span class="score-value">{{ result.obtained_score }}/{{ result.total_score }}</span>
              <el-tag 
                :type="getScoreType(result.obtained_score, result.total_score)"
                size="large"
              >
                {{ getScorePercentage(result.obtained_score, result.total_score) }}%
              </el-tag>
            </div>
            <div class="time-info">
              <span>提交时间：{{ formatDateTime(result.submitted_at) }}</span>
              <span>批改时间：{{ formatDateTime(result.graded_at) }}</span>
            </div>
          </div>
        </div>
        
        <div class="header-actions">
          <el-button @click="$router.back()">返回</el-button>
          <el-button type="primary" @click="$router.push('/assignments')">
            作业列表
          </el-button>
        </div>
      </div>

      <!-- 总体评价 -->
      <div v-if="result.overall_feedback" class="overall-feedback">
        <h3>总体评价</h3>
        <div class="feedback-content">
          <el-alert
            :title="result.overall_feedback"
            type="info"
            :closable="false"
            show-icon
          />
        </div>
      </div>

      <!-- 题目详细批改结果 -->
      <div class="questions-results">
        <h3>题目详情</h3>
        <div class="questions-list">
          <div 
            v-for="(answer, index) in result.answers" 
            :key="answer.id"
            class="question-result-card"
          >
            <!-- 题目头部 -->
            <div class="question-header">
              <div class="question-info">
                <span class="question-number">第{{ index + 1 }}题</span>
                <span class="question-score">
                  {{ answer.obtained_score }}/{{ answer.question_score }}分
                </span>
              </div>
              <el-tag 
                :type="getQuestionScoreType(answer.obtained_score, answer.question_score)"
              >
                {{ getScorePercentage(answer.obtained_score, answer.question_score) }}%
              </el-tag>
            </div>

            <!-- 题目内容 -->
            <div class="question-content">
              <div class="question-text">
                <h4>题目：</h4>
                <div class="question-markdown">
                  <MarkdownRenderer :content="answer.question_text" compact />
                </div>
              </div>

              <!-- 答案对比 -->
              <div class="answers-comparison">
                <div class="student-answer">
                  <h4>您的答案：</h4>
                  <div class="answer-box student">
                    <MarkdownRenderer :content="answer.student_answer" compact />
                  </div>
                </div>

                <div class="reference-answer">
                  <h4>参考答案：</h4>
                  <div class="answer-box reference">
                    <MarkdownRenderer :content="answer.reference_answer" compact />
                  </div>
                </div>
              </div>

              <!-- AI反馈 -->
              <div v-if="answer.ai_feedback" class="ai-feedback">
                <h4>AI评价：</h4>
                <div class="feedback-box">
                  <el-icon class="feedback-icon"><ChatDotRound /></el-icon>
                  <div class="feedback-content">
                    <MarkdownRenderer :content="answer.ai_feedback" compact />
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- 错误状态 -->
    <div v-else class="error-state">
      <el-result
        icon="warning"
        title="批改结果不存在"
        sub-title="作业可能尚未提交或批改，请检查作业状态"
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
import { computed, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useAssignmentsStore } from '@/stores'
import { formatDateTime } from '@/utils'
import { Loading, ChatDotRound } from '@element-plus/icons-vue'
import MarkdownRenderer from '@/components/common/MarkdownRenderer.vue'

const route = useRoute()
const router = useRouter()
const assignmentsStore = useAssignmentsStore()

// 批改结果
const result = computed(() => assignmentsStore.currentSubmission)

// 获取批改结果
const fetchResult = async () => {
  const assignmentId = route.params.id as string
  try {
    await assignmentsStore.fetchAssignmentResult(assignmentId)
  } catch (error) {
    console.error('获取批改结果失败:', error)
  }
}

// 计算分数百分比
const getScorePercentage = (obtained: number, total: number): number => {
  if (total === 0) return 0
  return Math.round((obtained / total) * 100)
}

// 获取总分标签类型
const getScoreType = (obtained: number, total: number): string => {
  const percentage = getScorePercentage(obtained, total)
  if (percentage >= 90) return 'success'
  if (percentage >= 70) return 'warning'
  return 'danger'
}

// 获取单题分数标签类型
const getQuestionScoreType = (obtained: number, total: number): string => {
  const percentage = getScorePercentage(obtained, total)
  if (percentage >= 80) return 'success'
  if (percentage >= 60) return 'warning'
  return 'danger'
}

// 页面加载时获取批改结果
onMounted(() => {
  fetchResult()
})
</script>

<style scoped>
.assignment-result {
  padding: 24px;
  max-width: 1200px;
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

.result-content {
  background: white;
  border-radius: 8px;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.1);
  overflow: hidden;
}

.result-header {
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
  margin: 0 0 20px 0;
  color: #303133;
  font-size: 24px;
  font-weight: 500;
}

.score-info {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.total-score {
  display: flex;
  align-items: center;
  gap: 12px;
}

.score-label {
  font-size: 16px;
  color: #606266;
}

.score-value {
  font-size: 24px;
  font-weight: bold;
  color: #303133;
}

.time-info {
  display: flex;
  gap: 24px;
  font-size: 14px;
  color: #909399;
}

.header-actions {
  display: flex;
  gap: 12px;
}

.overall-feedback {
  padding: 32px;
  border-bottom: 1px solid #ebeef5;
}

.overall-feedback h3 {
  margin: 0 0 16px 0;
  color: #303133;
  font-size: 18px;
  font-weight: 500;
}

.questions-results {
  padding: 32px;
}

.questions-results h3 {
  margin: 0 0 24px 0;
  color: #303133;
  font-size: 18px;
  font-weight: 500;
}

.questions-list {
  display: flex;
  flex-direction: column;
  gap: 24px;
}

.question-result-card {
  border: 1px solid #ebeef5;
  border-radius: 8px;
  padding: 24px;
  background: #fafafa;
}

.question-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
}

.question-info {
  display: flex;
  align-items: center;
  gap: 16px;
}

.question-number {
  font-weight: 500;
  color: #409eff;
  font-size: 16px;
}

.question-score {
  font-weight: 500;
  color: #303133;
}

.question-content {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.question-text h4,
.answers-comparison h4,
.ai-feedback h4 {
  margin: 0 0 8px 0;
  color: #303133;
  font-size: 14px;
  font-weight: 500;
}

.question-markdown {
  background: white;
  padding: 16px;
  border-radius: 6px;
  border: 1px solid #e4e7ed;
}

.question-markdown :deep(.markdown-content) {
  margin: 0;
  color: #303133;
  line-height: 1.6;
}

.answers-comparison {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 20px;
}

.answer-box {
  background: white;
  border: 1px solid #e4e7ed;
  border-radius: 6px;
  padding: 16px;
  min-height: 120px;
}

.answer-box.student {
  border-left: 4px solid #409eff;
}

.answer-box.reference {
  border-left: 4px solid #67c23a;
}

.answer-box :deep(.markdown-content) {
  margin: 0;
  color: #303133;
  line-height: 1.6;
}

.ai-feedback {
  background: white;
  border-radius: 6px;
  border: 1px solid #e4e7ed;
  padding: 16px;
}

.feedback-box {
  display: flex;
  align-items: flex-start;
  gap: 12px;
}

.feedback-content {
  flex: 1;
}

.feedback-content :deep(.markdown-content) {
  margin: 0;
  color: #303133;
  line-height: 1.6;
}

.feedback-icon {
  color: #409eff;
  margin-top: 2px;
  flex-shrink: 0;
}

.feedback-box p {
  margin: 0;
  line-height: 1.6;
  color: #303133;
}

.error-state {
  background: white;
  border-radius: 8px;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.1);
  padding: 40px;
}

@media (max-width: 768px) {
  .answers-comparison {
    grid-template-columns: 1fr;
  }
  
  .result-header {
    flex-direction: column;
    gap: 20px;
  }
  
  .header-info {
    margin-right: 0;
  }
}
</style>
