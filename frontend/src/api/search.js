import http from './index'

/**
 * 单次检索
 * @param {string} keyword
 * @param {'strict'|'related'} mode
 * @param {boolean} showBrowser
 */
export const searchSingle = (keyword, mode = 'strict', showBrowser = false) =>
  http.post('/api/search', { keyword, mode, show_browser: showBrowser })

/**
 * 创建批量检索任务
 * @param {string[]} keywords
 */
export const createBatchTask = (keywords) =>
  http.post('/api/batch', { keywords })

/**
 * 健康检查
 */
export const ping = () =>
  http.get('/api/ping')