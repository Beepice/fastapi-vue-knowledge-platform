import { createRouter, createWebHistory } from 'vue-router'
import Login from '../views/Login.vue'
import Register from '../views/Register.vue'

import MainLayout from '../views/layout/MainLayout.vue'

const routes = [
  {
    path: '/',
    component: MainLayout,     // ← 布局组件作为父级
    children: [
      {
        path: '',              // 默认子路由 → /
        component: () => import ('../views/Home.vue')
      },
      {
        path: '/documents/:versionId/:documentId',
        name: 'DocumentDetail',
        component: () => import('../views/layout/components/DocumentView.vue'),
        props: true
      },
      // 后续加的页面都放这里，自动带导航栏
      // { path: 'entries', component: Entries },
      // { path: 'search', component: Search },
    ]
  },
  { path: '/login', component: Login },
  {path: '/register', component: Register}
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

export default router
