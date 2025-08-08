import { ref, computed } from 'vue'
import { defineStore } from 'pinia'
import { qaApi, type ChatMessageRequest } from '@/api'
import type { QAQuestion, CreateQuestionRequest, ChatSession, ChatMessage, ChatSessionDetail } from '@/types'
import { ElMessage } from 'element-plus'

export const useQAStore = defineStore('qa', () => {
  // 状态
  const questions = ref<QAQuestion[]>([])
  const currentQuestion = ref<QAQuestion | null>(null)
  const sessions = ref<ChatSession[]>([])
  const currentSession = ref<ChatSession | ChatSessionDetail | null>(null)
  const currentSessionMessages = ref<ChatMessage[]>([])
  const loading = ref(false)
  const total = ref(0)

  // 计算属性
  const questionCount = computed(() => questions.value.length)
  const sessionCount = computed(() => sessions.value.length)

  // 获取问题列表
  const fetchQuestions = async (params?: {
    page?: number
    page_size?: number
    subject?: string
  }) => {
    loading.value = true
    try {
      const response = await qaApi.getQuestions(params)
      questions.value = response.data.questions
      total.value = response.data.pagination.total
    } catch (error) {
      console.error('获取问题列表失败:', error)
      ElMessage.error('获取问题列表失败')
    } finally {
      loading.value = false
    }
  }

  // 获取问题详情
  const fetchQuestionDetail = async (questionId: string) => {
    loading.value = true
    try {
      const response = await qaApi.getQuestionDetail(questionId)
      currentQuestion.value = response.data
      return response.data
    } catch (error) {
      console.error('获取问题详情失败:', error)
      ElMessage.error('获取问题详情失败')
      throw error
    } finally {
      loading.value = false
    }
  }

  // 提交问题（学生）
  const submitQuestion = async (data: CreateQuestionRequest) => {
    loading.value = true
    try {
      const response = await qaApi.submitQuestion(data)
      ElMessage.success('问题提交成功')
      
      // 重新获取问题列表
      await fetchQuestions()
      
      return response.data
    } catch (error) {
      console.error('提交问题失败:', error)
      throw error
    } finally {
      loading.value = false
    }
  }

  // 删除问题
  const deleteQuestion = async (questionId: string) => {
    loading.value = true
    try {
      await qaApi.deleteQuestion(questionId)
      ElMessage.success('问题删除成功')
      
      // 从本地状态中移除
      questions.value = questions.value.filter(q => q.id !== questionId)
      if (currentQuestion.value?.id === questionId) {
        currentQuestion.value = null
      }
      
      return true
    } catch (error) {
      console.error('删除问题失败:', error)
      throw error
    } finally {
      loading.value = false
    }
  }

  // 清除当前问题
  const clearCurrentQuestion = () => {
    currentQuestion.value = null
  }

  // 按学科分组问题
  const getQuestionsBySubject = computed(() => {
    const grouped: Record<string, QAQuestion[]> = {}
    questions.value.forEach(question => {
      if (!grouped[question.subject]) {
        grouped[question.subject] = []
      }
      grouped[question.subject].push(question)
    })
    return grouped
  })

  // 获取最近的问题
  const getRecentQuestions = computed(() => {
    return questions.value
      .slice()
      .sort((a, b) => new Date(b.created_at).getTime() - new Date(a.created_at).getTime())
      .slice(0, 10)
  })

  // 新的聊天方法
  const sendChatMessage = async (data: ChatMessageRequest) => {
    loading.value = true
    try {
      const response = await qaApi.sendChatMessage(data)
      return response.data
    } catch (error) {
      console.error('发送消息失败:', error)
      ElMessage.error('发送消息失败')
      throw error
    } finally {
      loading.value = false
    }
  }

  const fetchSessions = async (params?: {
    page?: number
    page_size?: number
    subject?: string
  }) => {
    loading.value = true
    try {
      const response = await qaApi.getSessions(params)
      sessions.value = response.data.sessions
      total.value = response.data.pagination.total
      return response.data
    } catch (error) {
      console.error('获取会话列表失败:', error)
      ElMessage.error('获取会话列表失败')
      throw error
    } finally {
      loading.value = false
    }
  }

  const fetchSessionDetail = async (sessionId: string) => {
    loading.value = true
    try {
      const response = await qaApi.getSessionDetail(sessionId)
      currentSession.value = response.data
      currentSessionMessages.value = response.data.messages
      return response.data
    } catch (error) {
      console.error('获取会话详情失败:', error)
      ElMessage.error('获取会话详情失败')
      throw error
    } finally {
      loading.value = false
    }
  }

  return {
    // 状态
    questions,
    currentQuestion,
    sessions,
    currentSession,
    currentSessionMessages,
    loading,
    total,

    // 计算属性
    questionCount,
    sessionCount,
    getQuestionsBySubject,
    getRecentQuestions,

    // 新的聊天方法
    sendChatMessage,
    fetchSessions,
    fetchSessionDetail,

    // 旧的方法（保持兼容）
    fetchQuestions,
    fetchQuestionDetail,
    submitQuestion,
    deleteQuestion,
    clearCurrentQuestion
  }
})
