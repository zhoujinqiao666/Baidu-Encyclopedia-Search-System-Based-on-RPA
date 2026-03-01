<template>
  <div style="padding: 20px; max-width: 600px; margin: 0 auto;">
    <h1>百度百科RPA检索系统</h1>
    
    <!-- 输入框 -->
    <el-input
      v-model="keyword"
      placeholder="请输入要搜索的词条"
      style="margin: 20px 0"
    />
    
    <!-- 搜索按钮 -->
    <el-button 
      type="primary" 
      @click="handleSearch"
      :loading="loading"
    >
      开始搜索
    </el-button>
    
    <!-- 显示结果 -->
    <div v-if="result" style="margin-top: 30px;">
      <el-card>
        <h3>{{ result.title }}</h3>
        <p>{{ result.summary }}</p>
        <p>
          <a :href="result.url" target="_blank">查看原文</a>
        </p>
      </el-card>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import axios from 'axios'
import { ElMessage } from 'element-plus'

// 定义响应式变量
const keyword = ref('')      // 输入框的内容
const loading = ref(false)   // 是否正在搜索
const result = ref(null)     // 搜索结果

// 定义搜索方法
const handleSearch = async () => {
  if (!keyword.value.trim()) {
    ElMessage.warning('请输入关键词')
    return
  }
  
  loading.value = true
  result.value = null
  
  try {
    // 发送请求到后端
    const response = await axios.post('http://localhost:5000/api/search', {
      keyword: keyword.value
    })
    
    // 显示结果
    result.value = response.data
    ElMessage.success('搜索成功！')
    
  } catch (error) {
    console.error('搜索失败:', error)
    ElMessage.error('搜索失败，请检查后端是否启动')
  } finally {
    loading.value = false
  }
}
</script>