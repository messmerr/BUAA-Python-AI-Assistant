import { ElMessage, ElMessageBox } from 'element-plus'

/**
 * 格式化日期时间
 */
export function formatDateTime(dateString: string): string {
  if (!dateString) return ''
  
  const date = new Date(dateString)
  const year = date.getFullYear()
  const month = String(date.getMonth() + 1).padStart(2, '0')
  const day = String(date.getDate()).padStart(2, '0')
  const hours = String(date.getHours()).padStart(2, '0')
  const minutes = String(date.getMinutes()).padStart(2, '0')
  
  return `${year}-${month}-${day} ${hours}:${minutes}`
}

/**
 * 格式化日期
 */
export function formatDate(dateString: string): string {
  if (!dateString) return ''
  
  const date = new Date(dateString)
  const year = date.getFullYear()
  const month = String(date.getMonth() + 1).padStart(2, '0')
  const day = String(date.getDate()).padStart(2, '0')
  
  return `${year}-${month}-${day}`
}

/**
 * 计算相对时间
 */
export function getRelativeTime(dateString: string): string {
  if (!dateString) return ''
  
  const now = new Date()
  const date = new Date(dateString)
  const diff = now.getTime() - date.getTime()
  
  const minutes = Math.floor(diff / (1000 * 60))
  const hours = Math.floor(diff / (1000 * 60 * 60))
  const days = Math.floor(diff / (1000 * 60 * 60 * 24))
  
  if (minutes < 1) return '刚刚'
  if (minutes < 60) return `${minutes}分钟前`
  if (hours < 24) return `${hours}小时前`
  if (days < 7) return `${days}天前`
  
  return formatDate(dateString)
}

/**
 * 检查截止时间状态
 */
export function getDeadlineStatus(deadline: string): {
  status: 'normal' | 'warning' | 'danger' | 'expired'
  text: string
  color: string
} {
  if (!deadline) return { status: 'normal', text: '', color: '' }
  
  const now = new Date()
  const deadlineDate = new Date(deadline)
  const diff = deadlineDate.getTime() - now.getTime()
  const hours = Math.floor(diff / (1000 * 60 * 60))
  const days = Math.floor(diff / (1000 * 60 * 60 * 24))
  
  if (diff < 0) {
    return { status: 'expired', text: '已过期', color: '#F56C6C' }
  } else if (hours < 24) {
    return { status: 'danger', text: `${hours}小时后截止`, color: '#F56C6C' }
  } else if (days < 3) {
    return { status: 'warning', text: `${days}天后截止`, color: '#E6A23C' }
  } else {
    return { status: 'normal', text: `${days}天后截止`, color: '#67C23A' }
  }
}

/**
 * 获取用户角色显示文本
 */
export function getRoleText(role: string): string {
  const roleMap: Record<string, string> = {
    teacher: '教师',
    student: '学生'
  }
  return roleMap[role] || role
}

/**
 * 获取作业状态显示文本
 */
export function getSubmissionStatusText(status: string): string {
  const statusMap: Record<string, string> = {
    submitted: '已提交',
    grading: '批改中',
    graded: '已批改'
  }
  return statusMap[status] || status
}

/**
 * 获取作业状态颜色
 */
export function getSubmissionStatusColor(status: string): string {
  const colorMap: Record<string, string> = {
    submitted: '#E6A23C',
    grading: '#409EFF',
    graded: '#67C23A'
  }
  return colorMap[status] || '#909399'
}

/**
 * 复制文本到剪贴板
 */
export async function copyToClipboard(text: string): Promise<void> {
  try {
    await navigator.clipboard.writeText(text)
    ElMessage.success('复制成功')
  } catch (error) {
    console.error('复制失败:', error)
    ElMessage.error('复制失败')
  }
}

/**
 * 确认对话框
 */
export function confirmDialog(
  message: string,
  title: string = '确认操作'
): Promise<boolean> {
  return ElMessageBox.confirm(message, title, {
    confirmButtonText: '确定',
    cancelButtonText: '取消',
    type: 'warning'
  })
    .then(() => true)
    .catch(() => false)
}

/**
 * 下载文件
 */
export function downloadFile(url: string, filename: string): void {
  const link = document.createElement('a')
  link.href = url
  link.download = filename
  document.body.appendChild(link)
  link.click()
  document.body.removeChild(link)
}

/**
 * 验证邮箱格式
 */
export function validateEmail(email: string): boolean {
  const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/
  return emailRegex.test(email)
}

/**
 * 验证学号格式（假设为8位数字）
 */
export function validateStudentId(studentId: string): boolean {
  const studentIdRegex = /^\d{8}$/
  return studentIdRegex.test(studentId)
}

/**
 * 防抖函数
 */
export function debounce<T extends (...args: any[]) => any>(
  func: T,
  wait: number
): (...args: Parameters<T>) => void {
  let timeout: NodeJS.Timeout | null = null
  
  return (...args: Parameters<T>) => {
    if (timeout) clearTimeout(timeout)
    timeout = setTimeout(() => func(...args), wait)
  }
}

/**
 * 节流函数
 */
export function throttle<T extends (...args: any[]) => any>(
  func: T,
  wait: number
): (...args: Parameters<T>) => void {
  let lastTime = 0
  
  return (...args: Parameters<T>) => {
    const now = Date.now()
    if (now - lastTime >= wait) {
      lastTime = now
      func(...args)
    }
  }
}
