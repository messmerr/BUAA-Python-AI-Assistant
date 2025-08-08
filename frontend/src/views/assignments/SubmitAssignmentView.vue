<template>
  <div class="submit-assignment">
    <div v-if="assignmentsStore.loading" class="loading">
      <el-icon class="is-loading" size="32"><Loading /></el-icon>
      <p>加载中...</p>
    </div>

    <div v-else-if="assignment" class="assignment-content">
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
                >
                  <div class="answer-wrapper">
                    <el-input
                      v-model="submissionForm.answers[index].answer_text"
                      type="textarea"
                      :rows="6"
                      placeholder="请在此输入您的答案..."
                      maxlength="2000"
                      show-word-limit
                      :disabled="!!submissionForm.answers[index].answer_file"
                    />
                    
                    <div class="upload-section">
                      <div v-if="submissionForm.answers[index].image_preview" class="image-preview">
                        <el-image
                          :src="submissionForm.answers[index].image_preview"
                          fit="contain"
                          style="width: 120px; height: 120px; border-radius: 6px; border: 1px solid #dcdfe6;"
                          :preview-src-list="[submissionForm.answers[index].image_preview]"
                          preview-teleported
                        />
                        <el-button type="danger" circle :icon="Delete" @click="handleFileRemove(index)" />
                      </div>
                      
                      <el-upload
                        v-else
                        :id="`uploader-${index}`"
                        action="#"
                        :auto-upload="false"
                        :show-file-list="false"
                        :on-change="(file) => handleFileChange(file, index)"
                        :disabled="!!submissionForm.answers[index].answer_text?.trim()"
                        accept="image/png, image/jpeg"
                      >
                        <el-button :icon="Upload" :disabled="!!submissionForm.answers[index].answer_text?.trim()">
                          上传图片
                        </el-button>
                        <template #tip>
                          <div class="el-upload__tip">
                            可上传手写答案图片 (JPG/PNG)
                          </div>
                        </template>
                      </el-upload>
                    </div>
                  </div>
                  <div class="answer-hint">
                    你可以选择文字 <b>或</b> 图片作为答案
                  </div>
                  </el-form-item>
              </div>
            </div>
          </div>
        </el-form>
      </div>

      <div class="submit-section">
        <el-alert
          title="提交提醒"
          description="请仔细检查您的答案，作业提交后将自动进行AI批改，无法修改。AI批改可能需要30-60秒，请耐心等待。"
          type="warning"
          show-icon
          :closable="false"
        />
        <div class="submit-actions">
          <el-button size="large" @click="$router.back()">取消提交</el-button>
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
    
    <div v-else-if="assignment && assignment.is_completed" class="completed-state">
      <el-result
        icon="success"
        title="作业已提交"
        sub-title="您已经提交过这个作业，无需重复提交"
      >
        <template #extra>
          <el-button type="primary" @click="$router.push(`/assignments/${route.params.id}/result`)">
            查看批改结果
          </el-button>
          <el-button @click="$router.push('/assignments')">
            返回作业列表
          </el-button>
        </template>
      </el-result>
    </div>

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
import { Loading, Upload, Delete } from '@element-plus/icons-vue'
import type { FormInstance, UploadFile } from 'element-plus'
import { ElMessage, ElMessageBox } from 'element-plus'
import MarkdownRenderer from '@/components/common/MarkdownRenderer.vue'

const route = useRoute()
const router = useRouter()
const assignmentsStore = useAssignmentsStore()

const formRef = ref<FormInstance>()
const assignment = computed(() => assignmentsStore.currentAssignment)
const submitting = ref(false)

const submissionForm = reactive({
  answers: [] as Array<{
    question_id: string
    answer_text: string
    answer_file: File | null
    image_preview: string | null
  }>
})

const canSubmit = computed(() => {
  if (!assignment.value) return false
  const now = new Date()
  const deadline = new Date(assignment.value.deadline)
  if (now > deadline) return false
  
  return submissionForm.answers.every(
    answer => (answer.answer_text && answer.answer_text.trim().length > 0) || !!answer.answer_file
  )
})

const initializeAnswers = () => {
  if (assignment.value?.questions) {
    submissionForm.answers = assignment.value.questions.map(question => ({
      question_id: question.id,
      answer_text: '',
      answer_file: null,
      image_preview: null
    }))
  }
}

const handleFileChange = (uploadFile: UploadFile, index: number) => {
  const answer = submissionForm.answers[index]
  if (answer.answer_text?.trim()) {
    ElMessage.warning('请先清空文本框再上传图片')
    const uploader = document.getElementById(`uploader-${index}`) as any;
    if (uploader && uploader.__vueParentComponent) {
      uploader.__vueParentComponent.ctx.uploader.clearFiles();
    }
    return
  }
  
  if (uploadFile.raw) {
    answer.answer_file = uploadFile.raw
    answer.image_preview = URL.createObjectURL(uploadFile.raw)
  }
}

const handleFileRemove = (index: number) => {
  const answer = submissionForm.answers[index]
  if (answer.image_preview) {
    URL.revokeObjectURL(answer.image_preview)
  }
  answer.answer_file = null
  answer.image_preview = null
}

const fetchAssignmentDetail = async () => {
  const assignmentId = route.params.id as string
  if (!assignmentId) return
  try {
    await assignmentsStore.fetchAssignmentDetail(assignmentId)
  } catch (error) {
    console.error('获取作业详情失败:', error)
  }
}

const handleSubmit = async () => {
  if (!assignment.value) return

  const allAnswered = submissionForm.answers.every(
    answer => (answer.answer_text && answer.answer_text.trim().length > 0) || !!answer.answer_file
  )
  if (!allAnswered) {
    ElMessage.error('请确保所有题目都已作答！')
    return
  }
  
  const now = new Date()
  const deadline = new Date(assignment.value.deadline)
  if (now > deadline) {
    ElMessage.error('作业已过截止时间，无法提交')
    return
  }

  try {
    await ElMessageBox.confirm('确定要提交作业吗？提交后将无法修改。', '确认提交', {
      confirmButtonText: '确定提交',
      cancelButtonText: '再检查一下',
      type: 'warning'
    })

    submitting.value = true
    const assignmentId = route.params.id as string

    const formData = new FormData()
    submissionForm.answers.forEach((answer, index) => {
      formData.append(`answers[${index}]question_id`, answer.question_id)
      if (answer.answer_file) {
        formData.append(`answers[${index}]answer_image`, answer.answer_file)
      } else {
        formData.append(`answers[${index}]answer_text`, answer.answer_text)
      }
    });

    const result = await assignmentsStore.submitAssignment(assignmentId, formData)

    if (result) {
      ElMessage.success('作业提交成功，AI批改完成！')
      router.push(`/assignments/${assignmentId}/result`)
    }
  } catch (error: any) {
    if (error !== 'cancel') {
      console.error('提交作业失败:', error)
      ElMessage.error('提交失败：' + (error.response?.data?.message || error.message || '网络错误'))
    }
  } finally {
    submitting.value = false
  }
}

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

const getDeadlineType = (deadline: string) => {
  const now = new Date()
  const deadlineDate = new Date(deadline)
  const diff = deadlineDate.getTime() - now.getTime()
  const hours = Math.floor(diff / (1000 * 60 * 60))
  
  if (diff < 0) return 'danger'
  if (hours < 24) return 'warning'
  return 'success'
}

watch(() => assignment.value, (newAssignment) => {
  if (newAssignment?.questions) {
    initializeAnswers()
  }
}, { immediate: true })

onMounted(() => {
  fetchAssignmentDetail()
})
</script>

<style scoped>
/* --- 新增/修改样式 --- */
.answer-wrapper {
  display: flex;
  gap: 24px;
  width: 100%;
  align-items: flex-start;
}
.answer-wrapper .el-input {
  flex: 1;
}
.upload-section {
  width: 150px;
  flex-shrink: 0;
  display: flex;
  flex-direction: column;
  align-items: center;
  text-align: center;
}
.image-preview {
  position: relative;
  width: 120px;
  height: 120px;
  margin-bottom: 8px;
}
.image-preview .el-button {
  position: absolute;
  top: -10px;
  right: -10px;
  z-index: 10;
}
.el-upload__tip {
  font-size: 12px;
  color: #909399;
  margin-top: 8px;
  line-height: 1.4;
}
.answer-hint {
  font-size: 13px;
  color: #909399;
  margin-top: 10px;
  width: 100%;
  text-align: left;
}
/* --- 样式结束 --- */

.submit-assignment { padding: 24px; max-width: 1000px; margin: 0 auto; }
.loading { display: flex; flex-direction: column; align-items: center; justify-content: center; padding: 60px; color: #606266; }
.loading p { margin-top: 12px; }
.assignment-content { background: white; border-radius: 8px; box-shadow: 0 2px 12px rgba(0, 0, 0, 0.1); overflow: hidden; }
.assignment-header { padding: 32px; border-bottom: 1px solid #ebeef5; display: flex; justify-content: space-between; align-items: flex-start; }
.header-info { flex: 1; margin-right: 24px; }
.header-info h1 { margin: 0 0 16px 0; color: #303133; font-size: 24px; font-weight: 500; }
.meta-info { display: flex; align-items: center; gap: 16px; margin-bottom: 16px; font-size: 14px; color: #606266; }
.description { margin: 0; color: #606266; line-height: 1.6; }
.header-actions { display: flex; gap: 12px; }
.questions-section { padding: 32px; }
.question-card { border: 1px solid #ebeef5; border-radius: 8px; padding: 24px; margin-bottom: 24px; background: #fafafa; }
.question-card:last-child { margin-bottom: 0; }
.question-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 20px; }
.question-number { font-weight: 500; color: #409eff; font-size: 16px; }
.question-score { color: #e6a23c; font-weight: 500; }
.question-content { display: flex; flex-direction: column; gap: 20px; }
.question-text h4, .answer-input h4 { margin: 0 0 8px 0; color: #303133; font-size: 14px; font-weight: 500; }
.question-markdown { background: white; padding: 16px; border-radius: 6px; border: 1px solid #e4e7ed; }
.answer-input { background: white; padding: 16px; border-radius: 6px; border: 1px solid #e4e7ed; }
.submit-section { padding: 32px; border-top: 1px solid #ebeef5; background: #f8f9fa; }
.submit-actions { display: flex; justify-content: center; gap: 16px; margin-top: 24px; }
.completed-state, .error-state { background: white; border-radius: 8px; box-shadow: 0 2px 12px rgba(0, 0, 0, 0.1); padding: 40px; }
.el-form-item { margin-bottom: 0; }
</style>