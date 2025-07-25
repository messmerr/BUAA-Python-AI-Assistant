<template>
  <div class="submit-assignment">
    <!-- 加载状态 -->
    <div v-if="assignmentsStore.loading" class="loading">
      <el-icon class="is-loading" size="32"><Loading /></el-icon>
      <p>加载中...</p>
    </div>

    <!-- 调试信息 -->
    <div v-if="!assignmentsStore.loading && !assignment" class="debug-info">
      <p>调试信息：</p>
      <p>Loading: {{ assignmentsStore.loading }}</p>
      <p>Assignment: {{ assignment }}</p>
      <p>Route ID: {{ route.params.id }}</p>
    </div>

    <!-- 作业提交界面 -->
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
          <div class="description">
            <MarkdownRenderer :content="assignment.description" />
          </div>
        </div>

        <div class="header-actions">
          <el-button @click="$router.back()">返回</el-button>
          <el-button
            type="primary"
            :loading="submitting"
            :disabled="!canSubmit"
            @click="handleSubmit"
          >
            {{ submitting ? 'AI批改中，请稍候...' : '提交作业' }}
          </el-button>
        </div>
      </div>

      <!-- 答题区域 -->
      <div class="questions-section">
        <el-form ref="formRef" :model="submissionForm" label-width="0">
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
              <div class="question-text">
                <h4>题目：</h4>
                <div class="question-markdown">
                  <MarkdownRenderer :content="question.question_text" compact />
                </div>
              </div>

              <div class="answer-input">
                <h4>答案：</h4>
                <el-form-item
                  v-if="submissionForm.answers[index]"
                  :prop="`answers.${index}.answer_text`"
                  :rules="[{ required: true, message: '请输入答案', trigger: 'blur' }]"
                >
                  <el-input
                    v-model="submissionForm.answers[index].answer_text"
                    type="textarea"
                    :rows="6"
                    placeholder="请在此输入您的答案..."
                    maxlength="2000"
                    show-word-limit
                  />
                </el-form-item>
              </div>
            </div>
          </div>
        </el-form>
      </div>

      <!-- 提交确认 -->
      <div class="submit-section">
        <el-alert
          title="提交提醒"
          description="请仔细检查您的答案，作业提交后将自动进行AI批改，无法修改。AI批改可能需要30-60秒，请耐心等待。"
          type="warning"
          show-icon
          :closable="false"
        />

        <!-- 提交中的额外提示 -->
        <el-alert
          v-if="submitting"
          title="正在处理"
          description="AI正在批改您的作业，请不要关闭页面或刷新浏览器..."
          type="info"
          show-icon
          :closable="false"
        />
        
        <div class="submit-actions">
          <el-button size="large" @click="$router.back()">
            取消提交
          </el-button>
          <el-button
            type="primary"
            size="large"
            :loading="submitting"
            :disabled="!canSubmit"
            @click="handleSubmit"
          >
            {{ submitting ? 'AI批改中，请稍候...' : '确认提交' }}
          </el-button>
        </div>
      </div>
    </div>

    <!-- 已提交状态 -->
    <div v-else-if="assignment && assignment.is_completed" class="completed-state">
      <el-result
        icon="success"
        title="作业已提交"
        sub-title="您已经提交过这个作业，无需重复提交"
      >
        <template #extra>
          <el-button type="primary" @click="$router.push(`/assignments/${route.params.id}`)">
            查看批改结果
          </el-button>
          <el-button @click="$router.push('/assignments')">
            返回作业列表
          </el-button>
        </template>
      </el-result>
    </div>

    <!-- 错误状态 -->
    <div v-else class="error-state">
      <el-result
        icon="warning"
        title="作业不存在或已过期"
        sub-title="请检查作业是否存在或是否已过截止时间"
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
import { ref, reactive, computed, onMounted, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useAssignmentsStore } from '@/stores'
import { Loading } from '@element-plus/icons-vue'
import type { FormInstance } from 'element-plus'
import { ElMessage, ElMessageBox } from 'element-plus'
import MarkdownRenderer from '@/components/common/MarkdownRenderer.vue'

const route = useRoute()
const router = useRouter()
const assignmentsStore = useAssignmentsStore()

// 表单引用
const formRef = ref<FormInstance>()

// 当前作业
const assignment = computed(() => assignmentsStore.currentAssignment)

// 提交状态
const submitting = ref(false)

// 提交表单数据
const submissionForm = reactive({
  answers: [] as Array<{
    question_id: string
    answer_text: string
  }>
})

// 是否可以提交
const canSubmit = computed(() => {
  if (!assignment.value) return false
  
  // 检查是否已过截止时间
  const now = new Date()
  const deadline = new Date(assignment.value.deadline)
  if (now > deadline) return false
  
  // 检查是否所有题目都有答案
  return submissionForm.answers.every(answer => answer.answer_text.trim().length > 0)
})

// 初始化答案数组
const initializeAnswers = () => {
  if (assignment.value?.questions) {
    submissionForm.answers = assignment.value.questions.map(question => ({
      question_id: question.id,
      answer_text: ''
    }))
    console.log('答案数组初始化完成:', submissionForm.answers)
  }
}

// 获取作业详情
const fetchAssignmentDetail = async () => {
  const assignmentId = route.params.id as string
  console.log('获取作业详情，ID:', assignmentId)

  if (!assignmentId) {
    console.error('作业ID不存在')
    return
  }

  try {
    await assignmentsStore.fetchAssignmentDetail(assignmentId)
    console.log('作业详情获取成功:', assignment.value)

    // 初始化答案数组
    initializeAnswers()
  } catch (error) {
    console.error('获取作业详情失败:', error)
  }
}

// 提交作业
const handleSubmit = async () => {
  if (!formRef.value || !assignment.value) return

  // 表单验证
  const valid = await formRef.value.validate().catch(() => false)
  if (!valid) return

  // 检查截止时间
  const now = new Date()
  const deadline = new Date(assignment.value.deadline)
  if (now > deadline) {
    ElMessage.error('作业已过截止时间，无法提交')
    return
  }

  try {
    // 确认提交
    await ElMessageBox.confirm(
      '确定要提交作业吗？提交后将无法修改。',
      '确认提交',
      {
        confirmButtonText: '确定提交',
        cancelButtonText: '再检查一下',
        type: 'warning'
      }
    )

    submitting.value = true

    const assignmentId = route.params.id as string
    const submitData = {
      answers: submissionForm.answers
    }

    console.log('提交数据:', submitData)
    console.log('作业ID:', assignmentId)
    console.log('答案详情:', submissionForm.answers)

    const result = await assignmentsStore.submitAssignment(assignmentId, submitData)

    if (result) {
      ElMessage.success('作业提交成功，AI批改完成！')
      // 跳转到作业详情页面
      router.push(`/assignments/${assignmentId}`)
    }
  } catch (error: any) {
    if (error !== 'cancel') {
      console.error('提交作业失败:', error)

      // 根据错误类型显示不同的提示
      if (error.code === 'ECONNABORTED') {
        ElMessage.error('AI批改超时，但作业可能已提交成功，请刷新页面查看状态')
      } else if (error.response?.status === 400) {
        const errorMessage = error.response.data?.message || ''
        const errorDetails = error.response.data?.errors || {}

        // 检查是否是重复提交错误
        if (errorMessage.includes('已经提交过') ||
            errorMessage.includes('重复提交') ||
            JSON.stringify(errorDetails).includes('已经提交过')) {
          ElMessage.warning({
            message: '您已经提交过这个作业了，无需重复提交。如需查看批改结果，请返回作业详情页面。',
            duration: 5000
          })
          // 自动跳转到作业详情页面
          setTimeout(() => {
            router.push(`/assignments/${route.params.id}`)
          }, 2000)
        } else if (errorMessage.includes('截止时间')) {
          ElMessage.error('提交失败：作业已过截止时间')
        } else if (errorMessage.includes('至少需要提交一个答案')) {
          ElMessage.error('提交失败：请至少回答一道题目')
        } else {
          ElMessage.error('提交失败：' + (errorMessage || '请检查答案格式'))
        }
      } else if (error.response?.status === 403) {
        ElMessage.error('提交失败：作业已过截止时间或权限不足')
      } else {
        ElMessage.error('提交失败：' + (error.message || '网络错误，请稍后重试'))
      }
    }
  } finally {
    submitting.value = false
  }
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

// 监听作业数据变化，自动初始化答案数组
watch(
  () => assignment.value,
  (newAssignment) => {
    if (newAssignment?.questions && submissionForm.answers.length === 0) {
      initializeAnswers()
    }
  },
  { immediate: true }
)

// 页面加载时获取作业详情
onMounted(() => {
  fetchAssignmentDetail()
})
</script>

<style scoped>
.submit-assignment {
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
  gap: 12px;
}

.questions-section {
  padding: 32px;
}

.question-card {
  border: 1px solid #ebeef5;
  border-radius: 8px;
  padding: 24px;
  margin-bottom: 24px;
  background: #fafafa;
}

.question-card:last-child {
  margin-bottom: 0;
}

.question-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
}

.question-number {
  font-weight: 500;
  color: #409eff;
  font-size: 16px;
}

.question-score {
  color: #e6a23c;
  font-weight: 500;
}

.question-content {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.question-text h4,
.answer-input h4 {
  margin: 0 0 8px 0;
  color: #303133;
  font-size: 14px;
  font-weight: 500;
}

.question-text p {
  margin: 0;
  color: #303133;
  line-height: 1.6;
  background: white;
  padding: 16px;
  border-radius: 6px;
  border: 1px solid #e4e7ed;
}

.answer-input {
  background: white;
  padding: 16px;
  border-radius: 6px;
  border: 1px solid #e4e7ed;
}

.submit-section {
  padding: 32px;
  border-top: 1px solid #ebeef5;
  background: #f8f9fa;
}

.submit-actions {
  display: flex;
  justify-content: center;
  gap: 16px;
  margin-top: 24px;
}

.completed-state,
.error-state {
  background: white;
  border-radius: 8px;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.1);
  padding: 40px;
}

/* 表单样式调整 */
.el-form-item {
  margin-bottom: 0;
}

.el-textarea {
  width: 100%;
}
</style>
