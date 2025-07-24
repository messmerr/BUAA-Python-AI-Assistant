<template>
  <div class="create-assignment">
    <div class="page-header">
      <h1>创建作业</h1>
      <div class="header-actions">
        <el-button @click="$router.back()">取消</el-button>
        <el-button 
          type="primary" 
          :loading="assignmentsStore.loading"
          @click="handleSubmit"
        >
          发布作业
        </el-button>
      </div>
    </div>

    <div class="form-container">
      <el-form 
        ref="formRef" 
        :model="assignmentForm" 
        :rules="rules"
        label-width="100px"
        size="large"
      >
        <!-- 基本信息 -->
        <div class="form-section">
          <h3>基本信息</h3>
          
          <el-form-item label="作业标题" prop="title">
            <el-input 
              v-model="assignmentForm.title" 
              placeholder="请输入作业标题"
              maxlength="100"
              show-word-limit
            />
          </el-form-item>
          
          <el-form-item label="科目" prop="subject">
            <el-input 
              v-model="assignmentForm.subject" 
              placeholder="请输入科目名称"
              maxlength="50"
            />
          </el-form-item>
          
          <el-form-item label="作业描述" prop="description">
            <el-input 
              v-model="assignmentForm.description" 
              type="textarea" 
              :rows="4"
              placeholder="请输入作业描述和要求"
              maxlength="500"
              show-word-limit
            />
          </el-form-item>
          
          <el-form-item label="截止时间" prop="deadline">
            <el-date-picker
              v-model="assignmentForm.deadline"
              type="datetime"
              placeholder="选择截止时间"
              format="YYYY-MM-DD HH:mm"
              value-format="YYYY-MM-DDTHH:mm:ss"
              :disabled-date="disabledDate"
            />
          </el-form-item>
        </div>

        <!-- 题目设置 -->
        <div class="form-section">
          <div class="section-header">
            <h3>题目设置</h3>
            <el-button type="primary" @click="addQuestion">
              <el-icon><Plus /></el-icon>
              添加题目
            </el-button>
          </div>

          <div v-if="assignmentForm.questions.length === 0" class="empty-questions">
            <el-empty description="暂无题目，请添加题目" />
          </div>

          <div v-else class="questions-list">
            <div 
              v-for="(question, index) in assignmentForm.questions" 
              :key="index"
              class="question-item"
            >
              <div class="question-header">
                <span class="question-number">第{{ index + 1 }}题</span>
                <el-button 
                  type="danger" 
                  size="small" 
                  text
                  @click="removeQuestion(index)"
                >
                  删除
                </el-button>
              </div>

              <el-form-item 
                :prop="`questions.${index}.question_text`" 
                :rules="questionRules.question_text"
                label="题目内容"
              >
                <el-input 
                  v-model="question.question_text" 
                  type="textarea" 
                  :rows="3"
                  placeholder="请输入题目内容"
                  maxlength="1000"
                  show-word-limit
                />
              </el-form-item>

              <el-form-item 
                :prop="`questions.${index}.reference_answer`" 
                :rules="questionRules.reference_answer"
                label="参考答案"
              >
                <el-input 
                  v-model="question.reference_answer" 
                  type="textarea" 
                  :rows="3"
                  placeholder="请输入参考答案"
                  maxlength="1000"
                  show-word-limit
                />
              </el-form-item>

              <el-form-item 
                :prop="`questions.${index}.score`" 
                :rules="questionRules.score"
                label="分值"
              >
                <el-input-number 
                  v-model="question.score" 
                  :min="1" 
                  :max="100"
                  placeholder="分值"
                />
              </el-form-item>
            </div>
          </div>

          <!-- 总分显示 -->
          <div v-if="totalScore > 0" class="total-score">
            <el-alert
              :title="`总分：${totalScore}分`"
              type="info"
              :closable="false"
              show-icon
            />
          </div>
        </div>
      </el-form>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, computed } from 'vue'
import { useRouter } from 'vue-router'
import { useAssignmentsStore } from '@/stores'
import { Plus } from '@element-plus/icons-vue'
import type { FormInstance, FormRules } from 'element-plus'
import { ElMessage } from 'element-plus'

const router = useRouter()
const assignmentsStore = useAssignmentsStore()

// 表单引用
const formRef = ref<FormInstance>()

// 作业表单数据
const assignmentForm = reactive({
  title: '',
  subject: '',
  description: '',
  deadline: '',
  questions: [] as Array<{
    question_text: string
    reference_answer: string
    score: number
    order: number
  }>
})

// 表单验证规则
const rules: FormRules = {
  title: [
    { required: true, message: '请输入作业标题', trigger: 'blur' }
  ],
  subject: [
    { required: true, message: '请输入科目名称', trigger: 'blur' }
  ],
  description: [
    { required: true, message: '请输入作业描述', trigger: 'blur' }
  ],
  deadline: [
    { required: true, message: '请选择截止时间', trigger: 'change' }
  ]
}

// 题目验证规则
const questionRules = {
  question_text: [
    { required: true, message: '请输入题目内容', trigger: 'blur' }
  ],
  reference_answer: [
    { required: true, message: '请输入参考答案', trigger: 'blur' }
  ],
  score: [
    { required: true, message: '请输入分值', trigger: 'blur' },
    { type: 'number', min: 1, message: '分值不能小于1', trigger: 'blur' }
  ]
}

// 计算总分
const totalScore = computed(() => {
  return assignmentForm.questions.reduce((sum, question) => sum + (question.score || 0), 0)
})

// 禁用过去的日期
const disabledDate = (time: Date) => {
  return time.getTime() < Date.now() - 24 * 60 * 60 * 1000
}

// 添加题目
const addQuestion = () => {
  assignmentForm.questions.push({
    question_text: '',
    reference_answer: '',
    score: 10,
    order: assignmentForm.questions.length + 1
  })
}

// 删除题目
const removeQuestion = (index: number) => {
  assignmentForm.questions.splice(index, 1)
  // 重新设置题目顺序
  assignmentForm.questions.forEach((question, idx) => {
    question.order = idx + 1
  })
}

// 提交表单
const handleSubmit = async () => {
  if (!formRef.value) return

  // 验证基本信息
  const valid = await formRef.value.validate().catch(() => false)
  if (!valid) return

  // 验证题目
  if (assignmentForm.questions.length === 0) {
    ElMessage.error('请至少添加一道题目')
    return
  }

  // 验证每个题目的内容
  for (let i = 0; i < assignmentForm.questions.length; i++) {
    const question = assignmentForm.questions[i]
    if (!question.question_text.trim()) {
      ElMessage.error(`第${i + 1}题的题目内容不能为空`)
      return
    }
    if (!question.reference_answer.trim()) {
      ElMessage.error(`第${i + 1}题的参考答案不能为空`)
      return
    }
    if (!question.score || question.score < 1) {
      ElMessage.error(`第${i + 1}题的分值必须大于0`)
      return
    }
  }

  try {
    const createData = {
      title: assignmentForm.title,
      subject: assignmentForm.subject,
      description: assignmentForm.description,
      deadline: assignmentForm.deadline,
      total_score: totalScore.value,
      questions: assignmentForm.questions
    }

    console.log('创建作业数据:', createData)
    
    const result = await assignmentsStore.createAssignment(createData)
    if (result) {
      ElMessage.success('作业创建成功')
      router.push('/assignments')
    }
  } catch (error) {
    console.error('创建作业失败:', error)
  }
}
</script>

<style scoped>
.create-assignment {
  padding: 24px;
  max-width: 1000px;
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

.form-container {
  background: white;
  border-radius: 8px;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.1);
  padding: 32px;
}

.form-section {
  margin-bottom: 40px;
}

.form-section:last-child {
  margin-bottom: 0;
}

.form-section h3 {
  margin: 0 0 24px 0;
  color: #303133;
  font-size: 18px;
  font-weight: 500;
  padding-bottom: 12px;
  border-bottom: 1px solid #ebeef5;
}

.section-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 24px;
}

.section-header h3 {
  margin: 0;
  border: none;
  padding: 0;
}

.empty-questions {
  padding: 40px;
  text-align: center;
}

.questions-list {
  display: flex;
  flex-direction: column;
  gap: 24px;
}

.question-item {
  border: 1px solid #ebeef5;
  border-radius: 8px;
  padding: 24px;
  background: #fafafa;
}

.question-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 16px;
}

.question-number {
  font-weight: 500;
  color: #409eff;
  font-size: 16px;
}

.total-score {
  margin-top: 24px;
}

/* 表单项样式调整 */
.el-form-item {
  margin-bottom: 24px;
}

.el-textarea {
  width: 100%;
}

.el-input-number {
  width: 200px;
}

.el-date-picker {
  width: 300px;
}
</style>
