<template>
  <div class="batch-page">

    <!-- 页头 -->
    <div class="page-header">
      <div class="header-tag">批量检索</div>
      <h2>批量词条检索</h2>
      <p>上传文件或粘贴关键词列表，批量执行百度词条抓取任务</p>
    </div>

    <!-- 恢复任务提示横幅 -->
    <transition name="slide-down">
      <div v-if="showResume" class="resume-banner">
        <div class="resume-left">
          <div class="resume-icon">
            <svg width="18" height="18" viewBox="0 0 24 24" fill="none">
              <circle cx="12" cy="12" r="10" stroke="currentColor" stroke-width="2"/>
              <polyline points="12 6 12 12 16 14" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
            </svg>
          </div>
          <div>
            <div class="resume-title">检测到未完成的批量任务</div>
            <div class="resume-desc">上次离开时任务仍在执行，是否恢复查看？</div>
          </div>
        </div>
        <div class="resume-actions">
          <button class="resume-btn secondary" @click="discardResume">重新检索</button>
          <button class="resume-btn primary" @click="resumeTask">继续查看</button>
        </div>
      </div>
    </transition>

    <!-- 未执行状态：输入区 -->
    <div v-if="!running && !finished && !showResume" class="input-stage">
      <div class="input-grid">

        <!-- 左列：文件上传 + 粘贴输入 -->
        <div class="left-col">

          <!-- 文件上传 -->
          <div class="card upload-card">
            <div class="card-label">文件上传</div>
            <div
              class="drop-zone"
              :class="{ dragging: isDragging }"
              @dragover.prevent="isDragging = true"
              @dragleave="isDragging = false"
              @drop.prevent="handleDrop"
              @click="$refs.fileInput.click()"
            >
              <input ref="fileInput" type="file" accept=".txt,.csv" style="display:none" @change="handleFileChange" />
              <div class="drop-icon">
                <svg width="28" height="28" viewBox="0 0 24 24" fill="none">
                  <path d="M21 15v4a2 2 0 01-2 2H5a2 2 0 01-2-2v-4" stroke="currentColor" stroke-width="1.5" stroke-linecap="round"/>
                  <polyline points="17 8 12 3 7 8" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"/>
                  <line x1="12" y1="3" x2="12" y2="15" stroke="currentColor" stroke-width="1.5" stroke-linecap="round"/>
                </svg>
              </div>
              <div class="drop-text">点击上传或拖拽文件到此区域</div>
              <div class="drop-hint">支持 .txt 或 .csv，每行一个关键词</div>
            </div>
          </div>

          <!-- 粘贴输入 -->
          <div class="card paste-card">
            <div class="card-label">或直接粘贴关键词列表</div>
            <textarea
              v-model="pasteText"
              class="paste-area"
              placeholder="每行输入一个关键词，例如：&#10;人工智能&#10;机器学习&#10;深度学习"
              @input="parsePasteText"
            ></textarea>
          </div>
        </div>

        <!-- 右列：预览 + 统计 -->
        <div class="right-col">

          <!-- 快速统计 -->
          <div class="card stats-card">
            <div class="card-label">快速统计</div>
            <div class="stats-grid">
              <div class="stat-item">
                <div class="stat-value">{{ keywords.length }}</div>
                <div class="stat-label">关键词数量</div>
              </div>
              <div class="stat-item">
                <div class="stat-value">{{ estimatedTime }}</div>
                <div class="stat-label">预计耗时</div>
              </div>
            </div>
            <div v-if="keywords.length > 0" class="stats-tip">
              <svg width="13" height="13" viewBox="0 0 24 24" fill="none">
                <circle cx="12" cy="12" r="10" stroke="currentColor" stroke-width="2"/>
                <line x1="12" y1="8" x2="12" y2="12" stroke="currentColor" stroke-width="2" stroke-linecap="round"/>
                <line x1="12" y1="16" x2="12.01" y2="16" stroke="currentColor" stroke-width="2" stroke-linecap="round"/>
              </svg>
              每条词条约 8 秒，顺序执行
            </div>
          </div>

          <!-- 关键词预览列表 -->
          <div class="card preview-card">
            <div class="preview-header">
              <div class="card-label">关键词预览</div>
              <button v-if="keywords.length > 0" class="clear-all-btn" @click="clearAll">清空全部</button>
            </div>

            <div v-if="keywords.length === 0" class="preview-empty">
              <svg width="32" height="32" viewBox="0 0 24 24" fill="none">
                <path d="M9 11l3 3L22 4" stroke="#d1d5db" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
                <path d="M21 12v7a2 2 0 01-2 2H5a2 2 0 01-2-2V5a2 2 0 012-2h11" stroke="#d1d5db" stroke-width="2" stroke-linecap="round"/>
              </svg>
              <span>上传文件或粘贴关键词后<br>将在此处预览</span>
            </div>

            <div v-else class="keyword-list">
              <div
                v-for="(kw, index) in keywords"
                :key="index"
                class="keyword-item"
              >
                <span class="kw-index">{{ index + 1 }}</span>
                <span class="kw-text">{{ kw }}</span>
                <button class="kw-delete" @click="removeKeyword(index)">
                  <svg width="12" height="12" viewBox="0 0 24 24" fill="none">
                    <path d="M18 6L6 18M6 6l12 12" stroke="currentColor" stroke-width="2" stroke-linecap="round"/>
                  </svg>
                </button>
              </div>
            </div>
          </div>

          <!-- 启动按钮 -->
          <button
            class="start-btn"
            :disabled="keywords.length === 0"
            @click="startBatch"
          >
            <svg width="16" height="16" viewBox="0 0 24 24" fill="none">
              <polygon points="5 3 19 12 5 21 5 3" fill="currentColor"/>
            </svg>
            批量启动检索任务
          </button>
        </div>
      </div>
    </div>

    <!-- 执行中 / 完成：进度面板 -->
    <div v-if="running || finished" class="progress-stage">

      <!-- 顶部总进度 -->
      <div class="card progress-header-card">
        <div class="progress-meta">
          <div class="progress-title">
            <span v-if="running" class="running-badge">
              <span class="running-dot"></span>执行中
            </span>
            <span v-else class="done-badge">✓ 执行完成</span>
            <span class="progress-keyword-hint">共 {{ totalCount }} 个词条</span>
          </div>
          <div class="progress-counts">
            <span class="count success">✓ {{ successCount }} 成功</span>
            <span class="count fail">✕ {{ failCount }} 失败</span>
            <span class="count pending">⏳ {{ pendingCount }} 等待</span>
          </div>
        </div>

        <div class="progress-bar-wrap">
          <div class="progress-bar" :style="{ width: progressPct + '%' }"></div>
        </div>
        <div class="progress-pct">{{ progressPct }}%</div>

        <button v-if="finished" class="restart-btn" @click="reset">重新检索</button>
      </div>

      <!-- 词条状态列表 -->
      <div class="card items-card">
        <div class="card-label">词条执行状态</div>
        <div class="items-list">
          <div
            v-for="(item, index) in taskItems"
            :key="index"
            class="task-item"
            :class="[item.status, { expanded: expandedIndex === index }]"
            @click="item.status === 'success' || item.status === 'failed' ? toggleExpand(index) : null"
            :style="(item.status === 'success' || item.status === 'failed') ? 'cursor:pointer' : ''"
          >
            <!-- 主行 -->
            <div class="item-main">
              <div class="item-left">
                <span class="item-index">{{ index + 1 }}</span>
                <div class="item-info">
                  <div class="item-keyword">{{ item.keyword }}</div>
                  <div v-if="item.title && expandedIndex !== index" class="item-title">→ {{ item.title }}</div>
                  <div v-if="item.error && expandedIndex !== index" class="item-error">{{ item.error }}</div>
                </div>
              </div>
              <div class="item-right">
                <div class="item-status-badge" :class="item.status">
                  <span v-if="item.status === 'pending'">等待中</span>
                  <span v-else-if="item.status === 'running'">
                    <svg class="spin" width="12" height="12" viewBox="0 0 24 24" fill="none">
                      <path d="M21 12a9 9 0 11-6.219-8.56" stroke="currentColor" stroke-width="2.5" stroke-linecap="round"/>
                    </svg>
                    抓取中
                  </span>
                  <span v-else-if="item.status === 'success'">✓ 成功</span>
                  <span v-else-if="item.status === 'failed'">✕ 失败</span>
                </div>
                <svg
                  v-if="item.status === 'success' || item.status === 'failed'"
                  class="expand-arrow"
                  :class="{ rotated: expandedIndex === index }"
                  width="14" height="14" viewBox="0 0 24 24" fill="none"
                >
                  <path d="M6 9l6 6 6-6" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
                </svg>
              </div>
            </div>

            <!-- 展开详情 -->
            <transition name="expand">
              <div v-if="expandedIndex === index && (item.status === 'success' || item.status === 'failed')" class="item-detail">
                <div v-if="item.status === 'success'">
                  <div class="detail-row">
                    <span class="detail-label">词条标题</span>
                    <span class="detail-value">{{ item.title || '—' }}</span>
                  </div>
                  <div class="detail-row">
                    <span class="detail-label">摘要</span>
                    <span class="detail-value summary-text">{{ item.summary || '暂无摘要' }}</span>
                  </div>
                  <div class="detail-row">
                    <span class="detail-label">链接</span>
                    <a v-if="item.url" :href="item.url" target="_blank" class="detail-link" @click.stop>
                      查看原文 →
                    </a>
                    <span v-else class="detail-value">—</span>
                  </div>
                </div>
                <div v-else class="detail-error">
                  <svg width="14" height="14" viewBox="0 0 24 24" fill="none">
                    <circle cx="12" cy="12" r="10" stroke="currentColor" stroke-width="2"/>
                    <line x1="12" y1="8" x2="12" y2="12" stroke="currentColor" stroke-width="2" stroke-linecap="round"/>
                    <line x1="12" y1="16" x2="12.01" y2="16" stroke="currentColor" stroke-width="2" stroke-linecap="round"/>
                  </svg>
                  {{ item.error || '未知错误' }}
                </div>
              </div>
            </transition>

          </div>
        </div>
      </div>

    </div>

  </div>
</template>

<script setup>
import { ref, computed, onMounted, onUnmounted } from 'vue'
import { createBatchTask } from '../api/search'
import { getTask, getTaskItems } from '../api/task'

// ── 输入状态 ──────────────────────────────────────────────
const keywords   = ref([])
const pasteText  = ref('')
const isDragging = ref(false)
const fileInput  = ref(null)

// ── 执行状态 ──────────────────────────────────────────────
const running       = ref(false)
const finished      = ref(false)
const taskItems     = ref([])
const expandedIndex = ref(null)
const showResume    = ref(false)   // 是否显示"恢复任务"提示

const toggleExpand = (index) => {
  expandedIndex.value = expandedIndex.value === index ? null : index
}

// ── 统计 ──────────────────────────────────────────────────
const totalCount   = computed(() => taskItems.value.length)
const successCount = computed(() => taskItems.value.filter(i => i.status === 'success').length)
const failCount    = computed(() => taskItems.value.filter(i => i.status === 'failed').length)
const pendingCount = computed(() => taskItems.value.filter(i => i.status === 'pending').length)
const progressPct  = computed(() => {
  if (!totalCount.value) return 0
  return Math.round((successCount.value + failCount.value) / totalCount.value * 100)
})

const estimatedTime = computed(() => {
  const secs = keywords.value.length * 8
  if (secs < 60) return `约 ${secs} 秒`
  return `约 ${Math.ceil(secs / 60)} 分钟`
})

// ── 关键词解析 ────────────────────────────────────────────
const parseLines = (text) => {
  return text.split('\n')
    .map(l => l.trim())
    .filter(l => l.length > 0)
}

const parsePasteText = () => {
  keywords.value = parseLines(pasteText.value)
}

const removeKeyword = (index) => {
  keywords.value.splice(index, 1)
  pasteText.value = keywords.value.join('\n')
}

const clearAll = () => {
  keywords.value = []
  pasteText.value = ''
}

// ── 文件上传 ──────────────────────────────────────────────
const readFile = (file) => {
  const reader = new FileReader()
  reader.onload = (e) => {
    const lines = parseLines(e.target.result)
    keywords.value = [...new Set([...keywords.value, ...lines])]  // 去重合并
    pasteText.value = keywords.value.join('\n')
  }
  reader.readAsText(file, 'utf-8')
}

const handleFileChange = (e) => {
  const file = e.target.files[0]
  if (file) readFile(file)
}

const handleDrop = (e) => {
  isDragging.value = false
  const file = e.dataTransfer.files[0]
  if (file) readFile(file)
}

// ── 批量执行 ──────────────────────────────────────────────
let pollTimer   = null
const currentTaskId = ref(null)

const startBatch = async () => {
  if (!keywords.value.length) return

  running.value  = true
  finished.value = false

  try {
    // 1. 一次性提交所有关键词，后端创建任务并后台执行
    const res = await createBatchTask(keywords.value)
    currentTaskId.value = res.data.task_id
    localStorage.setItem('batch_task_id', res.data.task_id)

    // 2. 用后端返回的关键词列表初始化前端状态（全部 pending）
    taskItems.value = keywords.value.map(kw => ({
      keyword: kw,
      status:  'pending',
      title:   '',
      summary: '',
      url:     '',
      error:   ''
    }))

    // 3. 开始轮询任务进度
    startPolling(currentTaskId.value)

  } catch (e) {
    console.error('创建批量任务失败', e)
    running.value = false
  }
}

const startPolling = (taskId) => {
  // 每 2 秒拉一次任务状态
  pollTimer = setInterval(async () => {
    try {
      const [taskRes, itemsRes] = await Promise.all([
        getTask(taskId),
        getTaskItems(taskId)
      ])

      const task  = taskRes.data
      const items = itemsRes.data

      // 用 keyword 匹配，避免下标错位
      items.forEach(item => {
        const local = taskItems.value.find(t => t.keyword === item.keyword)
        if (!local) return
        local.status  = item.status
        local.title   = item.title    || ''
        local.summary = item.summary  || ''
        local.url     = item.url      || ''
        local.error   = item.error_msg || ''
      })

      // 当前正在抓取的词条标记为 running
      if (task.status === 'running' && task.current_keyword) {
        const cur = taskItems.value.find(t => t.keyword === task.current_keyword)
        if (cur && cur.status === 'pending') cur.status = 'running'
      }

      // 任务完成，停止轮询
      if (task.status === 'completed') {
        clearInterval(pollTimer)
        running.value  = false
        finished.value = true
        localStorage.removeItem('batch_task_id')
      }

    } catch (e) {
      console.error('轮询失败', e)
    }
  }, 2000)
}

const reset = () => {
  clearInterval(pollTimer)
  running.value       = false
  finished.value      = false
  taskItems.value     = []
  expandedIndex.value = null
  currentTaskId.value = null
  showResume.value    = false
  keywords.value      = []
  pasteText.value     = ''
  localStorage.removeItem('batch_task_id')
}

// ── 恢复未完成任务 ────────────────────────────────────────
const resumeTask = async () => {
  const savedId = parseInt(localStorage.getItem('batch_task_id'))
  if (!savedId) return

  try {
    const [taskRes, itemsRes] = await Promise.all([
      getTask(savedId),
      getTaskItems(savedId)
    ])
    const task  = taskRes.data
    const items = itemsRes.data
    console.log('[resumeTask] task:', task)
    console.log('[resumeTask] items count:', items.length)

    if (task.status === 'completed') {
      // 任务已完成，直接显示结果
      taskItems.value     = items.map(i => ({
        keyword: i.keyword,
        status:  i.status,
        title:   i.title    || '',
        summary: i.summary  || '',
        url:     i.url      || '',
        error:   i.error_msg || ''
      }))
      currentTaskId.value = savedId
      finished.value      = true
      running.value       = false
      showResume.value    = false
      localStorage.removeItem('batch_task_id')
    } else if (task.status === 'running' || task.status === 'pending') {
      // 任务还在跑，恢复轮询
      taskItems.value = items.map(i => ({
        keyword: i.keyword,
        status:  i.status,
        title:   i.title    || '',
        summary: i.summary  || '',
        url:     i.url      || '',
        error:   i.error_msg || ''
      }))
      currentTaskId.value = savedId
      running.value       = true
      finished.value      = false
      showResume.value    = false
      startPolling(savedId)
    }
  } catch (e) {
    console.error('恢复任务失败', e)
    localStorage.removeItem('batch_task_id')
  }
}

const discardResume = () => {
  showResume.value = false
  localStorage.removeItem('batch_task_id')
}

onMounted(async () => {
  const savedId = localStorage.getItem('batch_task_id')
  if (savedId) {
    // 有未完成的任务，提示用户选择
    showResume.value = true
  }
})

onUnmounted(() => { clearInterval(pollTimer) })
</script>

<style scoped>
@import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@300;400;500;600&display=swap');

.batch-page {
  padding: 32px 36px;
  max-width: 1000px;
  width: 100%;
  box-sizing: border-box;
  font-family: 'DM Sans', sans-serif;
}

/* ── 页头 ── */
.page-header { margin-bottom: 28px; }

.header-tag {
  display: inline-flex;
  align-items: center;
  font-size: 11px;
  font-weight: 600;
  text-transform: uppercase;
  letter-spacing: 1px;
  color: #6366f1;
  background: #eef2ff;
  padding: 4px 10px;
  border-radius: 6px;
  margin-bottom: 12px;
}

.page-header h2 {
  font-size: 26px;
  font-weight: 700;
  color: #0f1117;
  margin: 0 0 6px;
  letter-spacing: -0.5px;
}

.page-header p {
  color: #6b7280;
  font-size: 14px;
  margin: 0;
}

/* ── 卡片基础 ── */
.card {
  background: #fff;
  border-radius: 16px;
  border: 1px solid #e8eaed;
  box-shadow: 0 1px 4px rgba(0,0,0,0.04);
  padding: 22px;
  margin-bottom: 16px;
}

.card-label {
  font-size: 12px;
  font-weight: 700;
  text-transform: uppercase;
  letter-spacing: 0.8px;
  color: #9ca3af;
  margin-bottom: 14px;
}

/* ── 输入阶段布局 ── */
.input-grid {
  display: grid;
  grid-template-columns: 1fr 320px;
  gap: 20px;
  align-items: start;
}

.left-col, .right-col {
  display: flex;
  flex-direction: column;
}

/* ── 拖拽区 ── */
.drop-zone {
  border: 2px dashed #e5e7eb;
  border-radius: 12px;
  padding: 40px 20px;
  text-align: center;
  cursor: pointer;
  transition: all 0.2s;
  background: #fafafa;
}

.drop-zone:hover, .drop-zone.dragging {
  border-color: #6366f1;
  background: #f5f3ff;
}

.drop-icon {
  color: #9ca3af;
  margin-bottom: 12px;
  display: flex;
  justify-content: center;
}

.drop-zone.dragging .drop-icon { color: #6366f1; }

.drop-text {
  font-size: 14px;
  font-weight: 500;
  color: #374151;
  margin-bottom: 6px;
}

.drop-hint {
  font-size: 12px;
  color: #9ca3af;
}

/* ── 粘贴区 ── */
.paste-area {
  width: 100%;
  height: 160px;
  border: 1.5px solid #e5e7eb;
  border-radius: 10px;
  padding: 14px;
  font-size: 13px;
  font-family: 'DM Sans', sans-serif;
  color: #111827;
  resize: none;
  outline: none;
  background: #fafafa;
  box-sizing: border-box;
  line-height: 1.7;
  transition: border-color 0.2s;
}

.paste-area:focus {
  border-color: #6366f1;
  background: #fff;
  box-shadow: 0 0 0 3px rgba(99,102,241,0.1);
}

/* ── 统计卡片 ── */
.stats-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 12px;
  margin-bottom: 12px;
}

.stat-item {
  background: #f9fafb;
  border-radius: 10px;
  padding: 14px;
  text-align: center;
}

.stat-value {
  font-size: 28px;
  font-weight: 700;
  color: #0f1117;
  letter-spacing: -1px;
  line-height: 1;
  margin-bottom: 6px;
}

.stat-label {
  font-size: 11px;
  color: #9ca3af;
  font-weight: 500;
}

.stats-tip {
  display: flex;
  align-items: center;
  gap: 6px;
  font-size: 12px;
  color: #9ca3af;
  padding-top: 4px;
}

/* ── 预览列表 ── */
.preview-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 14px;
}

.preview-header .card-label { margin-bottom: 0; }

.clear-all-btn {
  font-size: 12px;
  color: #ef4444;
  background: none;
  border: none;
  cursor: pointer;
  font-family: 'DM Sans', sans-serif;
  font-weight: 500;
}

.clear-all-btn:hover { text-decoration: underline; }

.preview-empty {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 10px;
  padding: 24px 0;
  color: #9ca3af;
  font-size: 13px;
  text-align: center;
  line-height: 1.6;
}

.keyword-list {
  display: flex;
  flex-direction: column;
  gap: 6px;
  max-height: 240px;
  overflow-y: auto;
}

.keyword-item {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 8px 10px;
  border-radius: 8px;
  background: #f9fafb;
  transition: background 0.15s;
}

.keyword-item:hover { background: #f0f0f5; }

.kw-index {
  font-size: 11px;
  color: #9ca3af;
  min-width: 20px;
  text-align: right;
  font-variant-numeric: tabular-nums;
}

.kw-text {
  flex: 1;
  font-size: 13px;
  color: #111827;
  font-weight: 500;
}

.kw-delete {
  background: none;
  border: none;
  cursor: pointer;
  color: #d1d5db;
  display: flex;
  align-items: center;
  padding: 3px;
  border-radius: 4px;
  transition: color 0.15s;
}

.kw-delete:hover { color: #ef4444; }

/* ── 启动按钮 ── */
.start-btn {
  width: 100%;
  height: 48px;
  border: none;
  border-radius: 10px;
  background: linear-gradient(135deg, #6366f1, #8b5cf6);
  color: white;
  font-size: 15px;
  font-weight: 600;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
  font-family: 'DM Sans', sans-serif;
  transition: all 0.2s;
  margin-top: 4px;
}

.start-btn:hover:not(:disabled) {
  transform: translateY(-1px);
  box-shadow: 0 6px 20px rgba(99,102,241,0.35);
}

.start-btn:disabled {
  opacity: 0.4;
  cursor: not-allowed;
  transform: none;
}

/* ── 进度阶段 ── */
.progress-header-card { margin-bottom: 16px; }

.progress-meta {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 16px;
}

.progress-title {
  display: flex;
  align-items: center;
  gap: 10px;
}

.running-badge {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  font-size: 12px;
  font-weight: 600;
  color: #6366f1;
  background: #eef2ff;
  padding: 4px 10px;
  border-radius: 20px;
}

.running-dot {
  width: 7px;
  height: 7px;
  background: #6366f1;
  border-radius: 50%;
  animation: pulse 1s infinite;
}

@keyframes pulse {
  0%, 100% { opacity: 1; transform: scale(1); }
  50% { opacity: 0.5; transform: scale(0.8); }
}

.done-badge {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  font-size: 12px;
  font-weight: 600;
  color: #059669;
  background: #d1fae5;
  padding: 4px 10px;
  border-radius: 20px;
}

.progress-keyword-hint {
  font-size: 13px;
  color: #6b7280;
}

.progress-counts {
  display: flex;
  gap: 14px;
}

.count {
  font-size: 13px;
  font-weight: 600;
}

.count.success { color: #059669; }
.count.fail    { color: #dc2626; }
.count.pending { color: #9ca3af; }

.progress-bar-wrap {
  height: 8px;
  background: #f3f4f6;
  border-radius: 99px;
  overflow: hidden;
  margin-bottom: 6px;
}

.progress-bar {
  height: 100%;
  background: linear-gradient(90deg, #6366f1, #8b5cf6);
  border-radius: 99px;
  transition: width 0.4s ease;
}

.progress-pct {
  font-size: 12px;
  color: #9ca3af;
  text-align: right;
  margin-bottom: 16px;
}

.restart-btn {
  background: #f9fafb;
  border: 1.5px solid #e5e7eb;
  border-radius: 8px;
  padding: 8px 20px;
  font-size: 13px;
  font-weight: 600;
  color: #374151;
  cursor: pointer;
  font-family: 'DM Sans', sans-serif;
  transition: all 0.15s;
}

.restart-btn:hover {
  border-color: #6366f1;
  color: #6366f1;
}

/* ── 词条状态列表 ── */
.items-list {
  display: flex;
  flex-direction: column;
  gap: 8px;
  max-height: 480px;
  overflow-y: auto;
}

.task-item {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 12px 14px;
  border-radius: 10px;
  border: 1px solid #f0f0f5;
  background: #fafafa;
  transition: all 0.2s;
}

.task-item.running {
  background: #f5f3ff;
  border-color: #c4b5fd;
}

.task-item.success {
  background: #f0fdf4;
  border-color: #bbf7d0;
}

.task-item.failed {
  background: #fff5f5;
  border-color: #fecaca;
}

.item-left {
  display: flex;
  align-items: center;
  gap: 12px;
  flex: 1;
  min-width: 0;
}

.item-index {
  font-size: 11px;
  color: #9ca3af;
  min-width: 22px;
  text-align: right;
  font-variant-numeric: tabular-nums;
  flex-shrink: 0;
}

.item-info { flex: 1; min-width: 0; }

.item-keyword {
  font-size: 14px;
  font-weight: 600;
  color: #111827;
}

.item-title {
  font-size: 12px;
  color: #6b7280;
  margin-top: 2px;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.item-error {
  font-size: 12px;
  color: #dc2626;
  margin-top: 2px;
}

.item-status-badge {
  font-size: 12px;
  font-weight: 600;
  padding: 4px 10px;
  border-radius: 6px;
  white-space: nowrap;
  display: flex;
  align-items: center;
  gap: 5px;
  flex-shrink: 0;
}

.item-status-badge.pending { background: #f3f4f6; color: #9ca3af; }
.item-status-badge.running { background: #ede9fe; color: #6366f1; }
.item-status-badge.success { background: #d1fae5; color: #059669; }
.item-status-badge.failed  { background: #fee2e2; color: #dc2626; }

.spin {
  animation: spin 0.8s linear infinite;
}

@keyframes spin {
  to { transform: rotate(360deg); }
}

/* ── 词条展开 ── */
.item-main {
  display: flex;
  align-items: center;
  justify-content: space-between;
  width: 100%;
}

.item-right {
  display: flex;
  align-items: center;
  gap: 8px;
  flex-shrink: 0;
}

.expand-arrow {
  color: #9ca3af;
  transition: transform 0.2s;
  flex-shrink: 0;
}

.expand-arrow.rotated {
  transform: rotate(180deg);
}

.task-item.expanded {
  background: #fff !important;
  border-color: #c4b5fd !important;
  box-shadow: 0 2px 12px rgba(99,102,241,0.08);
}

.item-detail {
  margin-top: 14px;
  padding-top: 14px;
  border-top: 1px solid #f0f0f5;
  width: 100%;
}

.detail-row {
  display: flex;
  gap: 12px;
  margin-bottom: 10px;
  align-items: flex-start;
}

.detail-label {
  font-size: 11px;
  font-weight: 700;
  text-transform: uppercase;
  letter-spacing: 0.6px;
  color: #9ca3af;
  min-width: 60px;
  padding-top: 1px;
  flex-shrink: 0;
}

.detail-value {
  font-size: 13px;
  color: #374151;
  line-height: 1.6;
}

.summary-text {
  color: #6b7280;
  line-height: 1.7;
}

.detail-link {
  font-size: 13px;
  font-weight: 600;
  color: #6366f1;
  text-decoration: none;
}

.detail-link:hover {
  text-decoration: underline;
}

.detail-error {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 13px;
  color: #dc2626;
}

/* 展开动画 */
.expand-enter-active,
.expand-leave-active {
  transition: all 0.25s ease;
  overflow: hidden;
}

.expand-enter-from,
.expand-leave-to {
  opacity: 0;
  max-height: 0;
  margin-top: 0;
  padding-top: 0;
}

.expand-enter-to,
.expand-leave-from {
  opacity: 1;
  max-height: 300px;
}


/* ── 恢复任务横幅 ── */
.resume-banner {
  display: flex;
  align-items: center;
  justify-content: space-between;
  background: #fffbeb;
  border: 1px solid #fde68a;
  border-radius: 14px;
  padding: 16px 20px;
  margin-bottom: 20px;
  gap: 16px;
}

.resume-left {
  display: flex;
  align-items: center;
  gap: 14px;
}

.resume-icon {
  width: 40px;
  height: 40px;
  border-radius: 10px;
  background: #fef3c7;
  color: #d97706;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}

.resume-title {
  font-size: 14px;
  font-weight: 700;
  color: #92400e;
  margin-bottom: 3px;
}

.resume-desc {
  font-size: 12px;
  color: #b45309;
}

.resume-actions {
  display: flex;
  gap: 8px;
  flex-shrink: 0;
}

.resume-btn {
  font-size: 13px;
  font-weight: 600;
  padding: 8px 18px;
  border-radius: 8px;
  border: none;
  cursor: pointer;
  font-family: 'DM Sans', sans-serif;
  transition: all 0.15s;
}

.resume-btn.secondary {
  background: #fff;
  color: #6b7280;
  border: 1px solid #e5e7eb;
}

.resume-btn.secondary:hover { background: #f9fafb; }

.resume-btn.primary {
  background: #f59e0b;
  color: #fff;
}

.resume-btn.primary:hover { background: #d97706; }

.slide-down-enter-active, .slide-down-leave-active {
  transition: all 0.25s ease;
}
.slide-down-enter-from, .slide-down-leave-to {
  opacity: 0;
  transform: translateY(-10px);
}

</style>