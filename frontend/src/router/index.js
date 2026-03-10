import Layout from '@/layout/Layout.vue'
import Dashboard from '@/views/Dashboard.vue'
import Search from '@/views/Search.vue'
import Batch from '@/views/Batch.vue'
import Task from '@/views/Task.vue'
import { createRouter, createWebHistory } from 'vue-router'

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    {
      path: '/',
      component: Layout,
      children:[
        {
          path:'',
          name:'Dashboard',
          component: Dashboard
        },
        {
          path:'search',
          name:'Search',
          component: Search
        },
        {
          path:'batch',
          name:'Batch',
          component: Batch
        },
        {
          path:'task',
          name:'Task',
          component: Task
        }
      ]
    },
    
  ],
 
})

export default router
