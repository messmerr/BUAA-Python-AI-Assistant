// 通用API响应格式
export interface ApiResponse<T = any> {
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
  question: string
  answer_text: string
  score: number
  feedback: string
}

export interface Submission {
  id: string
  assignment: string
  student: string
  status: 'submitted' | 'grading' | 'graded'
  total_score: number
  feedback: string
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
    answer_text: string
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

// 学习报告相关类型
export interface LearningReport {
  id: string
  student: string
  report_type: string
  content: any
  generated_at: string
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
  formatter?: (row: any, column: any, cellValue: any) => string
}

// 路由元信息
export interface RouteMeta {
  title?: string
  requiresAuth?: boolean
  roles?: string[]
  icon?: string
  hidden?: boolean
}
