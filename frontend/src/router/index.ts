import { createRouter, createWebHistory } from 'vue-router'
import type { RouteRecordRaw } from 'vue-router'
import { useAuthStore } from '@/stores'

// 路由配置
const routes: RouteRecordRaw[] = [
  {
    path: '/login',
    name: 'Login',
    component: () => import('@/views/auth/LoginView.vue'),
    meta: { requiresAuth: false, title: '登录' }
  },
  {
    path: '/register',
    name: 'Register',
    component: () => import('@/views/auth/RegisterView.vue'),
    meta: { requiresAuth: false, title: '注册' }
  },
  {
    path: '/',
    name: 'Layout',
    component: () => import('@/views/layout/LayoutView.vue'),
    meta: { requiresAuth: true },
    redirect: '/dashboard',
    children: [
      {
        path: '/dashboard',
        name: 'Dashboard',
        component: () => import('@/views/dashboard/DashboardView.vue'),
        meta: { title: '首页', icon: 'House' }
      },
      {
        path: '/assignments',
        name: 'Assignments',
        component: () => import('@/views/assignments/AssignmentsView.vue'),
        meta: { title: '作业管理', icon: 'Document' }
      },
      {
        path: '/assignments/:id',
        name: 'AssignmentDetail',
        component: () => import('@/views/assignments/AssignmentDetailView.vue'),
        meta: { title: '作业详情' }
      },
      {
        path: '/assignments/create',
        name: 'CreateAssignment',
        component: () => import('@/views/assignments/CreateAssignmentView.vue'),
        meta: { title: '创建作业', roles: ['teacher'] }
      },
      {
        path: '/assignments/:id/submit',
        name: 'SubmitAssignment',
        component: () => import('@/views/assignments/SubmitAssignmentView.vue'),
        meta: { title: '提交作业', roles: ['student'] }
      },
      {
        path: '/assignments/:id/result',
        name: 'AssignmentResult',
        component: () => import('@/views/assignments/AssignmentResultView.vue'),
        meta: { title: '批改结果' }
      },
      {
        path: '/assignments/:id/submissions',
        name: 'AssignmentSubmissions',
        component: () => import('@/views/assignments/AssignmentSubmissionsView.vue'),
        meta: { title: '提交情况', roles: ['teacher'] }
      },
      {
        path: '/qa',
        name: 'QA',
        component: () => import('@/views/qa/QAView.vue'),
        meta: { requiresAuth: true }
      },
      {
        path: '/chat',
        name: 'Chat',
        component: () => import('@/views/chat/ChatView.vue'),
        meta: { requiresAuth: true }
      },
      {
        path: '/reports',
        name: 'Reports',
        component: () => import('@/views/reports/ReportsView.vue'),
        meta: { requiresAuth: true }
      },
      {
        path: '/reports/:id',
        name: 'ReportDetail',
        component: () => import('@/views/reports/ReportDetailView.vue'),
        meta: { title: '报告详情' }
      },
      {
        path: '/profile',
        name: 'Profile',
        component: () => import('@/views/profile/ProfileView.vue'),
        meta: { title: '个人中心', icon: 'User' }
      }
    ]
  },
  {
    path: '/:pathMatch(.*)*',
    name: 'NotFound',
    component: () => import('@/views/error/NotFoundView.vue'),
    meta: { title: '页面不存在' }
  }
]

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes
})

// 路由守卫
router.beforeEach(async (to, from, next) => {
  const authStore = useAuthStore()

  // 设置页面标题
  if (to.meta.title) {
    document.title = `${to.meta.title} - AI助教系统`
  }

  // 检查是否需要认证
  if (to.meta.requiresAuth !== false) {
    if (!authStore.isAuthenticated) {
      // 尝试初始化用户信息
      await authStore.initUser()

      if (!authStore.isAuthenticated) {
        next({ name: 'Login', query: { redirect: to.fullPath } })
        return
      }
    }

    // 检查角色权限
    if (to.meta.roles && to.meta.roles.length > 0) {
      const userRole = authStore.user?.role
      if (!userRole || !to.meta.roles.includes(userRole)) {
        next({ name: 'Dashboard' })
        return
      }
    }
  }

  // 如果已登录用户访问登录/注册页面，重定向到首页
  if (authStore.isAuthenticated && (to.name === 'Login' || to.name === 'Register')) {
    next({ name: 'Dashboard' })
    return
  }

  next()
})

export default router

