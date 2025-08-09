// 通用API响应格式
export interface ApiResponse<T = unknown> {
  code: number
  message: string
  data: T
  timestamp?: string
}

// 分页响应格式
export interface PaginatedResponse<T> {
  results: T[]
  count: number
  next: string | null
  previous: string | null
}

// 用户相关类型
export interface User {
  id: string
  username: string
  email: string
  role: 'teacher' | 'student'
  real_name: string
  student_id?: string
  created_at: string
}

export interface LoginRequest {
  username: string
  password: string
}

export interface RegisterRequest {
  username: string
  password: string
  email: string
  role: 'teacher' | 'student'
  real_name: string
  student_id?: string
}

export interface LoginResponse {
  access_token: string
  refresh_token: string
  user: User
}

// 作业相关类型
export interface Assignment {
  id: string
  title: string
  description: string
  subject: string
  created_by: string
  deadline: string
  total_score: number
  created_at: string
  updated_at: string
  submission_count?: number
  is_completed?: boolean | null  // 学生视角：是否已完成
  obtained_score?: number | null // 学生视角：获得分数
  questions?: Question[]         // 作业详情中包含的题目列表
}

export interface Question {
  id: string
  assignment: string
  question_text: string
  reference_answer: string
  score: number
  order: number
}

export interface Answer {
  id: string
  question_id: string
  question_text: string
  student_answer: string
  reference_answer: string
  score: number
  obtained_score: number
  ai_feedback: string
  student_image_url?: string
}

export interface Submission {
  id: string
  assignment_title: string
  student_id?: string
  student_name?: string
  student_username?: string
  status: 'submitted' | 'grading' | 'graded'
  total_score: number
  obtained_score: number
  overall_feedback: string
  submitted_at: string
  graded_at?: string
  answers: Answer[]
}

export interface CreateAssignmentRequest {
  title: string
  description: string
  subject: string
  deadline: string
  total_score: number
  questions: {
    question_text: string
    reference_answer: string
    score: number
    order: number
  }[]
}

export interface SubmitAssignmentRequest {
  answers: {
    question_id: string
    answer_text?: string
  }[]
}

// 问答相关类型
export interface QAQuestion {
  id: string
  student: string
  question_text: string
  subject: string
  ai_answer: string
  created_at: string
}

export interface CreateQuestionRequest {
  question_text: string
  subject: string
  context?: string
}

// 聊天相关类型
export interface ChatMessage {
  id: string
  sender_id: string
  receiver_id: string
  content: string
  is_read: boolean
  created_at: string
  sender: 'teacher' | 'student'
}

export interface ChatSession {
  id: string
  subject: string
  created_at: string
  updated_at: string
  last_message?: {
    role: 'user' | 'ai'
    content: string
    created_at: string
  }
  message_count: number
}

export interface ChatSessionDetail {
  id: string
  subject: string
  created_at: string
  updated_at: string
  messages: ChatMessage[]
}

// 学习报告相关类型
export interface LearningReport {
  id: string
  student_name: string
  student_id_number: string
  generated_by_name: string
  period: 'week' | 'month' | 'semester' | 'all'
  period_display: string
  subjects: string[]
  status: 'generating' | 'completed' | 'failed'
  status_display: string
  total_assignments: number
  completed_assignments: number
  average_score: number
  total_questions: number
  report_content: string
  created_at: string
  updated_at: string
}

export interface GenerateReportRequest {
  student_id?: string
  period: 'week' | 'month' | 'semester' | 'all'
  subjects?: string[]
}

export interface ClassReportRequest {
  period: 'week' | 'month' | 'semester' | 'all'
  subjects: string[]
}

export interface ClassReportResponse {
  report_data: {
    total_students: number
    active_students: number
    average_score: number
    subjects: string[]
    period: string
  }
  students: Array<{
    id: string
    real_name: string
    username: string
  }>
}

// 通用工具类型
export interface SelectOption {
  label: string
  value: string | number
}

export interface TableColumn {
  prop: string
  label: string
  width?: string | number
  minWidth?: string | number
  align?: 'left' | 'center' | 'right'
  sortable?: boolean
  formatter?: (row: Record<string, unknown>, column: Record<string, unknown>, cellValue: unknown) => string
}

// 路由元信息
export interface RouteMeta {
  title?: string
  requiresAuth?: boolean
  roles?: string[]
  icon?: string
  hidden?: boolean
}
