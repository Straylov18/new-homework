import { createRouter, createWebHistory } from 'vue-router'
import MainPage from '@/components/pages/MainPage.vue'
import Page1 from '@/components/pages/Page1.vue'
import Page2 from '@/components/pages/Page2.vue'

const routes = [
  {
    name: "Main",
    path: "/",
    component: MainPage,
  },
  {
    name: "Page1",
    path: "/page1",
    component: Page1
  },
  {
    name: "Page2",
    path: "/page2",
    component: Page2
  },
]

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes,
})

export default router
