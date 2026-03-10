import http from './index'

/**
 * 获取所有任务
 */
export const getTasks = () =>
  http.get('/api/tasks')

/**
 * 获取单个任务详情
 * @param {number} taskId
 */
export const getTask = (taskId) =>
  http.get(`/api/tasks/${taskId}`)

/**
 * 获取任务词条列表
 * @param {number} taskId
 * @param {string} [status]
 */
export const getTaskItems = (taskId, status) =>
  http.get(`/api/tasks/${taskId}/items`, { params: status ? { status } : {} })

/**
 * 删除任务
 * @param {number} taskId
 */
export const deleteTask = (taskId) =>
  http.delete(`/api/tasks/${taskId}`)

/**
 * 获取控制台统计数据
 */
export const getStats = () =>
  http.get('/api/stats')

/**
 * 导出任务结果为 Excel
 * 使用 blob 下载，无需后端返回 JSON
 * @param {number} taskId
 * @param {string} taskName  用于拼接文件名（可选）
 */
export const exportTask = async (taskId, taskName = '') => {
  const response = await http.get(`/api/tasks/${taskId}/export`, {
    responseType: 'blob',   // 关键：告诉 axios 以二进制流接收
  })

  // 从响应头取文件名，没有则用默认值
  const disposition = response.headers['content-disposition'] || ''
  let filename = `检索结果_${taskName || taskId}.xlsx`
  const match = disposition.match(/filename\*?=(?:UTF-8'')?["']?([^"';\n]+)["']?/i)
  if (match) {
    try { filename = decodeURIComponent(match[1]) } catch { /* 解码失败就用默认 */ }
  }

  // 创建隐藏 <a> 标签触发下载
  const url = URL.createObjectURL(new Blob([response.data]))
  const link = document.createElement('a')
  link.href = url
  link.download = filename
  document.body.appendChild(link)
  link.click()
  document.body.removeChild(link)
  URL.revokeObjectURL(url)
}