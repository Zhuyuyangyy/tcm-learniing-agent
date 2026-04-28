import { createRouter, createWebHistory } from 'vue-router'
import HomeView from '../views/HomeView.vue'
import QuizView from '../views/QuizView.vue'
import ChatView from '../views/ChatView.vue'
import KBView from '../views/KBView.vue'
import DashboardView from '../views/DashboardView.vue'
import TherapyView from '../views/TherapyView.vue'

const routes = [
  { path: '/', name: 'home', component: HomeView },
  { path: '/quiz', name: 'quiz', component: QuizView },
  { path: '/chat', name: 'chat', component: ChatView },
  { path: '/kb', name: 'kb', component: KBView },
  { path: '/dashboard', name: 'dashboard', component: DashboardView },
  { path: '/therapy', name: 'therapy', component: TherapyView },
]

const router = createRouter({
  history: createWebHistory(),
  routes,
})

export default router
