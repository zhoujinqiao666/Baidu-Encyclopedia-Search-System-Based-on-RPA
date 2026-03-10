<template>
  <div class="search-page">

    <!-- 页面标题 -->
    <div class="page-header">
      <div class="header-tag">单次检索</div>
      <h2>百度词条检索</h2>
      <p>输入关键词，RPA 机器人将自动提取百度百科词条数据</p>
    </div>

    <div class="content-grid">

      <!-- 主操作卡片 -->
      <div class="main-card card">

        <!-- 关键词输入 -->
        <div class="form-section">
          <label class="form-label">
            搜索关键词
            <span class="required">必填</span>
          </label>
          <div class="input-wrapper" :class="{ focused: inputFocused }">
            <span class="input-icon">
              <svg width="16" height="16" viewBox="0 0 24 24" fill="none">
                <circle cx="11" cy="11" r="8" stroke="currentColor" stroke-width="2"/>
                <path d="M21 21l-4.35-4.35" stroke="currentColor" stroke-width="2" stroke-linecap="round"/>
              </svg>
            </span>
            <input
              v-model="keyword"
              class="search-input"
              placeholder="例如：人工智能、量子计算、区块链..."
              @focus="inputFocused = true"
              @blur="inputFocused = false"
              @keydown.enter="handleSearch"
            />
            <button v-if="keyword" class="clear-btn" @click="keyword = ''">
              <svg width="14" height="14" viewBox="0 0 24 24" fill="none">
                <path d="M18 6L6 18M6 6l12 12" stroke="currentColor" stroke-width="2" stroke-linecap="round"/>
              </svg>
            </button>
          </div>
        </div>

        <!-- 检索策略 -->
        <div class="form-section">
          <label class="form-label">检索策略</label>
          <div class="strategy-grid">
            <div
              class="strategy-card"
              :class="{ active: strategy === 'strict' }"
              @click="strategy = 'strict'"
            >
              <div class="strategy-header">
                <div class="strategy-icon strict-icon">
                  <svg width="14" height="14" viewBox="0 0 24 24" fill="none">
                    <path d="M22 11.08V12a10 10 0 11-5.93-9.14" stroke="currentColor" stroke-width="2" stroke-linecap="round"/>
                    <path d="M22 4L12 14.01l-3-3" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
                  </svg>
                </div>
                <div class="strategy-check" v-if="strategy === 'strict'">
                  <svg width="10" height="10" viewBox="0 0 24 24" fill="none">
                    <path d="M20 6L9 17l-5-5" stroke="white" stroke-width="3" stroke-linecap="round" stroke-linejoin="round"/>
                  </svg>
                </div>
              </div>
              <div class="strategy-name">严格匹配</div>
              <div class="strategy-desc">仅提取完全匹配的词条</div>
            </div>

            <div
              class="strategy-card"
              :class="{ active: strategy === 'related' }"
              @click="strategy = 'related'"
            >
              <div class="strategy-header">
                <div class="strategy-icon related-icon">
                  <svg width="14" height="14" viewBox="0 0 24 24" fill="none">
                    <circle cx="18" cy="5" r="3" stroke="currentColor" stroke-width="2"/>
                    <circle cx="6" cy="12" r="3" stroke="currentColor" stroke-width="2"/>
                    <circle cx="18" cy="19" r="3" stroke="currentColor" stroke-width="2"/>
                    <path d="M8.59 13.51l6.83 3.98M15.41 6.51l-6.82 3.98" stroke="currentColor" stroke-width="2"/>
                  </svg>
                </div>
                <div class="strategy-check" v-if="strategy === 'related'">
                  <svg width="10" height="10" viewBox="0 0 24 24" fill="none">
                    <path d="M20 6L9 17l-5-5" stroke="white" stroke-width="3" stroke-linecap="round" stroke-linejoin="round"/>
                  </svg>
                </div>
              </div>
              <div class="strategy-name">包含相关词条</div>
              <div class="strategy-desc">提取相关和多义词条</div>
            </div>
          </div>
        </div>

        <!-- 显示浏览器开关 -->
        <div class="form-section">
          <div class="toggle-row">
            <div class="toggle-info">
              <div class="toggle-label">显示自动化过程</div>
              <div class="toggle-desc">开启后可实时查看 RPA 执行流程</div>
            </div>
            <div
              class="toggle-switch"
              :class="{ on: showBrowser }"
              @click="showBrowser = !showBrowser"
            >
              <div class="toggle-thumb"></div>
            </div>
          </div>
        </div>

        <!-- 执行按钮 -->
        <button
          class="exec-btn"
          :class="{ loading: loading }"
          :disabled="loading"
          @click="handleSearch"
        >
          <span v-if="!loading" class="btn-content">
            <svg width="16" height="16" viewBox="0 0 24 24" fill="none">
              <polygon points="5 3 19 12 5 21 5 3" fill="currentColor"/>
            </svg>
            立即执行检索
          </span>
          <span v-else class="btn-content">
            <svg class="spin" width="16" height="16" viewBox="0 0 24 24" fill="none">
              <path d="M21 12a9 9 0 11-6.219-8.56" stroke="currentColor" stroke-width="2.5" stroke-linecap="round"/>
            </svg>
            正在检索中...
          </span>
        </button>
      </div>

      <!-- 右侧状态面板 -->
      <div class="side-panel">
        <div class="card info-card">
          <div class="info-title">执行状态</div>
          <div class="status-list">
            <div class="status-item" :class="{ active: !!keyword }">
              <div class="status-dot"></div>
              <span>关键词已输入</span>
            </div>
            <div class="status-item active">
              <div class="status-dot"></div>
              <span>RPA 引擎就绪</span>
            </div>
            <div class="status-item" :class="{ active: backendOnline, error: !backendOnline }">
              <div class="status-dot" :class="{ 'dot-error': !backendOnline }"></div>
              <span>{{ backendOnline ? '后端服务在线' : '后端服务离线' }}</span>
            </div>
          </div>
        </div>

        <div class="card tips-card">
          <div class="info-title">使用提示</div>
          <ul class="tips-list">
            <li>支持中英文关键词</li>
            <li>严格模式速度更快</li>
            <li>可按 Enter 键快速搜索</li>
          </ul>
        </div>
      </div>
    </div>

    <!-- 检索提示 Toast -->
    <transition name="slide-up">
      <div v-if="toast.show" class="toast" :class="toast.type">
        <span class="toast-icon">{{ toast.type === 'success' ? '✓' : '✕' }}</span>
        {{ toast.message }}
      </div>
    </transition>

    <!-- 执行结果 -->
    <transition name="slide-up">
      <div v-if="result" class="result-section">

        <!-- 相关模式：多条结果 -->
        <template v-if="Array.isArray(result)">
          <div class="result-list-header">
            <div class="result-tag success">找到 {{ result.length }} 个相关词条</div>
          </div>
          <div class="result-list">
            <div
              v-for="(item, index) in result"
              :key="index"
              class="card result-card"
            >
              <div class="result-header">
                <div class="result-tag" :class="item.success ? 'success' : 'fail'">
                  {{ item.category || '词条' }}
                </div>
                <span class="result-index"># {{ index + 1 }}</span>
              </div>
              <h3 class="result-title">{{ item.title || item.keyword }}</h3>
              <p class="result-summary">{{ item.summary || item.error || '暂无摘要' }}</p>
              <a v-if="item.url" :href="item.url" target="_blank" class="result-link">
                查看百度百科原文
                <svg width="12" height="12" viewBox="0 0 24 24" fill="none">
                  <path d="M18 13v6a2 2 0 01-2 2H5a2 2 0 01-2-2V8a2 2 0 012-2h6" stroke="currentColor" stroke-width="2" stroke-linecap="round"/>
                  <polyline points="15 3 21 3 21 9" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
                  <line x1="10" y1="14" x2="21" y2="3" stroke="currentColor" stroke-width="2" stroke-linecap="round"/>
                </svg>
              </a>
            </div>
          </div>
        </template>

        <!-- 严格模式：单条结果 -->
        <div v-else class="card result-card" :class="{ 'result-card-fail': !result.success }">
          <div class="result-header">
            <div class="result-tag" :class="result.success ? 'success' : 'fail'">
              {{ result.success ? '检索成功' : '未找到词条' }}
            </div>
            <div v-if="result.from_fallback" class="fallback-tag">
              来自 {{ result.source }}
            </div>
            <span class="result-time">刚刚</span>
          </div>

          <!-- 失败状态 -->
          <div v-if="!result.success" class="not-found-body">
            <svg width="40" height="40" viewBox="0 0 24 24" fill="none">
              <circle cx="11" cy="11" r="8" stroke="#d1d5db" stroke-width="1.5"/>
              <path d="M21 21l-4.35-4.35" stroke="#d1d5db" stroke-width="1.5" stroke-linecap="round"/>
              <line x1="8" y1="11" x2="14" y2="11" stroke="#d1d5db" stroke-width="1.5" stroke-linecap="round"/>
            </svg>
            <p class="not-found-text">{{ result.error || '未检索到该词条' }}</p>
          </div>

          <!-- 成功状态 -->
          <template v-else>
            <div v-if="result.from_fallback" class="fallback-notice">
              <svg width="13" height="13" viewBox="0 0 24 24" fill="none">
                <circle cx="12" cy="12" r="10" stroke="currentColor" stroke-width="2"/>
                <line x1="12" y1="8" x2="12" y2="12" stroke="currentColor" stroke-width="2" stroke-linecap="round"/>
                <line x1="12" y1="16" x2="12.01" y2="16" stroke="currentColor" stroke-width="2" stroke-linecap="round"/>
              </svg>
              百度百科未收录该词条，以下结果来自{{ result.source }}
            </div>
            <h3 class="result-title">{{ result.title }}</h3>
            <p class="result-summary">{{ result.summary }}</p>
            <a v-if="result.url" :href="result.url" target="_blank" class="result-link">
              查看{{ result.from_fallback ? result.source : '百度百科' }}原文
              <svg width="12" height="12" viewBox="0 0 24 24" fill="none">
                <path d="M18 13v6a2 2 0 01-2 2H5a2 2 0 01-2-2V8a2 2 0 012-2h6" stroke="currentColor" stroke-width="2" stroke-linecap="round"/>
                <polyline points="15 3 21 3 21 9" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
                <line x1="10" y1="14" x2="21" y2="3" stroke="currentColor" stroke-width="2" stroke-linecap="round"/>
              </svg>
            </a>
            <div v-if="result.source === 'DeepSeek AI'" class="ai-notice">以上解释由 DeepSeek AI 生成，仅供参考</div>
          </template>
        </div>

      </div>
    </transition>

  </div>
</template>

<script setup>
import { ref, onMounted, onUnmounted } from 'vue'
import { searchSingle, ping } from '../api/search'

const keyword = ref('')
const loading = ref(false)
const result = ref(null)
const strategy = ref('strict')
const showBrowser = ref(false)
const inputFocused = ref(false)

// ── 后端在线检测 ──────────────────────────────────────────
const backendOnline = ref(false)
let pingTimer = null

const checkBackend = async () => {
  try {
    await ping()
    backendOnline.value = true
  } catch {
    backendOnline.value = false
  }
}

onMounted(() => {
  checkBackend()
  pingTimer = setInterval(checkBackend, 5000)  // 每5秒检测一次
})

onUnmounted(() => {
  clearInterval(pingTimer)
})

// ── Toast 提示 ────────────────────────────────────────────
const toast = ref({ show: false, type: 'success', message: '' })
let toastTimer = null

const showToast = (type, message) => {
  clearTimeout(toastTimer)
  toast.value = { show: true, type, message }
  toastTimer = setTimeout(() => { toast.value.show = false }, 3000)
}

// ── 搜索 ──────────────────────────────────────────────────
const handleSearch = async () => {
  if (!keyword.value.trim()) return
  if (!backendOnline.value) {
    showToast('error', '后端服务未启动，请先运行 python app.py')
    return
  }

  loading.value = true
  result.value = null

  try {
    const response = await searchSingle(keyword.value, strategy.value, showBrowser.value)
    if (strategy.value === 'related' && response.data.results) {
      result.value = response.data.results
      showToast('success', `找到 ${result.value.length} 个相关词条`)
    } else {
      result.value = response.data
      if (result.value.success) {
        showToast('success', `检索成功：${result.value.title}`)
      } else {
        showToast('error', result.value.error || '未检索到该词条')
      }
    }
  } catch (error) {
    console.error(error)
    showToast('error', '请求失败，请检查后端是否正常运行')
    result.value = { success: false, error: '请求异常，请检查后端服务' }
  } finally {
    loading.value = false
  }
}
</script>

<style scoped>
@import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@300;400;500;600&display=swap');

.search-page {
  padding: 32px 36px;
  max-width: 960px;
  width: 100%;
  box-sizing: border-box;
  font-family: 'DM Sans', sans-serif;
}

/* ── 页头 ── */
.page-header {
  margin-bottom: 28px;
}

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
  background: #ffffff;
  border-radius: 16px;
  border: 1px solid #e8eaed;
  box-shadow: 0 1px 4px rgba(0,0,0,0.04);
}

/* ── 布局 ── */
.content-grid {
  display: grid;
  grid-template-columns: 1fr 220px;
  gap: 20px;
  align-items: start;
}

.main-card {
  padding: 28px;
}

/* ── 表单 ── */
.form-section {
  margin-bottom: 26px;
}

.form-section:last-child {
  margin-bottom: 0;
}

.form-label {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 13px;
  font-weight: 600;
  color: #374151;
  margin-bottom: 10px;
}

.required {
  font-size: 10px;
  font-weight: 600;
  color: #ef4444;
  background: #fee2e2;
  padding: 2px 6px;
  border-radius: 4px;
  letter-spacing: 0.3px;
}

/* ── 输入框 ── */
.input-wrapper {
  display: flex;
  align-items: center;
  border: 1.5px solid #e5e7eb;
  border-radius: 10px;
  padding: 0 14px;
  gap: 10px;
  transition: all 0.2s;
  background: #fafafa;
}

.input-wrapper.focused {
  border-color: #6366f1;
  background: #fff;
  box-shadow: 0 0 0 3px rgba(99,102,241,0.1);
}

.input-icon {
  color: #9ca3af;
  display: flex;
  align-items: center;
  flex-shrink: 0;
}

.search-input {
  flex: 1;
  border: none;
  outline: none;
  background: transparent;
  font-size: 14px;
  color: #111827;
  height: 46px;
  font-family: 'DM Sans', sans-serif;
}

.search-input::placeholder {
  color: #bfbfbf;
}

.clear-btn {
  background: none;
  border: none;
  cursor: pointer;
  color: #9ca3af;
  display: flex;
  align-items: center;
  padding: 4px;
  border-radius: 4px;
  transition: color 0.15s;
}

.clear-btn:hover {
  color: #6b7280;
}

/* ── 策略卡片 ── */
.strategy-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 12px;
}

.strategy-card {
  border: 1.5px solid #e5e7eb;
  border-radius: 12px;
  padding: 16px;
  cursor: pointer;
  transition: all 0.18s;
  background: #fafafa;
  position: relative;
}

.strategy-card:hover {
  border-color: #a5b4fc;
  background: #fafbff;
}

.strategy-card.active {
  border-color: #6366f1;
  background: #f5f3ff;
}

.strategy-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 10px;
}

.strategy-icon {
  width: 30px;
  height: 30px;
  border-radius: 8px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.strict-icon {
  background: #dbeafe;
  color: #2563eb;
}

.related-icon {
  background: #fce7f3;
  color: #db2777;
}

.strategy-check {
  width: 18px;
  height: 18px;
  background: #6366f1;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
}

.strategy-name {
  font-size: 13px;
  font-weight: 600;
  color: #111827;
  margin-bottom: 4px;
}

.strategy-desc {
  font-size: 12px;
  color: #6b7280;
}

/* ── 开关 ── */
.toggle-row {
  display: flex;
  justify-content: space-between;
  align-items: center;
  background: #f9fafb;
  border: 1px solid #f0f0f5;
  border-radius: 12px;
  padding: 14px 18px;
}

.toggle-label {
  font-size: 13px;
  font-weight: 600;
  color: #374151;
  margin-bottom: 3px;
}

.toggle-desc {
  font-size: 12px;
  color: #9ca3af;
}

.toggle-switch {
  width: 42px;
  height: 24px;
  border-radius: 12px;
  background: #d1d5db;
  cursor: pointer;
  transition: background 0.2s;
  position: relative;
  flex-shrink: 0;
}

.toggle-switch.on {
  background: #6366f1;
}

.toggle-thumb {
  position: absolute;
  top: 3px;
  left: 3px;
  width: 18px;
  height: 18px;
  border-radius: 50%;
  background: white;
  box-shadow: 0 1px 3px rgba(0,0,0,0.2);
  transition: transform 0.2s;
}

.toggle-switch.on .toggle-thumb {
  transform: translateX(18px);
}

/* ── 执行按钮 ── */
.exec-btn {
  width: 100%;
  height: 48px;
  border: none;
  border-radius: 10px;
  background: linear-gradient(135deg, #6366f1, #8b5cf6);
  color: white;
  font-size: 15px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.2s;
  margin-top: 6px;
  font-family: 'DM Sans', sans-serif;
}

.exec-btn:hover:not(:disabled) {
  transform: translateY(-1px);
  box-shadow: 0 6px 20px rgba(99,102,241,0.35);
}

.exec-btn:active:not(:disabled) {
  transform: translateY(0);
}

.exec-btn:disabled {
  opacity: 0.75;
  cursor: not-allowed;
}

.btn-content {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
}

.spin {
  animation: spin 0.8s linear infinite;
}

@keyframes spin {
  to { transform: rotate(360deg); }
}

/* ── 侧边面板 ── */
.side-panel {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.info-card,
.tips-card {
  padding: 20px;
}

.info-title {
  font-size: 12px;
  font-weight: 700;
  text-transform: uppercase;
  letter-spacing: 0.8px;
  color: #9ca3af;
  margin-bottom: 14px;
}

.status-list {
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.status-item {
  display: flex;
  align-items: center;
  gap: 9px;
  font-size: 13px;
  color: #9ca3af;
}

.status-item.active {
  color: #374151;
}

.status-dot {
  width: 7px;
  height: 7px;
  border-radius: 50%;
  background: #d1d5db;
  flex-shrink: 0;
}

.status-item.active .status-dot {
  background: #34d399;
  box-shadow: 0 0 5px rgba(52,211,153,0.5);
}

.tips-list {
  margin: 0;
  padding-left: 16px;
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.tips-list li {
  font-size: 13px;
  color: #6b7280;
  line-height: 1.4;
}

/* ── 结果卡片 ── */
.result-section {
  margin-top: 20px;
}

.result-card {
  padding: 24px 28px;
}

.result-header {
  display: flex;
  align-items: center;
  gap: 10px;
  margin-bottom: 14px;
}

.result-tag {
  font-size: 11px;
  font-weight: 600;
  padding: 3px 10px;
  border-radius: 6px;
}

.result-tag.success {
  background: #d1fae5;
  color: #059669;
}

.result-time {
  font-size: 12px;
  color: #9ca3af;
}

.result-title {
  font-size: 20px;
  font-weight: 700;
  color: #0f1117;
  margin: 0 0 10px;
  letter-spacing: -0.3px;
}

.result-summary {
  font-size: 14px;
  color: #6b7280;
  line-height: 1.7;
  margin: 0 0 18px;
}

.result-link {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  font-size: 13px;
  font-weight: 600;
  color: #6366f1;
  text-decoration: none;
  transition: gap 0.15s;
}

.result-link:hover {
  gap: 8px;
}

/* ── 动画 ── */
.slide-up-enter-active {
  transition: all 0.3s ease;
}

.slide-up-enter-from {
  opacity: 0;
  transform: translateY(12px);
}

.result-list-header {
  margin-bottom: 12px;
}

.result-list {
  display: flex;
  flex-direction: column;
  gap: 14px;
}

.result-index {
  font-size: 12px;
  color: #9ca3af;
  font-variant-numeric: tabular-nums;
}

.result-tag.fail {
  background: #fee2e2;
  color: #dc2626;
}


/* ── 后端离线状态 ── */
.status-item.error span {
  color: #ef4444;
}

.dot-error {
  background: #ef4444 !important;
  box-shadow: 0 0 5px rgba(239,68,68,0.5) !important;
}

/* ── Toast 提示 ── */
.toast {
  position: fixed;
  top: 24px;
  left: 50%;
  transform: translateX(-50%);
  z-index: 9999;
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 14px 24px;
  border-radius: 12px;
  font-size: 14px;
  font-weight: 500;
  box-shadow: 0 4px 20px rgba(0,0,0,0.12);
  white-space: nowrap;
  animation: slide-in 0.25s ease;
}

.toast.success {
  background: #d1fae5;
  color: #065f46;
  border: 1px solid #a7f3d0;
}

.toast.error {
  background: #fee2e2;
  color: #991b1b;
  border: 1px solid #fca5a5;
}

.toast-icon {
  font-size: 16px;
  font-weight: 700;
}

@keyframes slide-in {
  from { opacity: 0; transform: translateY(-8px); }
  to   { opacity: 1; transform: translateY(0); }
}


/* ── 备用来源提示 ── */
.fallback-tag {
  font-size: 11px;
  font-weight: 600;
  padding: 3px 8px;
  border-radius: 6px;
  background: #fef3c7;
  color: #d97706;
}

.fallback-notice {
  display: flex;
  align-items: center;
  gap: 7px;
  font-size: 13px;
  color: #d97706;
  background: #fffbeb;
  border: 1px solid #fde68a;
  border-radius: 8px;
  padding: 10px 14px;
  margin-bottom: 14px;
}


.result-card-fail {
  border-color: #fecaca !important;
  background: #fff5f5;
}

.not-found-body {
  display: flex;
  flex-direction: column;
  align-items: center;
  padding: 24px 0 12px;
  gap: 12px;
}

.not-found-text {
  font-size: 14px;
  color: #9ca3af;
  text-align: center;
  margin: 0;
}


.ai-notice {
  font-size: 12px;
  color: #9ca3af;
  margin-top: 12px;
  padding-top: 12px;
  border-top: 1px dashed #e5e7eb;
}

</style>